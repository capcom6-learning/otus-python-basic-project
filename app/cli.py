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

import asyncio
import os

import click

from app.log import setup_logging

setup_logging()


@click.group()
def cli():
    pass


@cli.command()
@click.option(
    "--host", default="127.0.0.1", show_default=True, help="Hostname to listen on"
)
@click.option("--port", default=8000, show_default=True, help="Port to listen on")
def start(host: str, port: int):
    """Start the server"""
    import uvicorn

    uvicorn.run("app.server:app", host=host, port=port, reload=True)


@cli.command()
def ping():
    """Ping the server"""
    import requests

    port = os.environ.get("PORT", "8000")

    try:
        response = requests.get(f"http://localhost:{port}", timeout=1)
        if response.status_code == 200:
            click.echo("Server is up")
        else:
            click.echo("Server is down")
            exit(1)
    except Exception:
        click.echo("Server is down")
        exit(1)


@cli.command()
def db_init():
    """Initialize the database"""
    from app.database import init

    asyncio.run(init())

    click.echo("Database initialized")


@cli.command()
@click.option("--name", help="Name of the user", required=True)
def user_add(name: str):
    """Add a user"""
    asyncio.run(user_add_async(name))


async def user_add_async(name: str):
    """Add a user async"""
    import app.repositories.users as users

    user = await users.get(name)
    if user:
        click.echo("User already exists")
        return

    import bcrypt

    password = click.prompt(
        "Password", hide_input=True, confirmation_prompt="Repeat password"
    )

    if len(password) < 8:
        click.echo("Password must be at least 8 characters long")
        return

    from app.models import User

    user = User(
        name=name, password=bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    )

    await users.insert(user)

    click.echo(f"User {name} added with id {user.id}")
