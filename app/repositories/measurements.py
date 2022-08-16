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

from datetime import datetime, time
from typing import List, Union

import app.models as models
import pymongo
from app.database import db

collection = db.measurements


async def select_last() -> List[models.WeatherRecord]:
    """Select last weather records grouped by station"""
    records = await collection.aggregate(
        [
            {"$group": {"_id": "$station._id", "record": {"$last": "$$ROOT"}}},
            {"$sort": {"record.timestamp": pymongo.DESCENDING}},
            {"$replaceRoot": {"newRoot": "$record"}},
        ]
    ).to_list(None)
    return [models.WeatherRecord(**record) for record in records]


async def get_last(station_id: models.PyObjectId) -> Union[models.WeatherRecord, None]:
    """Get last weather record for a station"""
    record = await collection.find_one(
        {"station._id": station_id}, sort=[("timestamp", pymongo.DESCENDING)]
    )
    if record:
        return models.WeatherRecord(**record)
    return None


async def insert(record: models.WeatherRecord) -> models.WeatherRecord:
    """Add a weather record"""
    await collection.insert_one(record.dict(by_alias=True))

    return record


async def select(
    station_id: models.PyObjectId,
    period: models.Period,
    *,
    samples: Union[int, None] = None,
) -> List[models.WeatherRecord]:
    """Select weather records for a station"""
    query = [
        {
            "$match": {
                "station._id": station_id,
                "timestamp": {
                    "$gte": datetime.combine(period.start, time.min)
                    if not period.start is None
                    else datetime.min,
                    "$lte": datetime.combine(period.end, time.max)
                    if not period.end is None
                    else datetime.max,
                },
            }
        },
    ]
    if samples:
        query.append({"$sample": {"size": samples}})

    records = await collection.aggregate(
        query + [{"$sort": {"timestamp": pymongo.ASCENDING}}]
    ).to_list(None)

    return [models.WeatherRecord(**record) for record in records]
