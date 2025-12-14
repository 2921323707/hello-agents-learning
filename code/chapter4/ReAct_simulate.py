import re #正则表达式用于解析大模型的输出
from llm_client_simulate import HelloAgentsLLM # 导入大模型客户端
from tools_simulate import ToolExecutor,search # 导入工具函数

#配置模式
React_Prompt_Template = """  
请注意，你是一个有能力调用外部工具的助手

可用工具如下:
{tools}

请严格按照以下格式进行回应

Thought:你的思考过程，用于分析问题，拆解任务，规划下一步
Action:你决定采取的行动,必须是以下格式之一:
- `{{tool_name}}[{{tool_input}}]`:调用一个可用工具。
- `Finish[最终答案]`:当你确定已经获得了最终答案时，必须在Action字段后使用此格式。

现在，请开始解决以下问题
Question: {question}
History: {history}
"""
VERBOSE = True

class ReActAgent:
    def __init__(self,llm_client,tool_executor,max_steps:int = 4):
        self.llm_client = llm_client 
        self.tool_executor = tool_executor
        self.max_steps = max_steps
        self.history = []

    def run(self,question:str):
        self.history = []
        current_step = 0 

        while current_step < self.max_steps:
            current_step += 1 

            tools_desc = self.tool_executor.getAvailableTools()
            history_str = "\n".join(self.history)

            prompt = React_Prompt_Template.format(tools = tools_desc,question = question,history = history_str)



            messages = [{"role":"user","content":prompt}] #工具描述+问题+历史记录
            response = self.llm_client.think(messages)

            thought,action = self._parse_output(response)
            print(f"{current_step}步的输出: {thought},{action}")


            import time
            if action.startswith("Finish"):
                time.sleep(5)
                final_ans = self._parse_action_out(action)
                print(f"最终答案: {final_ans}")
                return final_ans
            
            #
            tool_name,tool_input = self._parse_action(action)

            try:
                tool_func = tool_executor.getTool(tool_name)
                tool_output = tool_func(tool_input)
                self.history.append(f"Action: {action}")
                self.history.append(f"Observation: {tool_output}")
            except Exception as e:
                self.history.append(f"Observation: Error calling tool {tool_name}: {e}")
                continue


        print("Max steps reached. No final answer.")
        return self.history[-1]


    def _parse_output(self,text:str):
        # 使用 re.DOTALL 标志，让 . 匹配换行符，支持多行内容
        thought_match = re.search(r"Thought:(.*)",text, re.DOTALL)
        action_match  = re.search(r"Action:(.*)",text, re.DOTALL)
        if thought_match and action_match:
            thought = thought_match.group(1).strip()
            action = action_match.group(1).strip()
            return thought,action
        return None,None

    def _parse_action(self,action:str):
        tool_match = re.search(r"(\w+)\[(.+)\]",action)
        if tool_match:
            tool_name = tool_match.group(1).strip()
            tool_input = tool_match.group(2).strip()
            return tool_name,tool_input
        return None,None

    def _parse_action_out(self,action:str):
        # 匹配 Finish[answer="..."] 格式，支持多行内容
        # 使用 re.DOTALL 让 . 匹配换行符，使用非贪婪匹配到第一个 "]
        finish_match = re.search(r"Finish\[(.*)\]", action, re.DOTALL)
        if finish_match:
            return finish_match.group(1).strip()
        return None



llm_client = HelloAgentsLLM()
tool_executor = ToolExecutor()
search_desc = "一个用于搜索互联网的工具，输入是一个查询字符串，输出是搜索结果"
tool_executor.registerTool("search",search_desc,search)

agent = ReActAgent(llm_client,tool_executor,9)
question = "白丝和黑丝给男生的诱惑不一样吗"
agent.run(question)

            




