from typing import List

from pydantic import BaseModel, Field


class Config(BaseModel):
    """Plugin Config Here"""
    api_key: str = Field(default="API_KEY_HERE")
    model: str = Field(default="moonshot-v1-8k")
    valid_scenes: List[int] = Field(default=[])
    ops: List[int] = Field(default=[])
    omms_server_http_address: str = Field(default="http://localhost:50001")
    omms_api_key: str = Field(default="OMMS_API_KEY_HERE")
    command_root: str = Field(default="ruo")
