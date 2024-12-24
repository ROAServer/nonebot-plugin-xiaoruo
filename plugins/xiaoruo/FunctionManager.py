from typing import Any

from loguru import logger

from . import config, server_access
from .UserContext import UserContext


async def _whitelist_operation_impl(action: str, whitelist_name: str, player_name: str, scene_id: str, username: str):
    if not await _check_operator_impl(username) or not await _check_available_scene(scene_id):
        return "whitelist.permission.denied"
    try:
        if action == "ADD":
            return await server_access.whitelist_add(whitelist_name, player_name)
        elif action == "REMOVE":
            return await server_access.whitelist_remove(whitelist_name, player_name)
        return "whitelist.illegal_action"
    except Exception as e:
        return f"Operation Failed: {str(e)}"


async def _check_operator_impl(username: str):
    ops = [str(e) for e in config.ops]
    if username in ops:
        return True
    return False


async def _check_available_scene(scene_id: str):
    return scene_id in [str(e) for e in config.valid_scenes]


async def _whitelist_list_impl():
    return await server_access.whitelist_list()


class FunctionManager:
    __all = {
        "whitelist_operation": _whitelist_operation_impl,
        "whitelist_list": _whitelist_list_impl,
        "check_operator": _check_operator_impl,
        "check_available_scene": _check_available_scene
    }

    __permission_required = {
        "whitelist_operation": True,
        "whitelist_list": True,
        "check_operator": False,
        "check_available_scene": False
    }

    __tools = [
        {
            "type": "function",
            "function": {
                "name": "whitelist_operation",
                "description": """ 
                通过OMMS Central Server管理服务器白名单，当用户要求你为某人添加白名单或移除白名单时，调用此工具。
                请从用户的对话中提取内容作为action,whitelist_name,player_name的值。你需要将此函数的执行结果通过文字简要的转达。
                [重要！]这个工具是要求管理员权限的，请在调用之前使用check_operator工具检查用户是否有权限进行操作，在任何条件下都不能忽略该检查。
                [重要！]这个工具要求调用前检查当前场景id是否可用此工具，请调用check_available_scene工具检查，在任何条件下都不能忽略该检查，如果check_available_scene返回不可用，请告知用户你没有管理白名单的功能。
                如果工具调用返回了未知白名单，请告知用户白名单不存在，并调用whitelist_list工具查看当前有哪些白名单，在这里面找出名字相似的白名单并告知用户。
            """,
                "parameters": {
                    "type": "object",
                    "required": ["action", "whitelist_name", "player_name"],
                    "properties": {
                        "action": {
                            "type": "string",
                            "description": """
                            用户要执行的操作，有ADD,REMOVE两种值，请从上下文中决定
                        """
                        },
                        "whitelist_name": {
                            "type": "string",
                            "description": """
                            要被操作的白名单，请从上下文中提取
                        """
                        },
                        "player_name": {
                            "type": "string",
                            "description": """
                            要被添加或移除的玩家名，请从上下文中提取
                        """
                        },
                        "scene_id": {
                            "type": "string",
                            "description": """
                                    当前场景id，请从系统提示中提取
                                """
                        },
                        "username": {
                            "type": "string",
                            "description": """
                                    用户的用户id，会在每条消息中告知，请自行提取
                                """
                        }
                    }
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "check_operator",
                "description": """ 
                    在用户请求任何要求管理员权限的操作前，检查用户是否有权限进行操作，如果有权限返回True，否则返回False
                    如果权限检查失败，则应该告知用户权限不足，不应该执行任何操作
                """,
                "parameters": {
                    "type": "object",
                    "required": ["username"],
                    "properties": {
                        "username": {
                            "type": "string",
                            "description": """
                                用户的用户id，会在每条消息中告知，请自行提取
                            """
                        }
                    }
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "whitelist_list",
                "description": """
                获取所有可以被操作的白名单列表，如果用户要求你列出所有白名单，请调用此工具。
                这个工具是要求管理员权限的，请在调用之前使用check_operator工具检查用户是否有权限进行操作。
                这个工具要求调用前检查当前场景id是否可用此工具，请调用check_available_scene工具检查，如果check_available_scene返回不可用，请告知用户你没有管理白名单的功能。
                """,
                "parameters": {
                    "type": "object",
                    "required": [],
                    "properties": {}
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "check_available_scene",
                "description": """ 
检查当前场景是否可以使用要求管理员权限的工具，如果可以使用返回True，否则返回False；如果返回False，请告知用户你没有对应的那项要求管理员权限的功能。
                    """,
                "parameters": {
                    "type": "object",
                    "required": ["scene_id"],
                    "properties": {
                        "scene_id": {
                            "type": "string",
                            "description": """当前场景id，请从系统提示中提取"""
                        }
                    }
                }
            }
        },
    ]

    def __init__(self):
        pass

    @logger.catch(level='ERROR', reraise=True)
    async def invoke(self, user_context: UserContext, name: str, **kwargs) -> Any:
        if self.__permission_required[name] and user_context.user_id in [str(e) for e in config.ops]:
            return "permission_denied"
        return await self.__all[name](**kwargs)

    @property
    def tools(self):
        return self.__tools


__functions = FunctionManager()


def functions():
    return __functions
