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

import logging
import motor.motor_asyncio as motor
from app.settings import config

logger = logging.getLogger(__name__)

client = motor.AsyncIOMotorClient(config.database.dsn)
db = client[config.database.database]


async def init():
    server_info = await client.server_info()
    server_version = server_info["version"].split(".")
    logger.info(f"Connected to MongoDB {server_info['version']}")

    collections = set(await db.list_collection_names())

    if "users" not in collections:
        await db.create_collection("users")
        await db.users.create_index([("name", 1)], unique=True)

    if "stations" not in collections:
        await db.create_collection("stations")
        await db.stations.create_index([("code", 1)], unique=True)

    if "measurements" not in collections:
        options = (
            {
                "timeseries": {
                    "timeField": "timestamp",
                    "metaField": "station",
                    "granularity": "minutes",
                }
            }
            if int(server_version[0]) >= 5
            else {}
        )
        await db.create_collection("measurements", **options)
        await db.measurements.create_index([("station._id", 1), ("timestamp", -1)])
