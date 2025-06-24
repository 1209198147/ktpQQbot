from openai import OpenAI
from deepseek.conversation.conversation import Conversation
from deepseek.functool.func_tool import LLMTools

class DeepseekModel:
    clinet = None
    model = None
    tools = None
    response_format = None
    system_prompt = None

    def __init__(self, apiKey: str, model='deepseek-chat', tools:LLMTools=None, system_prompt=None, response_format=None):
        self.clinet = OpenAI(api_key=apiKey, base_url='https://api.deepseek.com')
        self.model = model
        self.tools = tools
        self.response_format = response_format
        if system_prompt:
            self.system_prompt = {'role':'system', 'content':system_prompt}

    def send_conversation(self, conversation:Conversation):
        if self.tools:
            tools = self.tools.getTools()
        response = self.clinet.chat.completions.create(
            model=self.model,
            messages=conversation.getHistoryMsgs(),
            tools=tools,
            response_format=self.response_format
        )
        conversation.append(response.choices[0].message)
        return response.choices[0].message

    def send_msg(self, user_msg: str, conversation:Conversation=None):
        if conversation is not None:
            if self.system_prompt and len(conversation)==0:
                conversation.append(self.system_prompt)
            if self.tools:
                tools = self.tools.getTools()
            conversation.append({'role': 'user', 'content': user_msg})
            response = self.clinet.chat.completions.create(
                model=self.model,
                messages=conversation.getHistoryMsgs(),
                tools=tools,
                response_format=self.response_format
            )
            conversation.append(response.choices[0].message)
            return response.choices[0].message
        else:
            msgs = []
            if self.system_prompt:
                msgs.append(self.system_prompt)
            if self.tools:
                tools = self.tools.getTools()
            msgs.append({'role': 'user', 'content': user_msg})
            response = self.clinet.chat.completions.create(
                model=self.model,
                messages=msgs,
                tools=tools,
                response_format = self.response_format
            )
            return response.choices[0].message


class GeminiModel:
    clinet = None
    model = None
    tools = None
    system_prompt = None

    def __init__(self, apiKey: str, model='gemini-2.5-flash', tools:LLMTools=None, system_prompt=None, response_format=None):
        self.clinet = OpenAI(api_key=apiKey, base_url='https://generativelanguage.googleapis.com/v1beta/openai/')
        self.model = model
        self.tools = tools
        if system_prompt:
            self.system_prompt = {'role':'system', 'content':system_prompt}

    def send_conversation(self, conversation:Conversation):
        tools = None
        if self.tools:
            tools = self.tools.getTools()
        response = self.clinet.chat.completions.create(
            model=self.model,
            messages=conversation.getHistoryMsgs(),
            tools=tools,
            response_format=self.response_format
        )
        conversation.append(response.choices[0].message)
        return response.choices[0].message

    def send_msg(self, user_msg: str, conversation:Conversation=None):
        if conversation is not None:
            if self.system_prompt and len(conversation)==0:
                conversation.append(self.system_prompt)
            if self.tools:
                tools = self.tools.getTools()
            conversation.append({'role': 'user', 'content': user_msg})
            response = self.clinet.chat.completions.create(
                model=self.model,
                messages=conversation.getHistoryMsgs(),
                tools=tools,
                response_format=self.response_format
            )
            conversation.append(response.choices[0].message)
            return response.choices[0].message
        else:
            msgs = []
            if self.system_prompt:
                msgs.append(self.system_prompt)
            if self.tools:
                tools = self.tools.getTools()
            msgs.append({'role': 'user', 'content': user_msg})
            response = self.clinet.chat.completions.create(
                model=self.model,
                messages=msgs,
                tools=tools,
                response_format = self.response_format
            )
            return response.choices[0].message