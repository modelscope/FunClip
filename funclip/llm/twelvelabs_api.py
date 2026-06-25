import os
import time
import logging


# Default instruction asking Pegasus to return segments in the same
# "N. [start-end] text" format that FunClip's extract_timestamps() parses,
# so the existing AI_clip pipeline works unchanged.
PEGASUS_SYSTEM_PROMPT = (
    "You are a video clipping assistant. Watch the video and select up to four "
    "of the most engaging, self-contained highlight segments based on what "
    "actually happens on screen and what is said. Merge consecutive moments "
    "into a single segment. Reply strictly in this format, one segment per line:\n"
    "1. [start_time-end_time] description\n"
    "where start_time and end_time are seconds from the start of the video "
    "(e.g. 12.5), the connector is '-', and description is a short summary."
)


def _resolve_video_context(client, video):
    """Return a VideoContext for a public URL or a local file path.

    Local files are uploaded as a TwelveLabs asset first; remote URLs are
    passed through directly.
    """
    from twelvelabs.types.video_context import VideoContext_Url, VideoContext_AssetId

    if video.startswith("http://") or video.startswith("https://"):
        return VideoContext_Url(url=video)

    if not os.path.isfile(video):
        raise FileNotFoundError("Video source not found: {}".format(video))

    with open(video, "rb") as f:
        asset = client.assets.create(method="direct", file=f)
    # Wait for the uploaded asset to finish processing before analysis.
    deadline = time.time() + 300
    while asset.status == "processing" and time.time() < deadline:
        time.sleep(5)
        asset = client.assets.retrieve(asset_id=asset.id)
    if asset.status != "ready":
        raise RuntimeError(
            "TwelveLabs asset {} not ready (status={}).".format(asset.id, asset.status)
        )
    return VideoContext_AssetId(asset_id=asset.id)


def call_twelvelabs_pegasus(apikey,
                            video,
                            model="pegasus1.5",
                            prompt=None,
                            max_tokens=2048):
    """Run TwelveLabs Pegasus content-aware analysis over a video.

    Unlike the ASR-text based LLM backends, Pegasus reasons over the actual
    video (visuals + audio), which lets it pick highlight segments even when
    the transcript alone is ambiguous. Returns Pegasus' text response, which
    is expected to follow the "N. [start-end] text" segment format.

    Args:
        apikey: TwelveLabs API key (https://twelvelabs.io, free tier available).
        video: a public video URL or a local video file path.
        model: Pegasus model name, e.g. "pegasus1.5".
        prompt: optional extra instruction appended to the default prompt.
        max_tokens: max tokens for the Pegasus response.
    """
    from twelvelabs import TwelveLabs

    client = TwelveLabs(api_key=apikey or os.environ.get("TWELVELABS_API_KEY"))
    video_context = _resolve_video_context(client, video)

    full_prompt = PEGASUS_SYSTEM_PROMPT
    if prompt is not None and len(prompt.strip()):
        full_prompt = full_prompt + "\n\n" + prompt.strip()

    response = client.analyze(
        model_name=model,
        video=video_context,
        prompt=full_prompt,
        max_tokens=max_tokens,
    )
    logging.info("TwelveLabs Pegasus inference done.")
    return response.data


if __name__ == '__main__':
    res = call_twelvelabs_pegasus(
        os.environ.get("TWELVELABS_API_KEY"),
        "https://test-videos.co.uk/vids/bigbuckbunny/mp4/h264/360/Big_Buck_Bunny_360_10s_1MB.mp4",
    )
    print(res)
