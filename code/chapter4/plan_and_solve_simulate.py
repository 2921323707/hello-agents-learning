#导入模块
import os 
import ast # 用于解析Python代码
from llm_client_simulate import HelloAgentsLLM
from dotenv import load_dotenv
from typing import List,Dict  

load_dotenv()

#llm客户端已定义

PLANNER_PROMPT_TEMPLATE = """
你是一位顶级的AI规划专家，你的任务是将用户提出的复杂问题分解为一个或多个简单的子问题。
确保计划中地每一个步骤都是独立的，可执行地小任务，严格按照逻辑顺序排列
你的输出必须是一个python列表，每个元素都是一个描述子任务的字符串。

问题:{question}

请严格按照以下格式输出你的规划,```python与```作为前后缀是必要的:
```python
["步骤1"，"步骤2"，"步骤3",...]
```
"""

#这里```python与```是必要的，不能省略,目的是告诉模型输出的是python代码

class Planner:
    def __init__(self,llm_client):
        self.llm_client = llm_client

    def plan(self,question:str) -> List[str]:
        """
        规划函数，将用户问题分解为子问题
        """
        prompt = PLANNER_PROMPT_TEMPLATE.format(question=question)
        message = [{"role":"user","content":prompt}]

        #调用llm
        response = self.llm_client.think(message)

        # DEBUG
        # print(f"计划已生成: \n{response}")

        plan_str = response.split("```python")[1].split("```")[0].strip()
        
        plan = ast.literal_eval(plan_str) 
        return plan if isinstance(plan,list) else []



#执行器
EXECUTOR_PROMPT_TEMPLATE = """    
你是一位顶级的AI执行专家。你的任务是严格按照给定的计划，一步步地解决问题。
你将收到原始问题、完整的计划、以及到目前为止已经完成的步骤和结果。
请你专注于解决“当前步骤”，并仅输出该步骤的最终答案，不要输出任何额外的解释或对话。

# 原始问题:
{question}

# 完整计划:
{plan}

# 历史步骤与结果:
{history}

# 当前步骤:
{current_step}

请仅输出针对“当前步骤”的回答:
"""

class Executor:
    def __init__(self,llm_client):
        self.llm_client = llm_client
    
    def execute(self,question,plan):
        history = ""
        final_answer = ""

        for i,step in enumerate(plan,1):  #从1开始
            prompt = EXECUTOR_PROMPT_TEMPLATE.format(
                question = question ,
                plan = plan,
                history = history,
                current_step = step
            )
            message = [{"role":"user","content":prompt}]

            #调用llm
            response = self.llm_client.think(message)

            # DEBUG
            # print(f"计划已生成: \n{response}")

            history += f"步骤{i}:{step}\n结果:{response}\n"

            final_answer = response
        return final_answer
    

class PlanAndSolve:
    def __init__(self,llm_client):
        self.llm_client = llm_client
        self.planner = Planner(llm_client)
        self.executor = Executor(llm_client)
    
    def run(self,question:str) -> str:
        """
        运行函数，将用户问题分解为子问题，然后执行子问题
        """
        plan = self.planner.plan(question)
        if not plan:
            return "无法生成计划"
        return self.executor.execute(question,plan)
    
if __name__ == "__main__":
    llm_client = HelloAgentsLLM()
    plan_and_solve = PlanAndSolve(llm_client)
    result = plan_and_solve.run("求解方程x^2-2x-3=0")
    print(result)


