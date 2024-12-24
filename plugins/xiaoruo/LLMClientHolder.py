from .ContextAwareLLMClient import ContextAwareLLMClient


class LLMClientHolder:
    def __init__(self):
        self.group_llms = {}
        self.private_llms = {}


    def get_group_llm(self, group_id: int):
        if group_id not in self.group_llms:
            self.group_llms[group_id] = ContextAwareLLMClient(group_id=group_id)
        return self.group_llms[group_id]


    def get_private_llm(self, user_id: int):
        if user_id not in self.private_llms:
            self.private_llms[user_id] = ContextAwareLLMClient(group_id=user_id)
        return self.private_llms[user_id]
