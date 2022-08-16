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

from typing import List
import fastapi
import bcrypt
import logging
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from app.models import PyObjectId, Station

import app.repositories.users as users
import app.repositories.stations as stations

logger = logging.getLogger(__name__)


async def get_user(
    credentials: HTTPBasicCredentials = fastapi.Depends(HTTPBasic()),
) -> users.User:
    user = await users.get(credentials.username)

    if user and bcrypt.checkpw(credentials.password.encode(), user.password.encode()):
        return user

    raise fastapi.HTTPException(
        status_code=fastapi.status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect email or password",
        headers={"WWW-Authenticate": "Basic"},
    )


stations_router = fastapi.APIRouter(tags=["Stations"])


@stations_router.get(
    "", response_model=List[Station], tags=["Stations"], summary="Get all stations"
)
async def station_select():
    return await stations.select()


@stations_router.get(
    "/{id}",
    summary="Get a station by id",
    response_model=Station,
    responses={404: {"description": "Station not found"}},
)
async def station_get(id: PyObjectId = fastapi.Path(..., title="Station ID")):
    station = await stations.get(id)
    if station:
        return station
    raise fastapi.HTTPException(status_code=404, detail="Station not found")


@stations_router.post(
    "",
    summary="Add a station",
    response_model=Station,
    responses={409: {"description": "Station already exists"}},
)
async def station_post(station: Station) -> Station:
    if await stations.get_by_code(station.code):
        raise fastapi.HTTPException(status_code=409, detail="Station already exists")

    return await stations.insert(station)


@stations_router.put(
    "/{id}",
    summary="Update a station",
    response_model=Station,
    responses={404: {"description": "Station not found"}},
)
async def station_put(
    id: PyObjectId = fastapi.Path(..., title="Station ID"),
    station: Station = fastapi.Body(..., title="Station"),
) -> Station:
    if not await stations.get(id):
        raise fastapi.HTTPException(status_code=404, detail="Station not found")

    station.id = id
    return await stations.update(station)


@stations_router.delete(
    "/{id}",
    summary="Delete a station",
    status_code=204,
    responses={404: {"description": "Station not found"}},
)
async def station_delete(id: PyObjectId = fastapi.Path(..., title="Station ID")):
    if await stations.delete(id) == 0:
        raise fastapi.HTTPException(status_code=404, detail="Station not found")


router = fastapi.APIRouter(dependencies=[fastapi.Depends(get_user)], tags=["Admin"])
router.include_router(stations_router, prefix="/station")
