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

import pymongo
from typing import List, Union
from app.database import db
from app.models import PyObjectId, Station, WeatherRecord

collection = db.measurements


async def select_last() -> List[WeatherRecord]:
    """Select last weather records grouped by station"""
    records = await collection.aggregate(
        [
            {"$group": {"_id": "$station._id", "record": {"$last": "$$ROOT"}}},
            {"$sort": {"record.timestamp": pymongo.DESCENDING}},
            {"$project": {"_id": 0, "record": 1}},
        ]
    ).to_list(None)
    return [WeatherRecord(**record) for record in records]


async def get_last(station_id: PyObjectId) -> Union[WeatherRecord, None]:
    """Get last weather record for a station"""
    record = await collection.find_one(
        {"station._id": station_id}, sort=[("timestamp", pymongo.DESCENDING)]
    )
    if record:
        return WeatherRecord(**record)
    return None


async def insert(record: WeatherRecord) -> WeatherRecord:
    """Add a weather record"""
    await collection.insert_one(record.dict(by_alias=True))

    return record
