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

from datetime import datetime
from typing import Union
import pydantic
import bson


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


class Station(BaseModel):
    code: str = pydantic.Field(..., description="Код станции")
    name: str = pydantic.Field(..., description="Название станции")
    lat: float = pydantic.Field(..., description="Широта")
    lon: float = pydantic.Field(..., description="Долгота")


class MeasureValue(pydantic.BaseModel):
    cur: float = pydantic.Field(..., description="Текущее значение")
    min: Union[float, None] = pydantic.Field(None, description="Минимальное значение")
    max: Union[float, None] = pydantic.Field(None, description="Максимальное значение")


class WindValue(MeasureValue):
    azimuth: Union[int, None] = pydantic.Field(None, description="Азимут")
    direction: Union[str, None] = pydantic.Field(None, description="Направление")


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
