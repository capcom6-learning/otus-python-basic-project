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

import app.models as models
import app.repositories.stations as stations
import app.repositories.measurements as measurements


async def import_data(station_code: str, record: models.AnonymousWeatherRecord):
    station = await stations.get_by_code(station_code)
    if station is None:
        raise ValueError(f"Station {station_code} not found")

    db_record = models.WeatherRecord(station=station, **record.dict())
    if db_record.wind.avg < 0.01:
        db_record.wind.azimuth = None
        db_record.wind.direction = None

    if not db_record.wind.azimuth is None:
        db_record.wind.direction = models.WindDirection.from_azimuth(
            db_record.wind.azimuth
        )

    await measurements.insert(db_record)
