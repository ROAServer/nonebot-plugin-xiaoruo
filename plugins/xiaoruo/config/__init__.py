import json
import os
import shutil

import toml
from loguru import logger
from pydantic import ValidationError

from .Config import Config
from ..utils.TomlMultiLineStringEncoder import TomlMultiLineStringEncoder


def save_config(config_data: Config, file_path: str = 'xiaoruo.toml'):
    with open(file_path, 'w', encoding="utf-8") as file:
        file.write(toml.dumps(config_data.model_dump(), encoder=TomlMultiLineStringEncoder()))


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


config = load_config()
logger.info("Config loaded: " + str(config))

save_config(config)
