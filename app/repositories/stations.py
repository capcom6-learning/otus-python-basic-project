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

from typing import List, Union
from app.database import db
from app.models import PyObjectId, Station

collection = db.stations


async def select() -> List[Station]:
    """Select all stations"""
    stations = await collection.find({}).to_list(None)
    return [Station(**station) for station in stations]


async def get(id: PyObjectId) -> Union[Station, None]:
    """Get a station by id"""
    station = await collection.find_one({"_id": id})
    if station:
        return Station(**station)
    return None


async def get_by_code(code: str) -> Union[Station, None]:
    """Get a station by code"""
    station = await collection.find_one({"code": code})
    if station:
        return Station(**station)
    return None


async def insert(station: Station) -> Station:
    """Add a station"""
    await collection.insert_one(station.dict(by_alias=True))

    return station


async def update(station: Station) -> Station:
    """Update a station"""
    await collection.update_one(
        {"_id": station.id}, {"$set": station.dict(by_alias=True)}
    )

    return station


async def delete(id: PyObjectId):
    """Delete a station"""
    await collection.delete_one({"_id": id})
