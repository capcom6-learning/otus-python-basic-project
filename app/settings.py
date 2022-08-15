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

import pydantic


class MongoUrl(pydantic.AnyUrl):
    allowed_schemes = ["mongodb"]


class DatabaseSettings(pydantic.BaseModel):
    dsn: MongoUrl = pydantic.Field(
        "mongodb://localhost:27017/", description="MongoDB connection string"
    )
    database: str = pydantic.Field("wind", description="MongoDB database name")
    debug: bool = False


class Settings(pydantic.BaseSettings):
    database: DatabaseSettings

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
