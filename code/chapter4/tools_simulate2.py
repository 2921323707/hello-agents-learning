from dotenv import load_dotenv # 用于加载环境变量  
import traceback  #用于DEBUG调试
import os #读取环境变量
from tavily import TavilyClient 
from typing import List,Dict,Any 

#config
load_dotenv() 
VERBOSE = False
#加载环境变量，这里用到Tavily 
tavily_api_key = os.getenv("TAVILY_API_KEY")
if tavily_api_key and VERBOSE:
    print("api_key已导入文件")




def search(query:str,verbose:bool=False) -> str:
    """   
    搜索查询字符串并返回搜索结果。 
    params:
        query(str):查询字符串
        verbose(bool):是否开启调试输出，默认False
    """
    if verbose:
        print(f"🔍 正在执行 [Tavily] 网页搜索: {query}")
    try:
        client = TavilyClient(
            api_key=tavily_api_key
        )
        response = client.search(
            query=query
        )
        if verbose:
            print(f"✅ Tavily API 搜索成功，返回 {len(response['results'])} 条结果")
        return response

    except Exception as e:
        if verbose:
            print(f"❌ 调用Tavily API时发生错误: {e}")
            traceback.print_exc()
        return None
    

# print(search("Hello Agents 是什么？",verbose=True))



#<think>以上定义了一个工具的特例WebSearch，用于搜索互联网，
#现在定义一个通用的工具执行器

class ToolExecuter:
    def __init__(self):
        self.tools:Dict[str,Dict[str,Any]] = {}
        pass 

    def registerTool(self,name:str,description:str,func:callable):
        """  
        向工具执行器注册工具
        """
        if name in self.tools and VERBOSE:
            print(f"工具已经存在{name}")
        self.tools[name] = {
            "description":description,
            "func":func
        }
        if VERBOSE:
            print(f"工具注册成功: {name}")


    def getTool(self,name:str) -> Dict[str,Any]:
        """   
        根据名称获取执行函数
        """
        return self.tools.get(name).get("func")
    
    def availableTools(self) -> str:
        """   
        获取工具描述列表
        """
        return "\n".join([
            f"{name}:{info['description']}"
            for name,info in self.tools.items()
        ])
    

if __name__ == "__main__":
    executer = ToolExecuter()
    
    #模拟注册工具
    search_description = """
    输入查询字符串，返回搜索结果的摘要
    尤其是你需要回答关于时事，最新事件相关的问题的时候，
    请使用这个工具。
    (这种情况下不要使用自生知识库回答问题)
    """
    executer.registerTool(
        name = "search",
        description=search_description,
        func=search
    )

    #获取工具描述列表
    print(executer.availableTools())

    #调用工具
    tool_name = "search"

    #simulate_search_input
    simulate_search_input = "Hello Agents 是什么？" if VERBOSE else input("请输入搜索查询: ")

    tool_func = executer.getTool(tool_name)
    if tool_func:
        result = tool_func(simulate_search_input)
        print(f"Observation: {result}")