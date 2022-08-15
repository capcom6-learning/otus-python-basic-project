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

init:
	pip install -r requirements.txt

init-dev: init
	pip install -r requirements-dev.txt

start:
	gunicorn --bind=0.0.0.0:8000 --access-logfile=- --proxy-allow-from='*' -k uvicorn.workers.UvicornWorker app.server:app

start-dev:
	python -m app start

.PHONY: init init-dev
