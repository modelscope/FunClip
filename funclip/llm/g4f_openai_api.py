from g4f.client import Client

if __name__ == '__main__':
    from llm.demo_prompt import demo_prompt
    client = Client()
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "你好你的名字是什么"}],
    )
    print(response.choices[0].message.content)
 

def g4f_openai_call(prompt, model="gpt-3.5-turbo"):
    client = Client()
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
    )
    return(response.choices[0].message.content)