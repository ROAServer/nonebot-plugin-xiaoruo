from typing import Type

from loguru import logger
from nonebot import Bot
from nonebot.adapters.onebot.v11 import MessageEvent
from nonebot.internal.matcher import Matcher
from openai import RateLimitError

from .UserContext import UserContext
from .ChatEnvType import ChatEnvType
from .LLMClientHolder import LLMClientHolder
from .config import config


async def handle_llm_chat(
    bot: Bot,
    env: ChatEnvType,
    event: MessageEvent,
    chat: Type[Matcher],
    llm_client_holder: LLMClientHolder,
):
    if env == ChatEnvType.group:
        logger.info(f"Group[{event.group_id}] message({event.message_id}) pass to llm.")
        current_llm = await llm_client_holder.get_group_llm(event.group_id)
    elif env == ChatEnvType.private:
        logger.info(f"Private[{event.sender.user_id}({event.sender.nickname})] message({event.message_id}) pass to llm.")
        current_llm = await llm_client_holder.get_private_llm(event.user_id)
    else:
        raise ValueError(f"Invalid chat environment: {env}.")

    text = event.get_message().extract_plain_text()

    try:
        if message := await current_llm.chat(
                UserContext(event.user_id, event.sender.nickname),
                f"{{用户id:{event.user_id},用户称呼：{event.sender.nickname}}}" + text
        ):
            await chat.finish(message)
    except RateLimitError as e:
        await chat.finish("Rate limit exceeded.")