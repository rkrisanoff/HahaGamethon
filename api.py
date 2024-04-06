import json
from typing import Sequence

import requests

from constants import CAPACITY_X, CAPACITY_Y
from settings import cfg
import path_finder as pathfinder
from view import distribute_figures, visualize_tight_shapes
from pprint import pprint


def get_universe() -> dict[str]:
    response = requests.get(
        f"{cfg.api_root}/player/universe", headers={"X-Auth-Token": cfg.api_key_token}
    )

    match response.status_code:
        case 200:
            return response.json()
        case _:
            raise Exception("Wrong universe", response.status_code, response.text)


def travel(planets_path: Sequence[str] | str) -> dict[str]:
    if not isinstance(planets_path, list):
        planets_path = [planets_path]

    response = requests.post(
        f"{cfg.api_root}/player/travel",
        headers={"X-Auth-Token": cfg.api_key_token},
        data=json.dumps({"planets": planets_path}),
    )

    match response.status_code:
        case 200:
            return response.json()
        case _:
            raise Exception("Wrong travel", response.status_code, response.text)


def collect(garbage: dict[str, list[list[int]]]) -> dict:
    if not list(garbage.keys()):
        raise Exception("Empty garbage")

    response = requests.post(
        f"{cfg.api_root}/player/collect",
        headers={"X-Auth-Token": cfg.api_key_token},
        data=json.dumps({"garbage": garbage}),
    )

    match response.status_code:
        case 200:
            return response.json()
        case _:
            raise Exception("Wrong travel", response.status_code, response.text)




# visualize_tight_shapes(
#     distribute_figures(
#         bag=get_universe()['ship']['garbage'],
#         inserted_figures={}
#     )
# )
