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

import fastapi
from fastapi.middleware.gzip import GZipMiddleware

from app.api import router as api_router
from app.drivers import router as drivers_router
from app.log import setup_logging
from app.settings import config

setup_logging()

app = fastapi.FastAPI(
    docs_url="/docs" if config.common.debug else None,
    redoc_url="/redoc" if config.common.debug else None,
)

app.add_middleware(GZipMiddleware, minimum_size=1024)

app.include_router(api_router, prefix="/api")
app.include_router(drivers_router)


@app.on_event("startup")
async def on_startup() -> None:
    # verify database
    pass


@app.get("/")
def index():
    return {"message": "Hello World"}
