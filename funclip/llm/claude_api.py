import anthropic

def claude_call(api_key, model_name, system_content, user_content):
    client = anthropic.Anthropic(api_key=api_key)
    
    messages = [
        {"role": "system", "content": system_content},
        {"role": "user", "content": user_content}
    ]
    
    response = client.messages.create(
        model=model_name,
        messages=messages,
        max_tokens=1024
    )
    
    return response.content[0].text 