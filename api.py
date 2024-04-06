import json

import requests

from settings import cfg
import path_finder as pathfinder
from view import distribute_figures


def get_universe() -> dict[str]:
    response = requests.get(
        f"{cfg.api_root}/player/universe", headers={"X-Auth-Token": cfg.api_key_token}
    )

    match response.status_code:
        case 200:
            return response.json()
        case _:
            raise Exception("Wrong universe", response.status_code, response.text)


def travel(planets_path: list[str] | str) -> dict[str]:
    if not isinstance(planets_path, list):
        planets_path = [planets_path]
    response = requests.post(
        f"{cfg.api_root}/player/travel",
        headers={"X-Auth-Token": cfg.api_key_token},
        data={"planets": planets_path},
    )

    match response.status_code:
        case 200:
            result = response.json()
            with open(f"travels/travel_to_{planets_path[0]}", "w") as file:
                file.write(json.dumps(result))
            # planet_garbage_0_name,planet_garbage_0 = result['planetGarbage'].items()[0]

            return result
        case _:
            raise Exception("Wrong travel", response.status_code, response.text)


def collect(garbage: dict[str, list[list[int]]]) -> None:
    if not list(garbage.keys()):
        raise Exception("Empty garbage")

    response = requests.post(
        f"{cfg.api_root}/player/travel",
        headers={"X-Auth-Token": cfg.api_key_token},
        data={"garbage": garbage},
    )

    match response.status_code:
        case 200:
            result = response.json()

            return result
        case _:
            raise Exception("Wrong travel", response.status_code, response.text)


has_empty = True


def transmit() -> None:
    response = get_universe()

    ship = response["ship"]
    ship_garbage = ship["garbage"]
    planet = ship["planet"]
    universe = response["universe"]
    # where target is
    shortest_path, _distance = pathfinder.result(universe, ship["planet"], "Eden")[0:]
    # where target is end
    traveled_json = travel(shortest_path)
    ship_garbage = traveled_json["shipGarbage"]
    planet_garbage = traveled_json["planetGarbage"]

    collect(
        distribute_figures(
            bag=ship_garbage,
            inserted_figures=planet_garbage,
        )
    )


transmit()

response = get_universe()
universe_graph = [response['universe']]
