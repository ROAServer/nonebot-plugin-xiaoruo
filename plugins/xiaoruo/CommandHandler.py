from typing import Type

from loguru import logger
from nonebot import Bot
from nonebot.adapters.onebot.v11 import MessageEvent
from nonebot.internal.matcher import Matcher

from .ChatEnvType import ChatEnvType
from .LLMClientHolder import LLMClientHolder


async def handle_command(
    bot: Bot,
    env: ChatEnvType,
    event: MessageEvent,
    chat: Type[Matcher],
    llm_client_holder: LLMClientHolder,
):
    if env == ChatEnvType.group:
        logger.info(f"Group[{event.group_id}] command message({event.message_id}) from ({event.sender.nickname},{event.sender.user_id}): " + text)
        current_llm = llm_client_holder.get_group_llm(event.group_id)
    elif env == ChatEnvType.private:
        logger.info(f"Private[{event.sender.user_id}({event.sender.nickname})] command message({event.message_id}): " + text)
        current_llm = llm_client_holder.get_private_llm(event.user_id)
    else:
        raise ValueError(f"Invalid chat environment: {env}.")

    command = event.get_message().extract_plain_text().split(' ')

    command.pop(0)

    if command[0] == "clear":
        command.pop(0)
        if len(command) == 0:
            current_llm.clear()
            if env == ChatEnvType.group:
                logger.info(f"Group[{event.group_id}]: Cleared llm context for group on command, by ({event.sender.nickname},{event.sender.user_id}).")
            elif env == ChatEnvType.private:
                logger.info(f"Private[{event.sender.user_id}({event.sender.nickname})]: Cleared llm context for private on command.")

            await chat.finish("Cleared command context.")
        else:
            await chat.finish("Invalid command arguments: command 'ruo-clear' does not accept any arguments.'")
    # end: ruo-clear
    else:
        await chat.finish("Invalid command.")
