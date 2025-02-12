import google.generativeai as genai

def gemini_call(api_key, model_name, system_content, user_content):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name)
    
    # Gemini 不直接支持 system prompt，所以我们将其添加到用户消息中
    prompt = f"{system_content}\n\n{user_content}"
    response = model.generate_content(prompt)
    
    return response.text 