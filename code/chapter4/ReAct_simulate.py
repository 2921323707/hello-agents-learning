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
- `Finish[最终答案]`:当你确定已经获得了最终答案时，使用此格式。
- 当你收集到足够的信息，能够回答用户的最终问题时，你必须在`Action`字段中使用`Finish(answer="...)`格式。

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
            if VERBOSE:
                print(f"Step {current_step}:")

            tools_desc = self.tool_executor.getAvailableTools()
            history_str = "\n".join(self.history)

            prompt = React_Prompt_Template.format(tools = tools_desc,question = question,history = history_str)
            print(f"Prompt: {prompt}")



            messages = [{"role":"user","content":prompt}] #工具描述+问题+历史记录
            response = self.llm_client.think(messages)

            if not response:
                if VERBOSE:
                    print("No response from LLM.")
                break

            thought,action = self._parse_output(response)
            if thought:print(f"Thought: {thought}")
            if not action:
                if VERBOSE:
                    print("No action from LLM.")
                break
            if action.startswith("Finish"):
                final_ans = self._parse_action_out(action)
                print(f"Final Answer: {final_ans}")
                return final_ans
            
            #
            tool_name,tool_input = self._parse_action(action)
            if not tool_name or not tool_input:
                self.history.append("Observation: Invalid action format.")
                continue

            print(f"Calling Tool: {tool_name} with Input: {tool_input}")
            tool_func = tool_executor.getTool(tool_name)
            # print(type(tool_func))
            if not tool_func:
                self.history.append("Observation: Tool not found.")
                continue
            try:
                tool_output = tool_func(tool_input)
                print(f"观察: {tool_output}")
                self.history.append(f"Action: {action}")
                self.history.append(f"Observation: {tool_output}")
            except Exception as e:
                self.history.append(f"Observation: Error calling tool {tool_name}: {e}")
                continue
            finally:
                print(f"Step {current_step} completed.History: {self.history}")

        print("Max steps reached. No final answer.")
        return self.history[-1]


    def _parse_output(self,text:str):
        thought_match = re.search(r"Thought:(.*)",text)
        action_match  = re.search(r"Action:(.*)",text)
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
        finish_match = re.search(r"Finish\(answer=\"(.*)\"\)",action)
        if finish_match:
            return finish_match.group(1).strip()
        return None



llm_client = HelloAgentsLLM()
tool_executor = ToolExecutor()
search_desc = "一个用于搜索互联网的工具，输入是一个查询字符串，输出是搜索结果"
tool_executor.registerTool("search",search_desc,search)

agent = ReActAgent(llm_client,tool_executor,9)
question = "女生的身上为什么香"
agent.run(question)

            




