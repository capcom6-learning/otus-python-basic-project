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

from datetime import datetime, date
from typing import Union
import pydantic
import bson


class Period(pydantic.BaseModel):
    start: Union[date, None]
    end: Union[date, None]


class PyObjectId(bson.ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not bson.ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return bson.ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


class BaseModel(pydantic.BaseModel):
    id: PyObjectId = pydantic.Field(
        default_factory=PyObjectId,
        alias="_id",
        title="Идентификатор",
        description="Идентификатор объекта",
    )

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {bson.ObjectId: str}


class User(BaseModel):
    name: str = pydantic.Field(..., description="Имя пользователя")
    password: str = pydantic.Field(..., description="Пароль пользователя")


class StationIn(pydantic.BaseModel):
    code: str = pydantic.Field(..., description="Код станции")
    name: str = pydantic.Field(..., description="Название станции")
    lat: float = pydantic.Field(..., description="Широта")
    lon: float = pydantic.Field(..., description="Долгота")


class Station(BaseModel, StationIn):
    pass


class MeasureValue(pydantic.BaseModel):
    avg: float = pydantic.Field(..., description="Среднее значение")
    min: Union[float, None] = pydantic.Field(None, description="Минимальное значение")
    max: Union[float, None] = pydantic.Field(None, description="Максимальное значение")


class WindDirection(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if v not in [
            "N",
            "NNE",
            "NE",
            "ENE",
            "E",
            "ESE",
            "SE",
            "SSE",
            "S",
            "SSW",
            "SW",
            "WSW",
            "W",
            "WNW",
            "NW",
            "NNW",
        ]:
            raise ValueError("Invalid wind direction")
        return v

    @classmethod
    def from_azimuth(cls, azimuth: Union[float, None]) -> Union["WindDirection", None]:
        if azimuth is None:
            return None

        azimuth = (azimuth + 180) % 360
        if azimuth < 11.25:
            return WindDirection("N")
        elif azimuth < 33.75:
            return WindDirection("NNE")
        elif azimuth < 56.25:
            return WindDirection("NE")
        elif azimuth < 78.75:
            return WindDirection("ENE")
        elif azimuth < 101.25:
            return WindDirection("E")
        elif azimuth < 123.75:
            return WindDirection("ESE")
        elif azimuth < 146.25:
            return WindDirection("SE")
        elif azimuth < 168.75:
            return WindDirection("SSE")
        elif azimuth < 191.25:
            return WindDirection("S")
        elif azimuth < 213.75:
            return WindDirection("SSW")
        elif azimuth < 236.25:
            return WindDirection("SW")
        elif azimuth < 258.75:
            return WindDirection("WSW")
        elif azimuth < 281.25:
            return WindDirection("W")
        elif azimuth < 303.75:
            return WindDirection("WNW")
        elif azimuth < 326.25:
            return WindDirection("NW")
        elif azimuth < 348.75:
            return WindDirection("NNW")
        else:
            return WindDirection("N")


class WindValue(MeasureValue):
    azimuth: Union[int, None] = pydantic.Field(None, description="Азимут")
    direction: Union[WindDirection, None] = pydantic.Field(
        None, description="Направление"
    )


class AnonymousWeatherRecord(pydantic.BaseModel):
    timestamp: datetime = pydantic.Field(..., description="Дата и время")
    wind: WindValue = pydantic.Field(..., description="Ветер")
    temperature: MeasureValue = pydantic.Field(..., description="Температура")
    humidity: Union[MeasureValue, None] = pydantic.Field(..., description="Влажность")
    pressure: Union[MeasureValue, None] = pydantic.Field(..., description="Давление")
    light: Union[MeasureValue, None] = pydantic.Field(..., description="Освещенность")
    rain: Union[MeasureValue, None] = pydantic.Field(..., description="Осадки")


class WeatherRecord(BaseModel, AnonymousWeatherRecord):
    station: Station = pydantic.Field(..., description="Станция")
