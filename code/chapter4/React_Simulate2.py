# -*- coding: utf-8 -*-
import re 
from llm_client_simulate import HelloAgentsLLM
from tools_simulate import search,ToolExecutor

#配置模式
React_Prompt_Template = """
请注意，你是一个有能力调用外部工具的助手

可用工具如下:
{tools}

请严格按照以下格式进行回应

Thought:你的思考过程，用于分析问题，拆解任务，并谋划下一步
Action:你决定采取的行动，必须是以下格式之一:
- `{{tool_name}}[{{tool_input}}]` 调用一个可用工具
- `Finish[最终答案]`:当你确定已经获得了最终答案时，必须在Action字段后使用此格式

现在，请开始解决以下问题
Question: {question}
History: {history}
"""
VERBOSE = True 

class ReactAgent:
    def __init__(self,client,tool_executor,max_steps:int = 4):
        self.client = client 
        self.tool_executor = tool_executor
        self.max_steps = max_steps
        self.history = []

    def run(self,question:str):
        """  
        运行React代理
            Args:
                question (str): 要解决的问题    
            Returns:
                str: 最终答案
        """
        
        self.history = []
        current_step = 0 

        while current_step < self.max_steps:
            current_step += 1

            # 搭建提示词
                #获取可用的工具及其描述替代{tools}
            tools_available = self.tool_executor.getAvailableTools()
                #获取history替代{history}
            history_str = "\n".join(self.history)

            # 代换
            prompt = React_Prompt_Template.format(tools = tools_available,history = history_str,question = question)

            #搭建消息并传入llm
            messages = [
                {"role":"user","content":prompt}
            ]

            response = self.client.think(messages)
            
            #DEBUG
            break




if __name__ == "__main__":
    # 初始化LLM客户端
    llm_client = HelloAgentsLLM()
    #初始化工具执行器
    tool_executor = ToolExecutor()

    #注册工具
    #search
    search_des = "一个网页搜索引擎，当你需要回答关于时事以及与时间相关的信息时，使用此工具"
    tool_executor.registerTool("search",search_des,search)

    #初始化agent代理
    agent = ReactAgent(llm_client,tool_executor,5)

    #run
    question = "" if not VERBOSE else input("请输入问题: ")
    answer = agent.run(question)
    print(answer)


