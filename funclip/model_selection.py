MOSS_MODEL = "OpenMOSS-Team/MOSS-Transcribe-Diarize"
MOSS_MODEL_REVISION = "e8681d68e7042738ffca8ac8212bc8fcb1131ab8"
MOSS_DEFAULT_BASE_URL = "http://127.0.0.1:8898/v1"


def _moss_model_kwargs(
    backend="vllm",
    base_url=MOSS_DEFAULT_BASE_URL,
    api_key=None,
    max_tokens=8192,
):
    backend = str(backend).lower()
    if backend != "vllm":
        raise ValueError(f"unsupported MOSS backend: {backend}")

    max_tokens = int(max_tokens)
    if max_tokens <= 0:
        raise ValueError("MOSS generation token limit must be positive")

    kwargs = {
        "model": MOSS_MODEL,
        "model_revision": MOSS_MODEL_REVISION,
        "backend": backend,
        "disable_update": True,
    }
    base_url = str(base_url or "").rstrip("/")
    if not base_url:
        raise ValueError("--moss-base-url is required for remote MOSS backends")

    kwargs.update(
        {
            "vllm_base_url": base_url,
            "vllm_model": "moss-transcribe-diarize",
            "vllm_response_format": "json",
            "max_completion_tokens": max_tokens,
        }
    )
    if api_key:
        kwargs["vllm_api_key"] = api_key
    return kwargs


def create_asr_model(
    model_name,
    lang,
    auto_model_cls,
    moss_backend="vllm",
    moss_base_url=MOSS_DEFAULT_BASE_URL,
    moss_api_key=None,
    moss_max_tokens=8192,
):
    if model_name == "moss":
        return auto_model_cls(
            **_moss_model_kwargs(
                backend=moss_backend,
                base_url=moss_base_url,
                api_key=moss_api_key,
                max_tokens=moss_max_tokens,
            )
        )
    if model_name == "fun-asr-nano":
        return auto_model_cls(
            model="FunAudioLLM/Fun-ASR-Nano-2512",
            trust_remote_code=True,
            remote_code="./model.py",
            vad_model="fsmn-vad",
            vad_kwargs={"max_single_segment_time": 30000},
            spk_model="cam++",
            hub="hf",
        )
    if model_name == "sensevoice":
        return auto_model_cls(
            model="iic/SenseVoiceSmall",
            vad_model="fsmn-vad",
            vad_kwargs={"max_single_segment_time": 30000},
            spk_model="cam++",
        )

    paraformer_model = (
        "iic/speech_seaco_paraformer_large_asr_nat-zh-cn-16k-common-vocab8404-pytorch"
        if lang == "zh"
        else "iic/speech_paraformer_asr-en-16k-vocab4199-pytorch"
    )
    return auto_model_cls(
        model=paraformer_model,
        vad_model="damo/speech_fsmn_vad_zh-cn-16k-common-pytorch",
        punc_model="damo/punc_ct-transformer_zh-cn-common-vocab272727-pytorch",
        spk_model="damo/speech_campplus_sv_zh-cn_16k-common",
    )
