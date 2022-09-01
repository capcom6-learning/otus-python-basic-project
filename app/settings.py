# Copyright 2022 Aleksandr Soloshenko
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
from typing import Any, Dict, Tuple

import dotenv
import pydantic
import yaml
from pydantic.env_settings import SettingsSourceCallable

dotenv.load_dotenv()


def yaml_config_settings_source(settings: pydantic.BaseSettings) -> Dict[str, Any]:
    """
    A simple settings source that loads variables from a JSON file
    at the project's root.

    Here we happen to choose to use the `env_file_encoding` from Config
    when reading `config.json`
    """
    encoding = settings.__config__.env_file_encoding
    filename = os.environ.get("CONFIG_FILE", "config.yml")
    if not os.path.exists(filename):
        return {}

    with open(filename, encoding=encoding) as f:
        return yaml.safe_load(f)


class MongoUrl(pydantic.AnyUrl):
    allowed_schemes = ["mongodb"]


class CommonSettings(pydantic.BaseModel):
    debug: bool = False


class DatabaseSettings(pydantic.BaseModel):
    dsn: MongoUrl = pydantic.Field(
        "mongodb://localhost:27017/", description="MongoDB connection string"
    )
    database: str = pydantic.Field("wind", description="MongoDB database name")
    debug: bool = False


class Settings(pydantic.BaseSettings):
    common: CommonSettings = CommonSettings()
    database: DatabaseSettings = DatabaseSettings()  # type: ignore

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        env_nested_delimiter = "__"

        @classmethod
        def customise_sources(
            cls,
            init_settings: SettingsSourceCallable,
            env_settings: SettingsSourceCallable,
            file_secret_settings: SettingsSourceCallable,
        ) -> Tuple[SettingsSourceCallable, ...]:
            return (
                init_settings,
                yaml_config_settings_source,
                env_settings,
                file_secret_settings,
            )


config = Settings()
