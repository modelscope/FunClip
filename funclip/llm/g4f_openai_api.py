from g4f.client import Client

if __name__ == '__main__':
    from llm.demo_prompt import demo_prompt
    client = Client()
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "你好你的名字是什么"}],
    )
    print(response.choices[0].message.content)
 

def g4f_openai_call(model="gpt-3.5-turbo", 
                    user_content="如何做西红柿炖牛腩？", 
                    system_content=None):
    client = Client()
    if system_content is not None and len(system_content.strip()):
        messages = [
            {'role': 'system', 'content': system_content},
            {'role': 'user', 'content': user_content}
      ]
    else:
        messages = [
            {'role': 'user', 'content': user_content}
      ]
    response = client.chat.completions.create(
        model=model,
        messages=messages,
    )
    return(response.choices[0].message.content)