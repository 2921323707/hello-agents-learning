from dotenv import load_dotenv
import os 
from openai import OpenAI 
from typing import List,Dict,Any 

#DEBUG 
import traceback

#加载配置信息
load_dotenv()
VERBOSE = True 
LLM_API_KEY  = os.getenv("LLM_API_KEY")
LLM_BASE_URL = os.getenv("LLM_BASE_URL")
LLM_MODEL    = os.getenv("LLM_MODEL_ID")
if VERBOSE:
    if not all([LLM_API_KEY, LLM_BASE_URL, LLM_MODEL]):
        print("LLM_API_KEY, LLM_BASE_URL, or LLM_MODEL is missing. Please check your .env file.")
        exit(1)


class LLM:
    def __init__(self):

        #定义模型ID
        self.model = LLM_MODEL

        #定义代理客户端
        self.client = OpenAI(
            api_key = LLM_API_KEY,
            base_url = LLM_BASE_URL,
            timeout = 60,
        )  ##这里没有定义MODEL,往往在调用的时候才会指定

        if VERBOSE:
            print("LLM client initialized.")

    def think(self,query:Dict[str,str],temperature:float = 0.7) ->str:
        """
        调用大预言模型进行思考，并返回其响应。
        :message:消息列表
        :temperature:温度参数，用于控制模型的随机程度。
        """
        if VERBOSE:
            print(f"正在调用 {self.model} 模型...")
        try:
            response = self.client.chat.completions.create(
                model = self.model,
                messages = query,
                temperature = temperature,
                stream = True,
            )
            if VERBOSE:
                print("LLM响应成功")


            #处理流式响应 
            collected_content = []
            for chunk in response:
                delta_content = chunk.choices[0].delta.content or ""
                if VERBOSE:
                    print(delta_content, end="", flush=True)
                collected_content.append(delta_content)

                if not VERBOSE:
                    return "".join(collected_content)

        except Exception as e:
            if VERBOSE:
                print(f"LLM调用失败: {e}")
                traceback.print_exc()
            return None


if __name__ == "__main__":
    llm =LLM()

    #构建消息列表
    messages = [
        {"role":"system","content":"你是一个异世界的虚拟人偶，身份为菜小包的好朋友"}
    ]
    user_input = input("请输入你的问题: ") if VERBOSE else input("请输入你的问题: (这是VERBOSE)")

    #添加用户消息
    messages.append({"role":"user","content":user_input})

    response = llm.think(messages)

    if response:
        print("完整模型响应")
        print(response)



