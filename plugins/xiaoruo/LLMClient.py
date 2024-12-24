import json
from typing import Optional, List, Dict

from loguru import logger
from openai import OpenAI

from . import config
from .Constants import SYSTEM_PROMPT
from .FunctionManager import functions


class LLMClient(object):
    def __init__(self):
        self.client = OpenAI(
            api_key=config.api_key,
            base_url="https://api.moonshot.cn/v1",
        )

    def get_system_prompt(self):
        return SYSTEM_PROMPT

    def get_context(self) -> List[Dict[str, str]]:
        return [
            {
                "role": "system",
                "content": self.get_system_prompt()
            }
        ]

    async def chat(self, input: str) -> Optional[str]:
        logger.info(f"LLMClient.chat({input})")
        context = self.get_context()
        logger.debug(f"Context: {context}")
        context.append(
            {
                "role": "user",
                "content": input,
            }
        )
        finish_reason = None
        completion = None
        while finish_reason is None or finish_reason == "tool_calls":
            completion = self.client.chat.completions.create(
                model=config.model,
                messages=context,
                temperature=0.3,
                tools=functions().tools
            )
            choice = completion.choices[0]
            finish_reason = choice.finish_reason
            if finish_reason == "tool_calls":
                context.append(choice.message)
                for tool_call in choice.message.tool_calls:
                    tool_call_name = tool_call.function.name
                    logger.debug(
                        "Called tools " + tool_call.function.name + " with arguments " + tool_call.function.arguments)
                    tool_call_arguments = json.loads(
                        tool_call.function.arguments
                    )
                    try:
                        tool_result = await functions().invoke(tool_call_name, **tool_call_arguments)
                        context.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "name": tool_call_name,
                            "content": json.dumps(tool_result),
                        })
                    except Exception as e:
                        context.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "name": tool_call_name,
                            "content": "An exception was thrown while running tools." + str(e),
                        })
        assistant_message = completion.choices[0].message
        context.append(assistant_message)
        if completion:
            usage = completion.usage
            logger.debug(f"chat_prompt_tokens:          {usage.prompt_tokens}")
            logger.debug(f"chat_completion_tokens:      {usage.completion_tokens}")
            logger.debug(f"chat_total_tokens:           {usage.total_tokens}")
        return assistant_message.content
