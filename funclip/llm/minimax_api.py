import requests

def minimax_call(api_key, model_name, system_content, user_content):
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
        "https://api.minimax.chat/v1/text/chat",
        headers=headers,
        json=data
    )
    
    return response.json()["choices"][0]["message"]["content"] 