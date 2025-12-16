import time,os,sys
from llm_client import HelloAgentsLLM
from typing import Dict,List,Any  
import traceback


#Config
VERBOSE = True



class Memory:
    """   
    一个记忆模块，就是一次循环中大模型的行动与反思
    """
    def __init__(self):
        #初始化一个空列表存储记录
        self.records: List[Dict[str,Any]] = [] #type: List[Dict[str,Any]]

    def add_record(self,record_type:str,content:str):
        """   
        向记忆中添加一条新纪录
        params:
        - record_type(str):记录的类型('execution'/'reflection')
        - content(str):记录的具体的内容
        """
        self.records.append({
            "type": record_type,
            "content": content,
        })
        if VERBOSE:
            time.sleep(0.5)
            print(f"添加记录: {record_type} - {content}")



    def get_trajectory(self) ->str :
        """   
        将记忆记录格式化为连贯的字符串文本，用于搭建Prompt
        """
        trajectory = ""
        for record in self.records:
            if record["type"] == "execution":
                trajectory += f"---上一轮尝试(代码) ---\n{record['content']}\n\n"
            elif record["type"] == "reflection":
                trajectory += f"--- 评审员反馈 ---\n{record['content']}\n\n"
        return trajectory.strip()
    
    def get_last_execution(self) -> str:
        """   
        获取最近一次执行的代码
        """
        for record in reversed(self.records): #reversed反转列表
            if record["type"] == "execution":
                return record["content"]
        return ""
    






#PROMPT
# 1.初始执行提示词
INITIAL_PROMPT_TEMPLATE = """
你是一位资深的Python程序员。请根据以下要求，编写一个Python函数。
你的代码必须包含完整的函数签名、文档字符串，并遵循PEP 8编码规范。

要求: {task}

请直接输出代码，不要包含任何额外的解释。
"""

# 2.反思提示词
REFLECT_PROMPT_TEMPLATE = """
你是一位极其严格的代码评审专家和资深算法工程师，对代码的性能有极致的要求。
你的任务是审查以下Python代码，并专注于找出其在**算法效率**上的主要瓶颈。

# 原始任务:
{task}

# 待审查的代码:
```python
{code}
```

请分析该代码的时间复杂度，并思考是否存在一种**算法上更优**的解决方案来显著提升性能。
如果存在，请清晰地指出当前算法的不足，并提出具体的、可行的改进算法建议（例如，使用筛法替代试除法）。
如果代码在算法层面已经达到最优，才能回答“无需改进”。

请直接输出你的反馈，不要包含任何额外的解释。
""" 

# 3. 优化提示词
REFINE_PROMPT_TEMPLATE = """
你是一位资深的Python程序员。你正在根据一位代码评审专家的反馈来优化你的代码。

# 原始任务:
{task}

# 你上一轮尝试的代码:
{last_code_attempt}

# 评审员的反馈:
{feedback}

请根据评审员的反馈，生成一个优化后的新版本代码。
你的代码必须包含完整的函数签名、文档字符串，并遵循PEP 8编码规范。
请直接输出优化后的代码，不要包含任何额外的解释。
"""

class ReflectionAgent:
    """   
    反思智能体
    """
    def __init__(self,client,max_iterations=3):
        self.client = client
        self.max_iterations = max_iterations
        self.memory = Memory()


    def run(self,task:str):
        initial_prompt = INITIAL_PROMPT_TEMPLATE.format(task=task)
        initial_message = [{"role": "user", "content": initial_prompt}]

        initial_code = self.client.think(initial_message)
        self.memory.add_record("execution",initial_code)

        for i in range(self.max_iterations):
            if VERBOSE:
                print(f"第{i+1}轮循环")
            
            last_code = self.memory.get_last_execution()
            reflect_prompt = REFLECT_PROMPT_TEMPLATE.format(task = task,code = last_code)
            reflect_message = [{"role": "user", "content": reflect_prompt}]
            reflect_feedback = self.client.think(reflect_message)
            self.memory.add_record("reflection",reflect_feedback)

            if "无需改进" in reflect_feedback or "no need for improvement" in reflect_feedback.lower():
                if VERBOSE:
                    print("无需改进，循环结束")
                break

            refine_prompt = REFINE_PROMPT_TEMPLATE.format(task = task,last_code_attempt = last_code,feedback = reflect_feedback)
            refine_message = [{"role": "user", "content": refine_prompt}]
            refine_code = self.client.think(refine_message)
            self.memory.add_record("execution",refine_code)


        final_code = self.memory.get_last_execution()
        return final_code
    

if __name__ == "__main__":
    try:
        llm_client = HelloAgentsLLM()
        reflection_agent = ReflectionAgent(llm_client)
        final_code = reflection_agent.run("写一个快速排序算法")
        print(final_code)
    except Exception as e:
        print(f"运行时发生错误: {e}")
        traceback.print_exc()





    #无需改进时处理容易出错，需要添加判断


    

