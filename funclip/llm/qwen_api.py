import dashscope
from dashscope import Generation


def call_qwen_model(key=None, 
                    model="qwen_plus", 
                    user_content="如何做西红柿炖牛腩？", 
                    system_content=None):
    dashscope.api_key = key
    if system_content is not None and len(system_content.strip()):
        messages = [
            {'role': 'system', 'content': system_content},
            {'role': 'user', 'content': user_content}
      ]
    else:
        messages = [
            {'role': 'user', 'content': user_content}
      ]
    responses = Generation.call(model,
                                messages=messages,
                                result_format='message',  # 设置输出为'message'格式
                                stream=False, # 设置输出方式为流式输出
                                incremental_output=False  # 增量式流式输出
                                )
    print(responses)
    return responses['output']['choices'][0]['message']['content']


if __name__ == '__main__':
    call_qwen_model('YOUR_BAILIAN_APIKEY')