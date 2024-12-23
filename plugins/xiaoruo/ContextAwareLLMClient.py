from datetime import datetime
from typing import List, Dict

from .LLMClient import LLMClient


def _get_current_time():
    now = datetime.now()
    current_time = now.strftime("%Y-%m-%d %H:%M:%S")
    return current_time


class ContextAwareLLMClient(LLMClient):
    def __init__(self):
        super().__init__()
        self.context = super().get_context()

    def get_context(self) -> List[Dict[str, str]]:
        return self.context

    def get_system_prompt(self):
        return "当前时间：" + _get_current_time() + "\n" + super().get_system_prompt()

    def clear(self):
        self.context = super().get_context()
