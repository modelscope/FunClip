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
    
    
def openai_call(prompt, model="gpt-3.5-turbo"):
    client = OpenAI(
        # This is the default and can be omitted
        api_key=os.environ.get("OPENAI_API_KEY"),
    )

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model=model,
    )
    logging.info("Openai model inference done.")
    return chat_completion.choices[0].message.content