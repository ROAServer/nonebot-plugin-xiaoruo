import base64
from typing import Optional, Any

import aiohttp
from loguru import logger


class OMMSServerAccess:
    def __init__(self, server_http_address: str, api_key: str):
        self.server_http_address = server_http_address
        self.api_key = api_key

    # 使用aiohttp对服务器发送请求并接受回复
    @logger.catch(level='ERROR', reraise=True)
    async def request(self, endpoint: str, method: str, data: Optional[dict] = None) -> tuple[int, Any]:
        auth = base64.b64encode(f'xiaoruo:{self.api_key}'.encode()).decode()
        async with aiohttp.ClientSession() as session:
            async with session.request(
                    method,
                    self.server_http_address + endpoint,
                    headers={
                        'Authorization': 'Basic ' + auth
                    },
                    json=data
            ) as response:
                if response.status == 401:
                    return 401, None
                return response.status, await response.json()

    # 获取白名单列表
    async def whitelist_add(self, whitelist_name: str, player_name: str):
        status, resp = await self.request("/api/whitelist/add", "POST", {
            "whitelistName": whitelist_name,
            "playerName": player_name
        })
        if status == 401:
            return "api.configure_failure.auth_with_server_failed"
        return resp

    async def whitelist_remove(self, whitelist_name: str, player_name: str):
        status, resp = await self.request("/api/whitelist/remove", "POST", {
            "whitelistName": whitelist_name,
            "playerName": player_name
        })
        if status == 401:
            return "api.configure_failure.auth_with_server_failed"
        return resp

    async def whitelist_list(self):
        status, resp = await self.request("/api/whitelist/list", "GET")
        if status == 401:
            return "api.configure_failure.auth_with_server_failed"
        return resp

