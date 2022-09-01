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

from typing import Union
from app.database import db
from app.models import User

collection = db.users


async def insert(user: User):
    """Add a user"""
    await collection.insert_one(user.dict(by_alias=True))


async def get(name: str) -> Union[User, None]:
    """Get a user by name"""
    user = await collection.find_one({"name": name})
    if user:
        return User(**user)
    return None
