import logging
import os


def _import_litellm():
    try:
        import litellm
        return litellm
    except ImportError:
        raise ImportError(
            "litellm is required for the litellm provider. "
            "Install it with: pip install 'litellm>=1.83.0'"
        )


def litellm_call(apikey,
                 model="openai/gpt-3.5-turbo",
                 user_content="How to make tomato beef stew?",
                 system_content=None):
    litellm = _import_litellm()
    api_base = os.environ.get("LITELLM_API_BASE", "").strip()

    if model.startswith("litellm/"):
        model = model[len("litellm/"):]

    if not model:
        raise ValueError("Model name is empty after stripping litellm/ prefix")

    messages = []
    if system_content is not None and len(system_content.strip()):
        messages.append({'role': 'system', 'content': system_content})
    messages.append({'role': 'user', 'content': user_content})

    kwargs = {
        'model': model,
        'messages': messages,
        'stream': False,
        'drop_params': True,
    }
    if apikey:
        kwargs['api_key'] = apikey
    if api_base:
        kwargs['api_base'] = api_base

    try:
        response = litellm.completion(**kwargs)
    except litellm.AuthenticationError as e:
        logging.error(f"LiteLLM authentication failed: {e}")
        raise
    except litellm.NotFoundError as e:
        logging.error(f"LiteLLM model not found: {e}")
        raise
    except litellm.RateLimitError as e:
        logging.warning(f"LiteLLM rate limited: {e}")
        raise
    except litellm.Timeout as e:
        logging.error(f"LiteLLM request timed out: {e}")
        raise
    except litellm.APIConnectionError as e:
        logging.error(f"LiteLLM connection error: {e}")
        raise

    choices = getattr(response, 'choices', None)
    if not choices:
        logging.error("LiteLLM returned empty choices")
        return ""

    content = getattr(choices[0].message, 'content', None)
    if content is None:
        logging.warning("LiteLLM returned null content")
        return ""

    logging.info("LiteLLM model inference done.")
    return content
