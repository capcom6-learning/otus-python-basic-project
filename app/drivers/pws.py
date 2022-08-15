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
    dateutc: str
    softwaretype: str
    action: str
    rtfreq: int
    realtime: int
