import random
import yaml

from ncatbot.core import BotClient, MessageChain, Text, At, Image, Face, Reply
from ncatbot.core import GroupMessage, PrivateMessage
from ncatbot.utils.logger import get_log

from deepseek.model.model import GeminiModel, DeepseekModel
from deepseek.conversation.conversation import Conversation, ChatMemory

from core.ktp.tools import ktpTool

import json


group_chat_chace = ChatMemory()
private_chat_chace = ChatMemory()
model = None

config_path = 'config.yml'
_log = get_log("main")

with open(config_path) as f:
    config = yaml.load(f, Loader=yaml.FullLoader)

with open(config['system_prompt']) as f:
    system_prompt = f.read()


_log.info(f"使用{config['model']}模型")
if config['model'].lower()=='gemini':
    model = GeminiModel(apiKey=config['apiKey'],
                          tools=ktpTool,
                          system_prompt=system_prompt)
elif config['model'].lower()=='deepseek':
    model = DeepseekModel(apiKey=config['apiKey'],
                        tools=ktpTool,
                        system_prompt=system_prompt,
                        response_format={
                            'type': 'json_object'
                        })
bot = BotClient()
def parse_message(message):
    message_json = json.loads(message)
    res = MessageChain()
    for msg in message_json["msgChain"]:
        if msg['type']=='text':
            res += (msg['content'].strip()+"\n")
        elif msg['type']=='at':
            res += At(msg['content'])
        elif msg['type']=='reply':
            res += Reply(msg['content'])
        elif msg['type'] == 'Face':
            res += Face(msg['content'])
        elif msg['type'] == 'image':
            res += Image(msg['content'])
    return res

@bot.group_event()
async def on_group_message(msg:GroupMessage):
    group_uin = list(map(int, config['group_uin'].split(','))) # 指定群聊的账号

    if msg.group_id in group_uin:
        conversation = group_chat_chace.get(msg.group_id)
        if conversation is None:
            conversation = Conversation(maxLen=int(config['group_conversation_maxLen']))
            group_chat_chace.add(msg.group_id, conversation)

        should_reply = False
        for m in msg.message:
            if m['type']=='at' and m['data']['qq']==config['qq']:
                should_reply = True
            elif m['type']=='reply':
                reply_msg = bot.api.get_msg_sync(m['data']['id'])
                print(reply_msg)
                if reply_msg['data']['user_id']==config['qq']:
                    should_reply = True
            else:
                if random.random()<config['reply_p']:
                    should_reply = True
        prompt = f"[user_id:{msg.sender.user_id} user_name:{msg.sender.nickname} msg_id:{msg.message_id} 场景:群聊]"
        if should_reply:
            message = model.send_msg(prompt+msg.raw_message, conversation)
            if message.tool_calls is not None:
                tool = message.tool_calls[0]
                model.tools.invoke_function(tool, conversation)
                message = model.send_conversation(conversation)
            print(message)
            if message.content is not None:
                await bot.api.post_group_msg(msg.group_id, rtf=parse_message(message.content))
        else:
            conversation.append({'role':'user', 'content':prompt + msg.raw_message})

@bot.private_event()
async def on_private_message(msg:PrivateMessage):
    conversation = private_chat_chace.get(msg.sender.user_id)
    if conversation is None:
        conversation = Conversation(maxLen=int(config['private_conversation_maxLen']))
        private_chat_chace.add(msg.sender.user_id, conversation)

    prompt = f"[user_id:{msg.sender.user_id} user_name:{msg.sender.nickname} msg_id:{msg.message_id} 场景:私聊]"
    message = model.send_msg(prompt + msg.raw_message, conversation)
    if message.tool_calls is not None:
        tool = message.tool_calls[0]
        model.tools.invoke_function(tool, conversation)
        message = model.send_conversation(conversation)
    print(message)
    if message.content is not None:
        await bot.api.post_private_msg(msg.sender.user_id, rtf=parse_message(message.content))

bot.run(bt_uin=config['qq'])