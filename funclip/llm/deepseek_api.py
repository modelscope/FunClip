from openai import OpenAI

def deepseek_call(api_key, model_name, system_content, user_content):
    client = OpenAI(
        api_key=f"{api_key}",
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )

    conversation = [
        {"role": "system", "content": system_content},
        {"role": "user", "content": ""}
    ]
    completion = client.chat.completions.create(
        model="deepseek-r1",
        messages=conversation
    )
    result = completion.choices[0].message.content
    print(result)

    # 增加「身份确认」
    conversation.append({"role": "assistant", "content": result})
    conversation.append({"role": "user", "content": user_content})
    completion = client.chat.completions.create(
        model="deepseek-r1",
        messages=conversation
    )

    result = completion.choices[0].message.content
    print(result)
    return result
