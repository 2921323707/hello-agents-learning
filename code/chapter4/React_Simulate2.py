# -*- coding: utf-8 -*-
import re 
import time
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


            #----------------------------------------


            response = self.client.think(messages)

            #解析响应
            thought,action = self._parse_llm_response(response)

            # #DEBUG
            # #分析提取结果
            # print(f"action:\n{action}")

            

            if action.startswith("Finish"):
                if VERBOSE:
                    print("成功捕捉Finish指令，准备退出")
                time.sleep(3)
                res = self._parse_finish(action)
                
                if res:
                    return res 
                return 
            

            #执行工具section
            tool_name,tool_input = self._parse_action(action)


            if tool_name and tool_input:
                tool_func = self.tool_executor.getTool(tool_name) #检查返回类型!

                if VERBOSE:
                    print(type(tool_func))

             


                #执行工具
                tool_res = tool_func(tool_input)
                # print(f"工具 {tool_name} 执行结果: {tool_res}")

                #历史记录更新
                self.history.append(f"Action:{action}")
                self.history.append(f"Observation:{tool_res}")
                
        print("达到最大步数，退出")
        return
                


            


            
            


    #定义解析方法
    #解析llm响应
    def _parse_llm_response(self,response:str):
        """   
        解析llm的响应，提取Thought和Action
        Args:
            response (str): llm的响应字符串
        Returns:
            tuple: (thought,action) 包含解析后的思考过程和行动
        """
        thought_match = re.search(r"Thought[:：](.*)Action[:：]",response,re.DOTALL)
        action_match = re.search(r"Action[:：](.*)",response,re.DOTALL)

        if thought_match and action_match:
            thought = thought_match.group(1).strip()
            action = action_match.group(1).strip()

            return thought,action
        
        print(f"无法解析响应: {response}")
        return None,None
    




    #解析action中的工具调用
    def _parse_action(self,action:str):
        tool_match = re.search(r"(\w+)\[(.+)\]",action)
        if tool_match:
            tool_name = tool_match.group(1).strip()
            tool_input = tool_match.group(2).strip()

            return tool_name,tool_input
        return None,None






    #解析最终finish
    def _parse_finish(self,action:str):
        """    
        解析Finish指令，提取最终答案
        Params:
            action (str): Finish指令字符串，格式为"Finish[最终答案]"
        Returns:
            str: 提取到的最终答案
        """
        finish_match = re.search(r"Finish\[(.*)\]",action,re.DOTALL)

        if finish_match:
            return finish_match.group(1).strip()
        return "最终答案匹配出现问题啦"



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

    print(f"\n\n\n!!!!最终输出!!!!\n\n{answer}")


