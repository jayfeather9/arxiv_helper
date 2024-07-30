from openai import OpenAI
import os

def get_response(prompt):
    client = OpenAI(
        api_key=os.getenv("DASHSCOPE_API_KEY"), # 如果您没有配置环境变量，请在此处用您的API Key进行替换
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",  # 填写DashScope服务的base_url
    )
    completion = client.chat.completions.create(
        model="qwen-turbo",
        messages=[
            {'role': 'system', 'content': 'You are a helpful assistant.'},
            {'role': 'user', 'content': prompt}],
        temperature=0.8,
        top_p=0.8
        )
    # print(completion.model_dump_json())
    return completion.choices[0].message.content

if __name__ == '__main__':
    print(get_response("Hello, answer me in Chinese"))