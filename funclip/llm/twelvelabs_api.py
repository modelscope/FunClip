import os
import time
import logging
import re
from decimal import Decimal, ROUND_HALF_UP


_PEGASUS_SECONDS_RANGE_RE = re.compile(r"\[(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)\]")


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


def _seconds_to_milliseconds(seconds):
    return int(
        (Decimal(seconds) * 1000).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    )


def _format_srt_timestamp(milliseconds):
    hours, remainder = divmod(milliseconds, 60 * 60 * 1000)
    minutes, remainder = divmod(remainder, 60 * 1000)
    seconds, milliseconds = divmod(remainder, 1000)
    return "{:02d}:{:02d}:{:02d},{:03d}".format(
        hours, minutes, seconds, milliseconds
    )


def _normalize_pegasus_timestamps(text):
    """Convert Pegasus decimal-second ranges to FunClip's SRT range format."""
    if not isinstance(text, str):
        return text

    def replace_range(match):
        start_millis = _seconds_to_milliseconds(match.group(1))
        end_millis = _seconds_to_milliseconds(match.group(2))
        if end_millis <= start_millis or end_millis >= 100 * 60 * 60 * 1000:
            logging.warning(
                "Ignoring invalid Pegasus timestamp range: %s", match.group(0)
            )
            return match.group(0)
        return "[{}-{}]".format(
            _format_srt_timestamp(start_millis),
            _format_srt_timestamp(end_millis),
        )

    return _PEGASUS_SECONDS_RANGE_RE.sub(replace_range, text)


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
    return _normalize_pegasus_timestamps(response.data)


if __name__ == '__main__':
    res = call_twelvelabs_pegasus(
        os.environ.get("TWELVELABS_API_KEY"),
        "https://test-videos.co.uk/vids/bigbuckbunny/mp4/h264/360/Big_Buck_Bunny_360_10s_1MB.mp4",
    )
    print(res)
