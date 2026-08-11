from typing import AsyncGenerator
from app.repositories.influxdb_repository import influx_repo


async def get_repository():
    return influx_repo
