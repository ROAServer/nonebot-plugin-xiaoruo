from typing import Any

from loguru import logger

from . import config


def _whitelist_operation_impl(action: str, whitelist_name: str, player_name: str):
    logger.debug(f"LLM Called whitelist_operation({action}, {whitelist_name}, {player_name})")
    if action == "ADD":
        return "failure.whitelist.player_exists"
    if action == "REMOVE":
        return "SUCCESS"

def _check_operator_impl(username:str):
    ops = [str(e) for e in config.ops]
    if username in ops:
        return True
    return False


class FunctionManager:
    __all = {
        "whitelist_operation": _whitelist_operation_impl,
        "check_operator": _check_operator_impl
    }

    __tools = [
        {
            "type": "function",  # 约定的字段 type，目前支持 function 作为值
            "function": {  # 当 type 为 function 时，使用 function 字段定义具体的函数内容
                "name": "whitelist_operation",  # 函数的名称，请使用英文大小写字母、数据加上减号和下划线作为函数名称
                "description": """ 
				通过OMMS Central Server管理服务器白名单，当用户要求你为某人添加白名单或移除白名单时，调用此工具。
				请从用户的对话中提取内容作为action,whitelist_name,player_name的值。你需要将此函数的执行结果通过文字简要的转达。
				这个工具是要求管理员权限的，请在调用之前使用check_operator工具检查用户是否有权限进行操作。
			""",  # 函数的介绍，在这里写上函数的具体作用以及使用场景，以便 Kimi 大模型能正确地选择使用哪些函数
                "parameters": {  # 使用 parameters 字段来定义函数接收的参数
                    "type": "object",  # 固定使用 type: object 来使 Kimi 大模型生成一个 JSON Object 参数
                    "required": ["action", "whitelist_name", "player_name"],  # 使用 required 字段告诉 Kimi 大模型哪些参数是必填项
                    "properties": {  # properties 中是具体的参数定义，你可以定义多个参数
                        "action": {  # 在这里，key 是参数名称，value 是参数的具体定义
                            "type": "string",  # 使用 type 定义参数类型
                            "description": """
							用户要执行的操作，有ADD,REMOVE两种值，请从上下文中决定
						"""  # 使用 description 描述参数以便 Kimi 大模型更好地生成参数
                        },
                        "whitelist_name": {  # 在这里，key 是参数名称，value 是参数的具体定义
                            "type": "string",  # 使用 type 定义参数类型
                            "description": """
							要被操作的白名单，请从上下文中提取
						"""  # 使用 description 描述参数以便 Kimi 大模型更好地生成参数
                        },
                        "player_name": {  # 在这里，key 是参数名称，value 是参数的具体定义
                            "type": "string",  # 使用 type 定义参数类型
                            "description": """
							要被添加或移除的玩家名，请从上下文中提取
						"""  # 使用 description 描述参数以便 Kimi 大模型更好地生成参数
                        }
                    }
                }
            }
        },
        {
            "type": "function",  # 约定的字段 type，目前支持 function 作为值
            "function": {  # 当 type 为 function 时，使用 function 字段定义具体的函数内容
                "name": "check_operator",  # 函数的名称，请使用英文大小写字母、数据加上减号和下划线作为函数名称
                "description": """ 
    				在用户请求任何要求管理员权限的操作前，检查用户是否有权限进行操作，如果有权限返回True，否则返回False
    				如果权限检查失败，则应该告知用户权限不足，不应该执行任何操作
    			""",  # 函数的介绍，在这里写上函数的具体作用以及使用场景，以便 Kimi 大模型能正确地选择使用哪些函数
                "parameters": {  # 使用 parameters 字段来定义函数接收的参数
                    "type": "object",  # 固定使用 type: object 来使 Kimi 大模型生成一个 JSON Object 参数
                    "required": ["username"],  # 使用 required 字段告诉 Kimi 大模型哪些参数是必填项
                    "properties": {  # properties 中是具体的参数定义，你可以定义多个参数
                        "username": {  # 在这里，key 是参数名称，value 是参数的具体定义
                            "type": "string",  # 使用 type 定义参数类型
                            "description": """
    							用户的用户id，会在每条消息中告知，请自行提取
    						"""  # 使用 description 描述参数以便 Kimi 大模型更好地生成参数
                        }
                    }
                }
            }
        }
    ]

    def __init__(self):
        pass

    @logger.catch(level='ERROR', reraise=True)
    def invoke(self, name: str, **kwargs) -> Any:
        return self.__all[name](**kwargs)

    @property
    def tools(self):
        return self.__tools


__functions = FunctionManager()

def functions():
    return __functions
