from typing import Dict,List,Any 
from llm_client_simulate import HelloAgentsLLM
import time 
import traceback

#Config
VERBOSE = True

class Memory:
    """   
    记忆存储
    """
    def __init__(self):
        self.records:List[Dict[str,Any]] = []

    def add_record(self,record_type:str,content:str):
        """  
        向记忆中添加一条记录(格式化)
        """
        self.records.append({
            "type":record_type,
            "content":content
        })

    def get_trajectory(self) -> str:
        """   
        将记忆转化为连贯的字符串文本,输入prompt
        """
        trajectory = ""
        for record in self.records:
            if record["type"] == "execution":
                trajectory += f"--- 上一轮尝试(代码) ---\n{record['content']}\n\n"
            elif record["type"] == "reflection":
                trajectory += f"--- 评审员反馈 ---\n{record['content']}\n\n"

        return trajectory.strip()


    def get_last_execution(self) -> str:
        """   
        获取最近一次执行的代码
        """
        for record in reversed(self.records):
            if record["type"] == "execution":
                return record["content"]
        return
    
    

