class Conversation:
    messages = []
    maxLen = None

    def __init__(self, maxLen=None):
        if maxLen == 0:
            raise ValueError("maxLen不能为0")
        self.maxLen = maxLen

    def __len__(self):
        return len(self.messages)

    def append(self, msg):
        if self.maxLen and self.maxLen>0 and len(self.messages)==self.maxLen:
            if self.messages[0]["role"]=='system':
                self.messages.pop(1)
            else:
                self.messages.pop(0)
        self.messages.append(msg)

    def getHistoryMsgs(self):
        return self.messages

    def clear(self):
        self.messages.clear()

class ChatCache:
    cache = None

    def add(self, key, conversation:Conversation):
        pass

    def remove(self, key):
        pass

    def get(self, key):
        pass


class ChatMemory(ChatCache):
    def __init__(self):
        self.cache = dict()

    def add(self, key, conversation: Conversation):
        self.cache[key] = conversation

    def remove(self, key):
        return self.cache.pop(key)

    def get(self, key):
        return self.cache.get(key, None)