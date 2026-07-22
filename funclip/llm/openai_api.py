import os
import logging
from openai import OpenAI

ATLASCLOUD_API_BASE = "https://api.atlascloud.ai/v1"
ATLASCLOUD_MODEL_PREFIX = "atlascloud/"


def _resolve_model_config(model):
    base_url = None
    api_key_env = None

    if model.startswith(ATLASCLOUD_MODEL_PREFIX):
        model = model[len(ATLASCLOUD_MODEL_PREFIX):]
        if not model:
            raise ValueError(
                "Model name is empty after stripping atlascloud/ prefix"
            )
        base_url = os.environ.get("ATLASCLOUD_API_BASE", ATLASCLOUD_API_BASE).strip()
        if not base_url:
            base_url = ATLASCLOUD_API_BASE
        api_key_env = "ATLASCLOUD_API_KEY"
    elif model.startswith("deepseek"):
        base_url = "https://api.deepseek.com"
    elif model.startswith("gpt-3.5-turbo"):
        base_url = "https://api.moonshot.cn/v1"

    return model, base_url, api_key_env


if __name__ == '__main__':
    from llm.demo_prompt import demo_prompt
    client = OpenAI(
        # This is the default and can be omitted
        api_key=os.environ.get("OPENAI_API_KEY"),
    )

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": demo_prompt,
            }
        ],
        model="gpt-3.5-turbo-0125",
    )
    print(chat_completion.choices[0].message.content)
    
    
def openai_call(apikey, 
                model="gpt-3.5-turbo", 
                user_content="如何做西红柿炖牛腩？", 
                system_content=None):
    model, base_url, api_key_env = _resolve_model_config(model)
    if not apikey and api_key_env:
        apikey = os.environ.get(api_key_env)

    client = OpenAI(
        # This is the default and can be omitted
        api_key=apikey,
        base_url=base_url
    )
    if system_content is not None and len(system_content.strip()):
        messages = [
            {'role': 'system', 'content': system_content},
            {'role': 'user', 'content': user_content}
      ]
    else:
        messages = [
            {'role': 'user', 'content': user_content}
      ]
    
    chat_completion = client.chat.completions.create(
        messages=messages,
        model=model,
    )
    logging.info("Openai model inference done.")
    return chat_completion.choices[0].message.content
