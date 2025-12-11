import os 
from openai import OpenAI 
from dotenv import load_dotenv
from typing import List, Dict

import traceback
import httpx

load_dotenv()

class HelloAgentsLLM:
    """
    为本书定制的客户端
    调用任何兼容OpenAI接口的服务，并默认使用流式响应
    """

    def __init__(self,model:str= None ,apiKey: str = None,baseurl:str = None,timeout:int = None):
        """   
        初始化客户端，优先使用传入参数，否则从环境变量中获取
            :model: 模型ID
            :apiKey: API密钥
            :baseurl: 基础URL
            :timeout: 超时时间
        """
        self.model = model or os.getenv("LLM_MODEL_ID")
        apiKey = apiKey or os.getenv("LLM_API_KEY")
        baseurl = baseurl or os.getenv("LLM_BASE_URL")
        timeout = timeout or int(os.getenv("LLM_TIMEOUT", 60))

        #检查必填参数是否缺失
        if not all([self.model,apiKey,baseurl]):
            raise ValueError("模型ID、API密钥和服务地址必须被提供或在.env文件中定义。")

        self.client = OpenAI(
            api_key = apiKey,
            base_url = baseurl,
            timeout = timeout,
        )

    def think(self,messages:List[Dict[str,str]],temperature:float=0)-> str:
        """  
        调用大语言模型进行思考，并返回其响应
        :messages: 消息列表
        :temperature: 温度参数，用于控制响应的随机性
        """
        print(f"正在调用{self.model}模型...")

        try:
            response = self.client.chat.completions.create(
                model = self.model,
                messages = messages,
                temperature = temperature,
                stream = True,
            )

            print("LLM响应成功")
            
            collected_content = []
            for chunk in response:
                content = chunk.choices[0].delta.content or ""
                print(content,end = "",flush = True)
                collected_content.append(content)
            print()  # 在流式输出结束后换行
            return "".join(collected_content)

        except Exception as e:
            print(f"调用LLM API时发生错误: {e}")
            traceback.print_exc()
            return None
        

        #调用示例
if __name__ == '__main__':
    try:
        llmClient = HelloAgentsLLM()
        user_input = "你好"
        messages = [
            {"role": "system", "content": "你是一个性感挑逗的助手。"},
            {"role": "user", "content": user_input}
        ]
        response = llmClient.think(messages)
        if response:
            print("完整模型响应:")
            print(response)
    except Exception as e:
         print(e)