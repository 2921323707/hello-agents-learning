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

    pass 
