import requests

def deepseek_call_v2(api_key, model_name, system_content, user_content):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    data = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_content}
        ]
    }

    response = requests.post(
        "https://api.deepseek.com/v1/chat/completions",
        headers=headers,
        json=data
    )

    print(response.json())
    result = response.json()["choices"][0]["message"]["content"]
    print(result)
    return result