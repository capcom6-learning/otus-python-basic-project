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
from typing import List

import app.models as models
import app.repositories.stations as stations
import app.repositories.users as users
import bcrypt
import fastapi
from fastapi.security import HTTPBasic, HTTPBasicCredentials

logger = logging.getLogger(__name__)


async def get_user(
    credentials: HTTPBasicCredentials = fastapi.Depends(HTTPBasic()),
) -> users.User:
    user = await users.get(credentials.username)

    if user and bcrypt.checkpw(credentials.password.encode(), user.password.encode()):
        return user

    raise fastapi.HTTPException(
        status_code=fastapi.status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Basic"},
    )


stations_router = fastapi.APIRouter(tags=["Stations"])


@stations_router.get(
    "",
    response_model=List[models.Station],
    tags=["Stations"],
    summary="Get all stations",
)
async def station_select():
    return await stations.select()


@stations_router.get(
    "/{id}",
    summary="Get a station by id",
    response_model=models.Station,
    responses={404: {"description": "Station not found"}},
)
async def station_get(id: models.PyObjectId = fastapi.Path(..., title="Station ID")):
    station = await stations.get(id)
    if station:
        return station
    raise fastapi.HTTPException(status_code=404, detail="Station not found")


@stations_router.post(
    "",
    summary="Add a station",
    response_model=models.Station,
    responses={409: {"description": "Station already exists"}},
)
async def station_post(station: models.StationIn) -> models.Station:
    if await stations.get_by_code(station.code):
        raise fastapi.HTTPException(status_code=409, detail="Station already exists")

    return await stations.insert(models.Station(**station.dict()))


@stations_router.put(
    "/{id}",
    summary="Update a station",
    response_model=models.Station,
    responses={404: {"description": "Station not found"}},
)
async def station_put(
    id: models.PyObjectId = fastapi.Path(..., title="Station ID"),
    station: models.StationIn = fastapi.Body(..., title="Station"),
) -> models.Station:
    existed = await stations.get(id)
    if not existed:
        raise fastapi.HTTPException(status_code=404, detail="Station not found")

    existed = existed.copy(update=station.dict(exclude_unset=True))

    return await stations.update(existed)


@stations_router.delete(
    "/{id}",
    summary="Delete a station",
    status_code=204,
    responses={404: {"description": "Station not found"}},
)
async def station_delete(id: models.PyObjectId = fastapi.Path(..., title="Station ID")):
    if await stations.delete(id) == 0:
        raise fastapi.HTTPException(status_code=404, detail="Station not found")


router = fastapi.APIRouter(dependencies=[fastapi.Depends(get_user)], tags=["Admin"])
router.include_router(stations_router, prefix="/station")
