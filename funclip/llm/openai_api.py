import os
import logging
from openai import OpenAI


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
    client = OpenAI(
        # This is the default and can be omitted
        api_key=apikey,
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