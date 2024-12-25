from typing import Type

from loguru import logger
from nonebot import Bot
from nonebot.adapters.onebot.v11 import MessageEvent
from nonebot.internal.matcher import Matcher

from .config import config
from .ChatEnvType import ChatEnvType
from .LLMClientHolder import LLMClientHolder


async def handle_command(
    bot: Bot,
    env: ChatEnvType,
    event: MessageEvent,
    chat: Type[Matcher],
    llm_client_holder: LLMClientHolder,
):
    text = event.get_message().extract_plain_text().lstrip()
    if env == ChatEnvType.group:
        logger.info(f"Group[{event.group_id}] command message({event.message_id}) from ({event.sender.nickname},{event.sender.user_id}): " + text)
        current_llm = llm_client_holder.get_group_llm(event.group_id)
    elif env == ChatEnvType.private:
        logger.info(f"Private[{event.sender.user_id}({event.sender.nickname})] command message({event.message_id}): " + text)
        current_llm = llm_client_holder.get_private_llm(event.user_id)
    else:
        raise ValueError(f"Invalid chat environment: {env}.")

    command = text.split(' ')

    if command.pop(0).removeprefix('/') != config.command_root: return

    if len(command) == 0:
        return
    elif command[0] in ["help", "?", "？"]:
        await chat.finish(
            f"Command list:\n"
            f"/{config.command_root} clear: Clear llm context."
        )
    # end: help
    elif command[0] == "clear":
        command.pop(0)
        if len(command) == 0:
            current_llm.clear()
            if env == ChatEnvType.group:
                logger.info(f"Group[{event.group_id}] Cleared llm context for group on command, by ({event.sender.nickname},{event.sender.user_id}).")
            elif env == ChatEnvType.private:
                logger.info(f"Private[{event.sender.user_id}({event.sender.nickname})] Cleared llm context for private on command.")

            await chat.finish("Cleared command context.")
        else:
            await chat.finish(f"Invalid command arguments: command '/{config.command_root} clear' does not accept any arguments.'")
    # end: ruo-clear
