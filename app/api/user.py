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

import enum
from io import BytesIO
import logging
from typing import List, Union

import app.repositories.stations as stations
import app.repositories.measurements as measurements
import fastapi
import starlette.responses as responses
import matplotlib.pyplot as plt
import app.models as models

logger = logging.getLogger(__name__)

router = fastapi.APIRouter(tags=["User"])


class RequestType(str, enum.Enum):
    LAST = "last"
    FORECAST = "forecast"
    HISTORY = "history"


@router.get(
    "/station",
    response_model=List[models.Station],
    summary="Get all stations",
    tags=["Stations"],
)
async def station_select():
    return await stations.select()


# ObjectId("62fa1796810616013f7f7b19")
@router.get(
    "/station/{id}/weather",
    summary="Get weather for a station",
    tags=["Stations", "Weather"],
    responses={
        200: {
            "model": Union[
                models.AnonymousWeatherRecord, List[models.AnonymousWeatherRecord]
            ]
        },
        400: {"description": "Invalid request"},
        404: {"description": "Data not found"},
        501: {"description": "Not implemented"},
    },
)
async def weather_get(
    id: models.PyObjectId = fastapi.Path(..., title="Station ID"),
    type: RequestType = fastapi.Query(RequestType.LAST, title="Request type"),
    period: models.Period = fastapi.Depends(models.Period),
):
    if type == RequestType.LAST:
        measure = await measurements.get_last(id)
        if measure:
            return models.AnonymousWeatherRecord(**measure.dict(by_alias=True))
        raise fastapi.HTTPException(404, "No weather record found")

    if type == RequestType.FORECAST:
        raise fastapi.HTTPException(501, "Not implemented")

    if type == RequestType.HISTORY:
        records = await measurements.select(id, period, samples=100)
        return [
            models.AnonymousWeatherRecord(**record.dict(by_alias=True))
            for record in records
        ]

    raise fastapi.HTTPException(400, "Invalid request type")


@router.get(
    "/station/{id}/{param}/graph",
    summary="Get graph for a station",
    tags=["Stations", "Weather"],
    responses={
        200: {"content": {"image/png": {}}, "description": "OK"},
        400: {"description": "Invalid request"},
    },
)
async def weather_graph(
    id: models.PyObjectId = fastapi.Path(..., title="Station ID"),
    param: models.MeasureType = fastapi.Path(..., title="Parameter"),
    period: models.Period = fastapi.Depends(models.Period),
    width: int = fastapi.Query(640, title="Width", gt=320, le=1920),
    height: int = fastapi.Query(480, title="Height", gt=240, le=1080),
):
    records = await measurements.select(id, period, samples=width)
    x = [record.timestamp for record in records]
    y = [getattr(record, param.value).avg for record in records]

    fig, ax = plt.subplots()
    ax.plot(x, y)
    # ax.set_title(str(param))
    # ax.set_xlabel("Time")
    # ax.set_ylabel(str(param))
    fig.set_size_inches(width / 100, height / 100)
    fig.set_dpi(100)
    fig.tight_layout()
    fig.canvas.draw()
    buf = BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    plt.close(fig)

    return responses.StreamingResponse(buf, media_type="image/png")
