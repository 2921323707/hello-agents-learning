from dotenv import load_dotenv 
import traceback
load_dotenv()


import os 
from tavily import TavilyClient 
from typing import List,Dict,Any 

def search(query:str) -> str:
    """  
    基于tavily的实战网页搜索引擎工具
    """
    print(f"🔍 正在搜索: {query}")
    try:
        api_key = os.getenv("TAVILY_API_KEY")
        if not api_key:
            return "没有配置TAVILY_API_KEY呢"
        
        #感受tavily的轻便吧!!
        client = TavilyClient(
            api_key=api_key
        )
        response = client.search(
            query=query
            )
        return tinyup(response)


    except Exception as e:
        print(f"搜索时发生错误: {e}")
        traceback.print_exc()
        return 0

#对返回信息进行整理
def tinyup(response:dict) -> dict:
    """  
    整理搜索结果
    """
    results = response.get("results",[])
    brief_results = []
    for res in results:
        brief_results.append({
            "title": res.get("title",""),
            "content": res.get("content",""),
            "url": res.get("url","")
        })
    main_info= {
        "query": response.get("query",""),
        "answer": response.get("answer",""),
        "results": brief_results,
    }
    return main_info
#---------------------------------------------------------

class ToolExecutor:
    """   
    工具执行器
    """
    def __init__(self):
        self.tools: Dict[str, Dict[str, Any]] = {}

    def registerTool(self,name:str,description:str,func:callable):
        """   
        向工具执行器注册工具
        """
        if name in self.tools: 
            print(f"工具 {name} 已存在")
        self.tools[name] = {
            "description": description,
            "func": func,
        }
        print(f"工具 {name} 已注册")

    def getTool(self,name:str) -> Dict[str,Any]:
        """   
        根据名称获取工具的描述和执行函数
        """
        return self.tools.get(name,None).get("func")
    def getAvailableTools(self) -> str:
        """    
        获取所有可用工具的描述字符串
        """
        return "\n".join([
            f"- {name}: {info['description']}" 
            for name, info in self.tools.items()
        ])
    
# --- 工具初始化与使用示例 ---
if __name__ == '__main__':
    executor = ToolExecutor()

    search_description = """
    使用此工具进行网页搜索，输入查询字符串，返回搜索结果的摘要。
    当你需要回答关于时事，以及在知识库中找不到答案时，使用此工具。
    """

    executor.registerTool("search",search_description,search)

    print("\n--- 可用的工具 ---")
    print(executor.getAvailableTools())

    # 示例调用搜索工具
    tool_name = "search"
    tool = executor.getTool(tool_name)
    if tool:
        observation = tool("原神fes信息")
        print("\n--- 观察 (Observation) ---")
        print(observation)
    
    else:
        print(f"未找到工具: {tool_name}")

