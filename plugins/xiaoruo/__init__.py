import json
import os
import shutil

import toml
from loguru import logger
from nonebot import Bot, on_message
from nonebot.adapters.onebot.v11 import GroupMessageEvent, PrivateMessageEvent
from nonebot.plugin import PluginMetadata
from openai import RateLimitError
from pydantic import ValidationError

from .Config import Config
from .OMMSServerAccess import OMMSServerAccess
from .TomlMultiLineStringEncoder import TomlMultiLineStringEncoder

__plugin_meta = PluginMetadata(
    name="xiaoruo",
    description="",
    usage=""
)


def load_config(file_path: str = 'xiaoruo.toml'):
    if not os.path.exists(file_path):
        logger.info("Creating default config.")
        c = Config()
        save_config(c)
        return c

    try:
        with open(file_path, 'r', encoding="utf-8") as file:
            data = toml.load(file)
            return Config.model_validate(data)
    except (json.JSONDecodeError, TypeError, ValueError, ValidationError) as e:
        logger.error("Load config failed." + str(e))
        backup_path = f"{file_path}.backup"
        logger.info(f"Creating backup for invalid config: {backup_path}")
        shutil.copyfile(file_path, backup_path)
        c = Config()
        save_config(c)
        return c


def save_config(config: Config, file_path: str = 'xiaoruo.toml'):
    with open(file_path, 'w', encoding="utf-8") as file:
        file.write(toml.dumps(config.model_dump(), encoder=TomlMultiLineStringEncoder()))


config = load_config()
logger.info("Config loaded: " + str(config))
save_config(config)
server_access = OMMSServerAccess(config.omms_server_http_address, config.omms_api_key)

from .ContextAwareLLMClient import ContextAwareLLMClient

chat = on_message()

group_llms = {}
private_llms = {}


def get_group_llm(group_id: int):
    if group_id not in group_llms:
        group_llms[group_id] = ContextAwareLLMClient(group_id=group_id)
    return group_llms[group_id]


def get_private_llm(user_id: int):
    if user_id not in private_llms:
        private_llms[user_id] = ContextAwareLLMClient(group_id=user_id)
    return private_llms[user_id]


@chat.handle()
async def handle_chat_group(bot: Bot, event: GroupMessageEvent):
    text = event.get_message().extract_plain_text()
    logger.info(f"Group[{event.group_id}] message from ({event.sender.nickname},{event.sender.user_id}): " + text)
    current_llm = get_group_llm(event.group_id)
    if text.endswith("/ruo-clear") and event.sender.user_id in config.ops:
        current_llm.clear()
        await chat.finish("Cleared command context for this group.")
        return
    if text.startswith("xiaoruo") or text.startswith("小若"):
        text = text.replace("xiaoruo", "").replace("小若", "")
        try:
            if message := await current_llm.chat(f"{{用户id:{event.user_id},用户称呼：{event.sender.nickname}}}" + text):
                await chat.finish(message)
        except RateLimitError as e:
            await chat.finish("Rate limit exceeded.")


@chat.handle()
async def handle_chat_private(bot: Bot, event: PrivateMessageEvent):
    current_llm = get_private_llm(event.user_id)
    text = event.get_message().extract_plain_text()
    logger.info(f"Private message from ({event.sender.nickname},{event.sender.user_id}): " + text)
    if text.endswith("/ruo-clear"):
        current_llm.clear()
        await chat.finish("Cleared command context for this group.")
        return
    try:
        if message := await current_llm.chat(f"{{用户id:{event.user_id},用户称呼：{event.sender.nickname}}}" + text):
            await chat.finish(message)
    except RateLimitError as e:
        await chat.finish("Rate limit exceeded.")
