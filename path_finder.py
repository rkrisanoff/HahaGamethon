import collections, sys
import json
import pprint
from typing import Sequence


def dijkstra_algorithm(graph, start_node):
    unvisited_nodes = list(graph.get_nodes())
    shortest_path = {}
    previous_nodes = {}
    max_value = sys.maxsize
    for node in unvisited_nodes:
        shortest_path[node] = max_value
    shortest_path[start_node] = 0

    while unvisited_nodes:
        current_min_node = None
        for node in unvisited_nodes:
            if current_min_node is None:
                current_min_node = node
            elif shortest_path[node] < shortest_path[current_min_node]:
                current_min_node = node

        neighbors = graph.get_outgoing_edges(current_min_node)
        for neighbor in neighbors:
            tentative_value = shortest_path[current_min_node] + graph.value(current_min_node, neighbor)
            if tentative_value < shortest_path[neighbor]:
                shortest_path[neighbor] = tentative_value
                previous_nodes[neighbor] = current_min_node

        unvisited_nodes.remove(current_min_node)

    return previous_nodes, shortest_path


def construct_graph(nodes, init_graph):
    graph = {}
    for node in nodes:
        graph[node] = {}

    graph.update(init_graph)
    return graph


class Graph(object):
    def __init__(self, nodes, init_graph):
        self.nodes = nodes
        self.graph = construct_graph(nodes, init_graph)

    def get_nodes(self):
        return self.nodes

    def get_outgoing_edges(self, node):
        connections = []
        for out_node in self.nodes:
            if self.graph[node].get(out_node, False):
                connections.append(out_node)
        return connections

    def value(self, node1, node2):
        return self.graph[node1][node2]

    def nearest_available(self, node,
                          banned_planets):  # принимает node (текущую планету), banned_planets (очищенные от мусора планеты)
        _, nearests = dijkstra_algorithm(self, node,
                                         "Eden"
                                         )
        planets = [planet for planet, distance in sorted(nearests.items(),
                                                         key=lambda item: item[1]) if
                   planet not in banned_planets and planet != node]
        if len(planets) <= 1:
            return None
            # raise Exception("No  planets available")
        return planets[1]


def result(graph, start_node, target_node) -> tuple[Sequence[str], int]:
    previous_nodes, shortest_path = dijkstra_algorithm(graph=graph, start_node=start_node)
    path = []
    node = target_node

    while node != start_node:
        path.append(node)
        node = previous_nodes[node]

    # Добавить начальный узел вручную
    path.append(start_node)
    return list(reversed(path)), shortest_path[target_node]


def to_graph(array):
    nodes = []
    init_graph = {}
    unique_names = set()
    for i in array:
        unique_names.update(i[:2])

    for node in unique_names:
        init_graph[node] = {}

    for node in array:
        init_graph[node[0]][node[1]] = node[2]

    graph = Graph(unique_names, init_graph)
    return graph

# with open('universe.json', 'r') as fl:
#     data = json.load(fl)
#
# universe = to_graph(data['universe'])
#
# pprint.pprint(result(universe, start_node="Earth", target_node="Eden"))
