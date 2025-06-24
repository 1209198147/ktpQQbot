from openai.types.chat import ChatCompletionMessageToolCall
from deepseek.conversation.conversation import Conversation
import inspect, json

class LLMTools:
    tools = None
    functions = None

    def __init__(self):
        self.tools = []
        self.functions = dict()

    def getTools(self):
        return self.tools

    def append(self, tool:dict, func):
        if not self.tools:
            self.tools = []
        if not self.functions:
            self.functions = dict()
        self.tools.append(tool)
        self.functions[tool["function"]["name"]] = func
        return self

    def removeByname(self, name: str):
        if not self.tools:
            return True
        idx = -1
        for i, tool in enumerate(self.tools):
            if tool["function"]["name"] == name:
                idx = i
                break
        if idx==-1:
            return False
        tool=self.tools.pop(idx)
        self.functions.pop(tool["function"]["name"])
        return True

    def invoke_function(self, tool_call:ChatCompletionMessageToolCall, conversation:Conversation=None):
        if not tool_call or tool_call.type != 'function':
            return
        tool_dict = tool_call.function.dict()
        func = self.functions[tool_dict['name']]
        if not func:
            raise Exception("未找到这个函数")
        try:
            args = tool_dict['arguments']
            args_dict = json.loads(args)
            result = func(**args_dict)
            if conversation is not None:
                conversation.append({"role": "tool", "tool_call_id": tool_call.id, "content": result})
            return result
        except Exception as e:
            print(f"调用函数失败！\n{e}")

def get_param_type(annotation):
    """将Python类型转换为JSON schema类型"""
    if annotation is inspect.Parameter.empty:
        return "string"  # 默认类型为字符串
    type_map = {
        str: "string",
        int: "integer",
        float: "number",
        bool: "boolean",
        list: "array",
        dict: "object"
    }
    return type_map.get(annotation, "string")

def llmtool(tools:LLMTools):
    """装饰器工厂函数，用于将函数注册为LLM工具"""

    def decorator(func):
        # 解析函数文档字符串
        description = None
        params_desc = {}
        if func.__doc__:
            doc = func.__doc__.strip().split("\n")
            for i, line in enumerate(doc):
                line = line.strip()
                if i == 0:
                    description = line
                elif ":" in line:  # 参数描述行
                    param, desc = line.split(":", 1)
                    params_desc[param.strip()] = desc.strip()

        # 创建工具定义
        tool = {
            "type": "function",
            "function": {
                "name": func.__name__,
                "description": description or func.__name__,
            }
        }

        # 获取函数签名
        sig = inspect.signature(func)
        parameters = list(sig.parameters.values())

        if parameters:
            properties = {}
            required = []
            for param in parameters:
                # 跳过 self 参数（如果是类方法）
                if param.name == "self":
                    continue

                # 获取参数描述
                param_desc = params_desc.get(param.name, param.name)

                properties[param.name] = {
                    "type": get_param_type(param.annotation),
                    "description": param_desc
                }

                # 如果参数没有默认值，则标记为必需
                if param.default is param.empty:
                    required.append(param.name)

            # 添加参数定义到工具
            tool["function"]["parameters"] = {
                "type": "object",
                "properties": properties,
                "required": required
            }

        # 注册工具到管理器
        tools.append(tool, func)

        # 返回原始函数，保持其功能不变
        return func

    return decorator