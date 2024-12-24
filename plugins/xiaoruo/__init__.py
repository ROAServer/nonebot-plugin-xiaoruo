from loguru import logger
from nonebot import Bot, on_message, on_command
from nonebot.adapters.onebot.v11 import GroupMessageEvent, PrivateMessageEvent
from nonebot.plugin import PluginMetadata
from nonebot.rule import to_me

from .ChatEnvType import ChatEnvType
from .CommandHandler import handle_command
from .LLMChatHandler import handle_llm_chat
from .LLMClientHolder import LLMClientHolder
from .OMMSServerAccess import OMMSServerAccess
from .config import config, load_config, save_config
from .ContextAwareLLMClient import ContextAwareLLMClient
from .UserContext import UserContext

__plugin_meta = PluginMetadata(
    name="xiaoruo",
    description="",
    usage=""
)


command_ruo = on_command("ruo")
chat_to_me = on_message(rule=to_me())
chat = on_message()

llm_client_holder = LLMClientHolder()


@command_ruo.handle()
async def handle_chat_command_group(bot: Bot, event: GroupMessageEvent):
    await handle_command(bot, ChatEnvType.group, event, command_ruo, llm_client_holder)


@chat_to_me.handle()
async def handle_chat_to_me(bot: Bot, event: GroupMessageEvent):
    text = event.get_message().extract_plain_text().lstrip()
    if text.startswith(config.command_prompt):
        await handle_command(bot, ChatEnvType.group, event, chat_to_me, llm_client_holder)
    else:
        await handle_llm_chat(bot, ChatEnvType.group, event, chat_to_me, llm_client_holder)


@chat.handle()
async def handle_chat_group(bot: Bot, event: GroupMessageEvent):
    text = event.get_message().extract_plain_text().lstrip()
    if text.startswith(config.command_prompt):
        await handle_command(bot, ChatEnvType.group, event, chat, llm_client_holder)
    elif text.startswith("xiaoruo") or text.startswith("小若"):
        await handle_llm_chat(bot, ChatEnvType.group, event, chat, llm_client_holder)
    else:
        logger.info(f"Group[{event.group_id}] message({event.message_id}) from ({event.sender.nickname},{event.sender.user_id}) unhandled: " + text)


@command_ruo.handle()
async def handle_chat_command_private(bot: Bot, event: PrivateMessageEvent):
    await handle_command(bot, ChatEnvType.private, event, command_ruo, llm_client_holder)


@chat.handle()
async def handle_chat_private(bot: Bot, event: PrivateMessageEvent):
    text = event.get_message().extract_plain_text()
    logger.info(f"Private[{event.sender.user_id}({event.sender.nickname})] message({event.message_id}): " + text)
    if text.startswith(config.command_prompt):
        await handle_command(bot, ChatEnvType.private, event, chat, llm_client_holder)
    else:
        await handle_llm_chat(bot, ChatEnvType.private, event, chat, llm_client_holder)
