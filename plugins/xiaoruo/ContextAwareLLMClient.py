from typing import List, Dict

from .LLMClient import LLMClient
from .utils import get_current_time


class ContextAwareLLMClient(LLMClient):
    def __init__(self, group_id: int):
        super().__init__()
        self.group_id = group_id
        self.context = super().get_context()

    def get_context(self) -> List[Dict[str, str]]:
        return self.context

    def get_system_prompt(self):
        return f"""当前时间：{get_current_time()}，当前场景id：{self.group_id}

{super().get_system_prompt()}
        """

    def clear(self):
        self.context = super().get_context()
