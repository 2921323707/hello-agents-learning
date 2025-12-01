import os 
import re
import dotenv
import json 
import requests
from typing import Dict,List,Optional,Any
from tavily import TavilyClient 
#

AGENT_SYSTEM_PROMPT = """
你是一个智能旅行助手。你的任务是分析用户的请求，并使用可用工具一步步地解决问题。

# 可用工具:
- `get_weather(city: str)`: 查询指定城市的实时天气。
- `get_attraction(city: str, weather: str)`: 根据城市和天气搜索推荐的旅游景点。

# 行动格式:
你的回答必须严格遵循以下格式。首先是你的思考过程，然后是你要执行的具体行动，每次回复只输出一对Thought-Action：
Thought: [这里是你的思考过程和下一步计划]
Action: [这里是你要调用的工具，格式为 function_name(arg_name="arg_value")]

# 任务完成:
当你收集到足够的信息，能够回答用户的最终问题时，你必须在`Action:`字段后使用 `finish(answer="...")` 来输出最终答案。

请开始吧！
"""

#获取天气
def get_weather(city:str) -> str:
    """
    通过调用wttr.in API查询天气信息
    项目链接:https://github.com/chubin/wttr.in

    Args:
        city:城市名称 example:Beijing,Shanghai,Tokyo
    Returns:
        str:城市天气信息
    """
    url = f"https://wttr.in/{city}?format=j1"
    headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36"}
    try:
        # 使用VPN代理，端口80
        response = requests.get(url, proxies={"http": "http://127.0.0.1:80", "https": "http://127.0.0.1:80"}, headers=headers)
        response.raise_for_status()

        #解析返回的数据
        data = response.json()

        current_condition = data['current_condition'][0]
        temp_C = current_condition['temp_C']
        weather_Desc = current_condition['weatherDesc'][0]['value']



        return f"{city}:当前天气:{weather_Desc},温度{temp_C}摄氏度"
    except requests.exceptions.HTTPError as e:
        return f"错误：查询天气时遇到网络问题 - {e}"
    except (KeyError,IndexError) as e:
        return f"错误：解析天气数据失败，可能是城市名称无效 - {e}"
# print(get_weather("Beijing"))


def get_attraction(city:str,weather:str) -> str:
    """
    根据城市和天气，使用Tavily Search API搜索并返回优化后的景点推荐。

    Args:
        city:城市名称 example:Beijing,Shanghai,Tokyo
        weather:天气信息 example:晴天,多云,雨天
    Returns:
        str:景点推荐信息
    """
    if not TAVILY_API_KEY:
        return "错误，未配置TAVILY_API_KEY"

    tavily = TavilyClient(api_key=TAVILY_API_KEY)
    #tavily文档https://docs.tavily.com/welcome

    query = f"{city}在{weather}天气下最值得去的旅游景点推荐及理由"

    try:
        response = tavily.search(query = query,search_depth = "advanced",include_answer = True)
        if response.get("answer"):
            return response['answer']

        formatted_results = []
        for result in response.get("results",[]):
            formatted_results.append(f"{result['title']}-{result['content']}")
        if not formatted_results:
            return "没找到"
        return f"根据搜索，为你找到如下信息  \n \n {formatted_results}"

    except Exception as e:
        print(f"{e}")



available_tools = {
    "get_weather":get_weather,
    "get_attraction":get_attraction,
}


from openai import OpenAI

class OpenAICompatibleClient:
    """
    一个用于调用兼容OpenAI接口的LLM服务的客户端
    """
    def __init__(self,model:str,api_key:str,base_url:str):
        self.model = model 
        self.client = OpenAI(api_key=api_key,base_url=base_url)

    def generate(self,prompt:str,system_prompt:str) -> str:
        """调用LLM API来生成回应"""
        print("正在调用大语言模型")
        try:
            messages = [
                {'role':'system','content':system_prompt},
                {'role':'user','content':prompt}
            ]
            response = self.client.chat.completions.create(
                model = self.model,
                messages = messages,
                stream = False 
            )

            answer = response.choices[0].message.content
            print("大语言模型响应成功")
            return answer 
        except Exception as e:
            print(f"调用LLM API时发生错误: {e}")
            return "错误：调用语言模型服务时出错。"




dotenv.load_dotenv()

#config
API_KEY = os.getenv("DEEPSEEK_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
BASE_URL = "https://api.deepseek.com/v1"
MODEL_ID = "deepseek-chat"

llm = OpenAICompatibleClient(
    model = MODEL_ID,
    api_key = API_KEY,
    base_url = BASE_URL
)

user_prompt = "你好，请帮我查询一下东京的天气，然后根据天气推荐一个合适的旅游景点。"
prompt_history = [f"用户请求:{user_prompt}"]

print(f"用户输入:{user_prompt}\n" + "="* 40)

for i in range(5):
    print(f"--- 循环{i+1} ---")
    full_prompt = "\n".join(prompt_history)
    llm_output = llm.generate(full_prompt,system_prompt=AGENT_SYSTEM_PROMPT)

    #抓取Thought-Action对
    match = re.search(f'(Thought:.*?Action:.*?)(?=\n\s*(?:Thought:|Action:|Observation:)|\Z)',llm_output,re.DOTALL)
    if match:
        truncated = match.group(1).strip()
        if truncated != llm_output.strip():
            llm_output = truncated
            print("已截断多余的 Thought-Action对")
    print(f"模型输出:\n{llm_output}\n")
    prompt_history.append(llm_output)


    #解析行动
    action_match = re.search(r"Action:(.*)",llm_output,re.DOTALL)
    if not action_match:
        print("解析错误：模型输出没有找到匹配的Action")
        break 
    action_str = action_match.group(1).strip()

    if action_str.startswith('finish'):
        final_answer = re.search(r'finish\(answer="(.*)"\)',action_str).group(1)
        print(f"任务完成,最终答案{final_answer}")
        break

    tool_name = re.search(r"(\w+)\(",action_str).group(1)
    args_str = re.search(r"\((.*)\)",action_str).group(1)
    kwargs = dict(re.findall(r'(\w+)="([^"]*)"',args_str)) ####

    if tool_name in available_tools:
        observation = available_tools[tool_name](**kwargs)
    else:
        observation = f"错误，未定义的工具{tool_name}"
    
    observation_str = f"Observation:{observation}"
    print(f"{observation_str}\n" + "="*40)
    prompt_history.append(observation_str)








