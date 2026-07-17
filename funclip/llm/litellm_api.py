import logging


def litellm_call(apikey,
                 model="openai/gpt-3.5-turbo",
                 user_content="How to make tomato beef stew?",
                 system_content=None):
    import litellm

    # Strip the "litellm/" prefix if present so the model name
    # follows litellm's provider/model format (e.g. "anthropic/claude-sonnet-4-6")
    if model.startswith("litellm/"):
        model = model[len("litellm/"):]

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

    response = litellm.completion(**kwargs)
    logging.info("LiteLLM model inference done.")
    return response.choices[0].message.content
