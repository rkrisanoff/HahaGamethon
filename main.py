from collections import deque
from pprint import pprint

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
            if (self._check_inventery()):
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


def transmit():
    forbidden_planets = {'Earth', 'Eden'}
    fullnesses = []
    response = api.get_universe()
    universe_graph = pathfinder.to_graph(response["universe"])
    current_planet = response["ship"]["planet"]['name']
    closest_planet = universe_graph.nearest_available(current_planet, forbidden_planets)

    while closest_planet:
        shortest_path, _distance = pathfinder.result(
            universe_graph,
            current_planet,
            closest_planet
        )
        shortest_path = shortest_path[1:]

        traveled_json = api.travel(shortest_path)
        ship_garbage = traveled_json["shipGarbage"] or {}
        planet_garbage = traveled_json["planetGarbage"]

        collected_garbage = distribute_figures(
            bag=ship_garbage,
            inserted_figures=planet_garbage,
        )
        collect_json = api.collect(collected_garbage)
        fullness = sum(1. for _ in collected_garbage.values()) / (CAPACITY_X * CAPACITY_Y)
        fullnesses.append(fullness)
        pprint(f'{fullness = }')
        if not (set(planet_garbage.keys()) - set(collected_garbage.keys())):
            forbidden_planets.add(current_planet)
            bag = api.get_universe()['ship']['garbage']
            visualize_tight_shapes(bag)
            response = api.get_universe()
            universe_graph = pathfinder.to_graph(response["universe"])
            current_planet = response["ship"]["planet"]['name']
            closest_planet = universe_graph.nearest_available(current_planet, forbidden_planets)
        else:
            shortest_path, _distance = pathfinder.result(
                universe_graph,
                current_planet,
                'Eden'
            )
            shortest_path = shortest_path[1:]
            traveled_json = api.travel(shortest_path[1:])

    return forbidden_planets, fullness


transmit()
