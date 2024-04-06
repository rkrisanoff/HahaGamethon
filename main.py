import json
from collections import deque
from math import ceil
from pprint import pprint
from time import sleep

import api
import path_finder as pathfinder
from constants import CAPACITY_X, CAPACITY_Y
from view import distribute_figures, visualize_tight_shapes


class Ship:
    current: str
    forbidden_planet: set[str]
    bag: dict[str, list[list[int]]]

    def __init__(self, universe):
        self.current = "Earth"
        # self.to_eden(universe)
        self.path = []
        self.bag = {}
        self.forbidden_planet = {"Earth"}

    def act(self, universe):
        if self.current == "Eden":
            new_planet = self.get_target()
            self.new_target(universe, new_planet)
            self.current = new_planet
            self._fly()
        else:
            self._collect_trash()
            if self._check_inventery():
                self.to_eden()
                self._fly()
            else:
                new_planet = self.get_target()
                self.new_target(universe, new_planet)
                self.current = new_planet
                self._fly()

    def _fly(self):  # произвести перелёт
        pass

    def _check_inventory(self):  # проверить инвентарь на заполненность
        return True

    def collect_trash(self):  # собрать мусор
        pass

    def new_target(self, universe, planet):  # прокладывает путь до planet
        self.path = path_finder.result(universe, self.current, planet)[0][1:]

    def get_target(self, universe):
        _, nearests = path_finder.dijkstra_algorithm(universe, self.current)
        distances = [v for k, v in sorted(nearests.items(), key=lambda item: item[1])]
        planets = [k for k, v in sorted(nearests.items(), key=lambda item: item[1])]
        for i in planets:
            if not (planets in self.is_visited[1:]):
                return i

    def to_eden(self, universe):  # прокладываем путь до Эдема
        self.path = deque(pathfinder.result(universe, self.current, "Eden")[0][1:])


def get_fullness(bag):
    return sum(len(trash_coords) for trash_coords in bag.values()) / (
            CAPACITY_X * CAPACITY_Y
    )


def transmit():
    with open('./forbidden_planets.json', 'r') as file:
        forbidden_planets = set(json.loads(file.read()))

    fullnesses = []
    response = api.get_universe()
    universe_graph = pathfinder.to_graph(response["universe"])
    current_planet = response["ship"]["planet"]["name"]
    closest_planet = universe_graph.nearest_available(current_planet, forbidden_planets)

    while closest_planet:
        try:
            shortest_path, _distance = pathfinder.result(
                universe_graph, current_planet, closest_planet
            )
            # pprint(f"ZERO{shortest_path = }")
            traveled_json = api.travel(shortest_path[1:])
            response = api.get_universe()
            universe_graph = pathfinder.to_graph(response["universe"])
            current_planet = response["ship"]["planet"]["name"]

            ship_garbage = traveled_json["shipGarbage"] or {}
            planet_garbage = traveled_json["planetGarbage"]
            if not set(planet_garbage.keys()):
                forbidden_planets.add(current_planet)
                with open('./forbidden_planets.json', 'w') as file:
                    file.write(json.dumps(list(forbidden_planets)))
                response = api.get_universe()
                bag = response["ship"]["garbage"]
                # visualize_tight_shapes(bag)
                universe_graph = pathfinder.to_graph(response["universe"])
                current_planet = response["ship"]["planet"]["name"]
                closest_planet = universe_graph.nearest_available(
                    current_planet, forbidden_planets
                )
                continue

            old_fullness = get_fullness(ship_garbage)
            collected_garbage = distribute_figures(
                bag=ship_garbage,
                inserted_figures=planet_garbage,
            )
            fullness = get_fullness(collected_garbage)
            pprint(f"{old_fullness = }")
            pprint(f"{fullness = }")
            fullnesses.append(fullness)

            if (
                    (old_fullness < 0.001 and fullness - old_fullness > 0.30)
                    or (old_fullness >= 0.001 and fullness - old_fullness > 0.05)
            ) or not (set(planet_garbage.keys()) - set(collected_garbage.keys())):
                collect_json = api.collect(collected_garbage)

                if not (set(planet_garbage.keys()) - set(collected_garbage.keys())):  # планета не пуста

                    if fullness >= 0.75:
                        shortest_path, _distance = pathfinder.result(
                            universe_graph, current_planet, "Eden"
                        )
                        pprint(f"{shortest_path = }")
                        traveled_json = api.travel(shortest_path[1:])
                        response = api.get_universe()
                        universe_graph = pathfinder.to_graph(response["universe"])
                        current_planet = response["ship"]["planet"]["name"]
                        continue

                    forbidden_planets.add(current_planet)
                    with open('./forbidden_planets.json', 'w') as file:
                        file.write(json.dumps(list(forbidden_planets)))

                    response = api.get_universe()
                    bag = response["ship"]["garbage"]
                    # visualize_tight_shapes(bag)
                    universe_graph = pathfinder.to_graph(response["universe"])
                    current_planet = response["ship"]["planet"]["name"]
                    closest_planet = universe_graph.nearest_available(
                        current_planet, forbidden_planets
                    )
                else:

                    shortest_path, _distance = pathfinder.result(
                        universe_graph, current_planet, "Eden"
                    )
                    pprint(f"{shortest_path = }")
                    traveled_json = api.travel(shortest_path[1:])
                    response = api.get_universe()
                    universe_graph = pathfinder.to_graph(response["universe"])
                    current_planet = response["ship"]["planet"]["name"]

            else:
                shortest_path, _distance = pathfinder.result(
                    universe_graph, current_planet, "Eden"
                )
                pprint(f"{shortest_path = }")
                traveled_json = api.travel(shortest_path[1:])
                response = api.get_universe()
                universe_graph = pathfinder.to_graph(response["universe"])
                current_planet = response["ship"]["planet"]["name"]
        except Exception as e:
            sleep(1)
            print(e)
    response = api.get_universe()
    universe_graph = pathfinder.to_graph(response["universe"])
    current_planet = response["ship"]["planet"]["name"]

    shortest_path, _distance = pathfinder.result(
        universe_graph, current_planet, "Eden"
    )
    traveled_json = api.travel(shortest_path[1:])
    with open('./forbidden_planets.json', 'w') as file:
        file.write(json.dumps([]))
    return []


transmit()
