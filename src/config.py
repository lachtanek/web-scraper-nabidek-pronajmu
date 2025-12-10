import functools
import operator
import os
from pathlib import Path
from typing import Annotated

import environ
from pydantic import BeforeValidator
from pydantic_settings import BaseSettings, SettingsConfigDict

from disposition import Disposition

app_env = os.getenv("APP_ENV")
if app_env:
    env_files = (".env", ".env." + app_env, ".env.local")
else:
    env_files = (".env", ".env.local")

_str_to_disposition_map = {
    "1+kk": Disposition.FLAT_1KK,
    "1+1": Disposition.FLAT_1,
    "2+kk": Disposition.FLAT_2KK,
    "2+1": Disposition.FLAT_2,
    "3+kk": Disposition.FLAT_3KK,
    "3+1": Disposition.FLAT_3,
    "4+kk": Disposition.FLAT_4KK,
    "4+1": Disposition.FLAT_4,
    "5++": Disposition.FLAT_5_UP,
    "others": Disposition.FLAT_OTHERS,
}


def dispositions_converter(raw_disps: str) -> Disposition:
    return functools.reduce(
        operator.or_,
        map(lambda d: _str_to_disposition_map[d], raw_disps.split(",")),
        Disposition.NONE,
    )


class Config(BaseSettings):
    model_config = SettingsConfigDict(env_file=env_files)

    debug: bool
    found_offers_file: Path
    refresh_interval_daytime_minutes: int
    refresh_interval_nighttime_minutes: int
    dispositions: Annotated[Disposition, BeforeValidator(dispositions_converter)]
    embed_batch_size: int = 10
    min_price: int | None = None
    max_price: int | None = None
    image_deduplication_threshold: int = 5

    discord_token: str = environ.var()
    discord_offers_channel: int = environ.var(converter=int)
    discord_dev_channel: int = environ.var(converter=int)


config = Config()
