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

from datetime import datetime, tzinfo
import pytz
import pydantic
import fastapi

from app.models import AnonymousWeatherRecord, WindValue, MeasureValue
from app.tasks import import_data

# /weatherstation/updateweatherstation.php?
# ID=IKRASN19&
# PASSWORD=w7M65w96&
# intemp=21.4&
# outtemp=17.7&
# dewpoint=9.1&
# windchill=17.7&
# inhumi=50&
# outhumi=57&
# windspeed=12.8&
# windgust=14.3&
# winddir=253&
# absbaro=966.2&
# relbaro=1007.5&
# rainrate=0.0&
# dailyrain=0.0&
# weeklyrain=0.0&
# monthlyrain=3.9&
# yearlyrain=99.9&
# light=19982.0&
# UV=415&
# dateutc=2022-8-15%2010:59:8&
# softwaretype=HP2000%20V2.5.1&
# action=updateraw&
# realtime=1&
# rtfreq=5

router = fastapi.APIRouter(
    prefix="/weatherstation/updateweatherstation.php",
    tags=["Drivers", "PWS"],
)


class RawData(pydantic.BaseModel):
    ID: str
    PASSWORD: str
    intemp: float
    outtemp: float
    dewpoint: float
    windchill: float
    inhumi: float
    outhumi: float
    windspeed: float
    windgust: float
    winddir: float
    absbaro: float
    relbaro: float
    rainrate: float
    dailyrain: float
    weeklyrain: float
    monthlyrain: float
    yearlyrain: float
    light: float
    UV: float
    dateutc: datetime
    softwaretype: str
    action: str
    rtfreq: int
    realtime: int


@router.get("", status_code=201, description="Process data in PWS format")
async def process(data: RawData = fastapi.Depends(RawData)):
    record = AnonymousWeatherRecord(
        timestamp=data.dateutc.replace(tzinfo=pytz.utc),
        wind=WindValue(
            avg=data.windspeed,
            min=None,
            max=data.windgust,
            azimuth=int(data.winddir + 180) % 360,
            direction=None,
        ),
        temperature=MeasureValue(avg=data.outtemp, min=None, max=None),
        humidity=MeasureValue(avg=data.inhumi, min=None, max=None),
        pressure=MeasureValue(avg=data.relbaro * 0.750061561303, min=None, max=None),
        light=MeasureValue(avg=data.light / 126.7, min=None, max=None),
        rain=MeasureValue(avg=data.dailyrain, min=None, max=None),
    )

    try:
        await import_data(data.ID, record)
    except ValueError as e:
        raise fastapi.HTTPException(status_code=400, detail=str(e)) from e

    return fastapi.Response(status_code=201)
