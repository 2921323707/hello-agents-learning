# -*- coding: utf-8 -*- 
import os
from dotenv import load_dotenv
import ast #用于将字符串转化为python对象
from llm_client_simulate import HelloAgentsLLM
from typing import List,Dict,Any 


# --------------------------------------------------
#Config
load_dotenv()

VERBOSE =True

#因为client已经在llm_client_simulate.py中定义了，所以这里不需要再定义
PLANNER_PROMPT = """ 
你是一位专业的计划者，你的任务是将用户提出的复杂问题分解为一个或多个简单的子问题。
确保计划中的每一个步骤都是独立的，可执行的小任务，请严格地按照逻辑顺序排列
你的输出必须是一个python列表，每一个元素都是一个描述子任务的字符串。

问题:{question}

请你严格按照以下格式输出你的规划,```python和```作为前后缀是必要的:
```python
["步骤1","步骤2","步骤3"]
```
"""

#tips:```python```是一个代码块，用于表示python代码(Markdown)

EXECUTOR_PROMPT = """   
你是一位执行专家，你的任务是严格按照给定的计划，一步步地解决问题
你将收到原始问题，完整的计划，以及到目前为止已经完成的步骤和结果。
请你专注于解决"当前步骤"，并仅输出该步骤的最终答案，不要输出任何额外的解释和对话

#原始问题
{question}

#完整计划
{plan}

#历史步骤与结果
{history}

#当前步骤
{current_step}

请输出针对当前步骤的回答
"""


###PLAN
class planner:
    def __init__(self,client): 
        self.client = client 
    def plan(self,question:str)->List[str]:
        """    
        对用户输入的复杂问题进行规划，将其分解为多个简单的子问题
        Args:
            question (str): 用户输入的复杂问题
        Returns:
            List[str]: 规划后的子问题列表
        """
        #补全提示词，搭建message
        prompt = PLANNER_PROMPT.format(question=question)
        message = [{"role":"user","content":prompt}]

        #调用llm
        response = self.client.think(message)

        if VERBOSE:

            # print(f"规划器llm回复:\n{response}")
            pass

        extract_response = response.split("```python")[1].split("```")[0].strip()
        result_plan = ast.literal_eval(extract_response) #type(list)
        if result_plan:
            return result_plan
        return 
    
###Ececute
class executor:
    def __init__(self,client):
        self.client = client 
    
    def execute(self,question:str = "",plan:List[str] = []) -> str:
        """    
        执行计划中的子问题，逐步解决复杂问题
        Args:
            question (str): 用户输入的复杂问题
            plan (List[str]): 规划后的子问题列表
        Returns:
            str: 最终解决复杂问题的答案
        """

        #初始化历史记录
        history = ""
        final_answer = ""

        for i,step in enumerate(plan,1):
            #搭建prompt,传入消息列表
            prompt = EXECUTOR_PROMPT.format(
                question = question,
                plan = plan,
                history = history,
                current_step = step
            )
            message = [{"role":"user","content":prompt}]  

            #调用llm
            response = self.client.think(message)

            if VERBOSE:
                # print(f"第{i}步回复:\n{response}")
                pass 

            history += f"第{i}步: {step}\n{response}\n"

        return final_answer
    

class plan_and_solve:
    def __init__(self,client):
        self.client = client
        self.planner = planner(client)
        self.executor = executor(client)

    def run(self,question:str)->str:
        """   
        对用户输入的复杂问题进行规划和执行，返回最终解决复杂问题的答案
        Args:
            question (str): 用户输入的复杂问题
        Returns:
            str: 最终解决复杂问题的答案
        """
        
        #plan
        plan = self.planner.plan(question)
        #act
        final_ans = self.executor.execute(question,plan)
        return final_ans







client = HelloAgentsLLM()
p_s = plan_and_solve(client)
p_s.run("求方程x^2-2x-3=0的根")



