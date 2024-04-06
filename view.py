from datetime import datetime
import itertools
from random import choice
from typing import NamedTuple, TypedDict, Sequence

import graphviz
import matplotlib.colors as colors
from matplotlib import pyplot as plt, patches

from constants import CAPACITY_X, CAPACITY_Y

colors = [color for color in colors._colors_full_map.values()]


def visualize_tight_shape(coordinates):
    fig, ax = plt.subplots()

    grid_size_x = max(coord[0] for coord in coordinates) + 1
    grid_size_y = max(coord[1] for coord in coordinates) + 1

    ax.set_aspect("equal")

    ax.set_xlim(-0.5, grid_size_x - 0.5)
    ax.set_ylim(-0.5, grid_size_y - 0.5)

    ax.set_xticks([])
    ax.set_yticks([])

    for coord in coordinates:
        square = patches.Rectangle(
            (coord[0] - 0.5, coord[1] - 0.5),
            1,
            1,
            linewidth=1,
            edgecolor="none",
            facecolor="blue",
        )
        ax.add_patch(square)

    plt.show()


def visualize_tight_shapes(bag):
    fig, ax = plt.subplots()

    grid_size_x = CAPACITY_X  # max(coord[0] for coord in trash_value) + 1
    grid_size_y = CAPACITY_Y  # max(coord[1] for coord in trash_value) + 1
    ax.set_aspect("equal")

    ax.set_xlim(-0.5, grid_size_x - 0.5)
    ax.set_ylim(-0.5, grid_size_y - 0.5)
    print()
    # colors = {'red', 'green', 'pink', 'orange', 'yellow', 'black', 'blue', 'purple', 'red'}

    for trash_key, trash_value in bag.items():
        ax.set_xticks([])
        ax.set_yticks([])
        color = choice(colors)
        for coord in trash_value:
            square = patches.Rectangle(
                (coord[0] - 0.5, coord[1] - 0.5),
                1,
                1,
                linewidth=1,
                edgecolor="none",
                facecolor=color,
            )
            ax.add_patch(square)

    plt.show()


def rotate_coords(x: int, y: int, rotate: int) -> tuple[int, int]:
    match rotate:
        case 0:
            return x, y
        case 90:
            return -y, x
        case 180:
            return -x, -y
        case 270:
            return y, -x
        case _:
            raise "Wrong rotate"


class Coordinates2D(TypedDict):
    x: int
    y: int


def distribute_figure(
        bag: dict[str, list[list[int]]], inserted_figure_coordinates: list[list[int]]
):
    matrix_with_filled_fields = [[False] * CAPACITY_Y for _ in range(CAPACITY_X)]

    for x, y in [
        coordinates
        for trash_coordinates_list in bag.values()
        for coordinates in trash_coordinates_list
    ]:
        matrix_with_filled_fields[x][y] = True

    empty_field_coordinates: Sequence[Coordinates2D] = sorted(
        [
            {"x": x, "y": y}
            for x, line_with_filled_fields in enumerate(matrix_with_filled_fields)
            for y, field in enumerate(line_with_filled_fields)
            if not field
        ],
        key=lambda coordinates: coordinates["x"] + coordinates["y"],
    )

    full_metric_evaluate = sum(
        sum(coordinates.values()) for coordinates in empty_field_coordinates
    )

    possible_placements = []

    for rotate, potential_coordinates in itertools.product(
            [0, 90, 180, 270], empty_field_coordinates
    ):
        potential_coordinates: Coordinates2D
        x_bag, y_bag = potential_coordinates["x"], potential_coordinates["y"]
        if not any(
                any(
                    (
                            inserted_figure_x + x_bag >= CAPACITY_X,
                            inserted_figure_y + y_bag >= CAPACITY_Y,
                            inserted_figure_x + x_bag < 0,
                            inserted_figure_y + y_bag < 0,
                    )
                )
                or matrix_with_filled_fields[inserted_figure_x + x_bag][
                    inserted_figure_y + y_bag
                ]
                for inserted_figure_x, inserted_figure_y in [
                    rotate_coords(*inserted_figure_coords, rotate)
                    for inserted_figure_coords in inserted_figure_coordinates
                ]
        ):
            possible_placements.append(
                {
                    "point": {"x": x_bag, "y": y_bag},
                    "rotate": rotate,
                    "metric": full_metric_evaluate
                              - sum(
                        sum(
                            (
                                *rotate_coords(*inserted_figure_coords, rotate),
                                x_bag,
                                y_bag,
                            )
                        )
                        for inserted_figure_coords in inserted_figure_coordinates
                    ),
                }
            )

    possible_placements.sort(key=lambda item: item["metric"], reverse=True)
    if not possible_placements:
        raise Exception("NULLABLE")
    return possible_placements[0]


def distribute_figures(
        bag: dict[str, list[list[int]]],
        inserted_figures: dict[str, list[list[int]]],
) -> dict[str, list[list[int]]]:
    sorted_inserted_figures = sorted(
        [(k, v) for k, v in inserted_figures.items()],
        key=lambda value: len(value[1]),
        # reverse=True
    )
    for inserted_figure_name, inserted_figures_coords in sorted_inserted_figures:
        try:
            rule_for_insert = distribute_figure(bag, inserted_figures_coords)
            x = rule_for_insert["point"]["x"]
            y = rule_for_insert["point"]["y"]
            bag[inserted_figure_name] = []
            for inserted_figure_coords in inserted_figures_coords:
                _x, _y = inserted_figure_coords
                _x, _y = rotate_coords(_x, _y, rule_for_insert["rotate"])
                bag[inserted_figure_name].append([x + _x, y + _y])
        except Exception as e:
            continue
            # print(len(bag.keys()))
            # return bag
    print(len(bag.keys()))
    return bag


# visualize_tight_shapes(
#     distribute_figures(bag={},
#                        inserted_figures={
#                            '1': [[0, 0], [0, 1], [1, 1], [1, 2]],
#                            '2': [[0, 0], [0, 1], [1, 1], [1, 2], [2, 2], [2, 3], [3, 3]
#                                  ],
#                            '3': [[0, 0], [0, 1], [1, 1], [2, 1], [2, 0], [3, 0]],
#                            '4': [[0, 0], [0, 1], [1, 1], [0, 2], [1, 2], [1, 3]],
#                            '5': [[0, 0], [1, 0], [2, 0], [3, 0], [0, 1], [2, 1], [2, 2], [3, 2]],
#                            '6': [[0, 0], [1, 0], [2, 0], [1, 1], [2, 1]],
#                            '7': [[0, 0], [1, 0], [1, 1], [1, 2], [0, 2], [2, 2], [0, 3], [2, 3], [3, 3]],
#                            '8': [[0, 0], [1, 0], [1, 1], [2, 1], [1, 2]],
#                            '9': [[0, 0], [0, 1], [1, 1], [1, 2]],
#                            '10': [[0, 0], [0, 1], [1, 1], [1, 2], [2, 2], [2, 3], [3, 3]
#                                   ],
#                            '11': [[0, 0], [1, 0], [2, 0], [3, 0], [0, 1], [2, 1]],
#                            '12': [[0, 0], [0, 1], [1, 1], [1, 2]],
#                            '13': [[0, 0], [1, 0], [1, 1], [1, 2], [0, 2], [2, 2], [0, 3], [2, 3], [3, 3]],
#                            '14': [[0, 0], [1, 0], [1, 1], [1, 2], [0, 2], [2, 2], [0, 3], [2, 3], [3, 3]],
#                            '15': [[0, 0], [1, 0], [2, 0], [3, 0], [0, 1], [2, 1], [2, 2], [3, 2]],
#                            '16': [[0, 0], [0, 1], [1, 1], [1, 2]],
#                            '17': [[0, 0], [0, 1], [1, 1], [1, 2]],
#                            '18': [[0, 0], [0, 1], [1, 1], [1, 2]],
#                            '19': [[0, 0], [0, 1], [1, 1], [1, 2]],
#
#                        }
#                        )
#
# )
#
# visualize_tight_shapes(
#     distribute_figures(
#         bag={},
#         inserted_figures={
#             "2FvakD": [[0, 0], [0, 1], [1, 1], [2, 1], [3, 1], [2, 2]],
#             "2FvbCi": [[0, 1], [0, 0], [1, 1], [2, 1], [2, 0], [3, 0]],
#             "2FvvP1": [[0, 2], [0, 1], [0, 0], [1, 2], [2, 2], [2, 1]],
#             "2FwFZJ": [[0, 1], [1, 1], [1, 0], [2, 1], [3, 1]],
#             "2FwG63": [[0, 0], [1, 0], [2, 0], [1, 1], [2, 1]],
#             "2FwbGL": [[0, 0], [0, 1], [1, 1], [0, 2], [1, 2], [1, 3]],
#             "2Fwbiq": [
#                 [0, 0],
#                 [1, 0],
#                 [2, 0],
#                 [3, 0],
#                 [0, 1],
#                 [3, 1],
#                 [0, 2],
#                 [1, 2],
#                 [1, 3],
#             ],
#             "2Fwvu8": [[0, 0], [0, 1], [1, 1], [1, 2], [2, 2], [2, 3], [3, 3]],
#             "2FxG5R": [[0, 1], [1, 1], [1, 0], [2, 1], [3, 1]],
#             "2FxGXv": [[0, 0], [0, 1], [1, 1], [2, 1], [1, 2], [1, 3], [2, 3], [3, 3]],
#             "2FxbiD": [
#                 [0, 0],
#                 [1, 0],
#                 [2, 0],
#                 [0, 1],
#                 [0, 2],
#                 [1, 2],
#                 [2, 2],
#                 [3, 2],
#                 [2, 3],
#             ],
#             "2FxcAi": [[0, 0], [0, 1], [1, 1]],
#             "HXLk": [
#                 [0, 0],
#                 [1, 0],
#                 [2, 0],
#                 [3, 0],
#                 [0, 1],
#                 [0, 2],
#                 [1, 2],
#                 [2, 2],
#                 [0, 3],
#                 [2, 3],
#             ],
#             "HXoF": [[0, 2], [1, 2], [1, 1], [1, 0], [2, 2], [3, 2]],
#             "HryY": [[0, 2], [0, 1], [1, 1], [1, 0], [2, 1]],
#             "HsS3": [[0, 2], [0, 1], [0, 0], [1, 2], [1, 1]],
#             "JCcL": [[0, 0], [1, 0]],
#             "JXnd": [[0, 2], [0, 1], [0, 0], [1, 2], [1, 0], [2, 2], [3, 2]],
#             "JYF8": [
#                 [0, 3],
#                 [0, 2],
#                 [0, 1],
#                 [1, 3],
#                 [1, 1],
#                 [2, 3],
#                 [2, 1],
#                 [3, 3],
#                 [3, 2],
#                 [3, 1],
#                 [3, 0],
#             ],
#             "JsRR": [[0, 0], [1, 0], [2, 0], [3, 0], [0, 1], [2, 1], [2, 2], [3, 2]],
#             "Jssv": [[0, 2], [0, 1], [0, 0], [1, 1], [2, 1], [3, 1], [3, 0]],
#             "KD8T": [[0, 0], [1, 0], [2, 0], [3, 0], [0, 1], [1, 1]],
#             "KYJk": [[0, 0], [1, 0], [2, 0], [3, 0], [0, 1], [3, 1]],
#             "KYmF": [[0, 0], [0, 1], [1, 1], [2, 1], [0, 2], [2, 2], [3, 2], [2, 3]],
#             "KswY": [[0, 2], [0, 1], [1, 1], [1, 0], [2, 1], [3, 1]],
#             "LD7q": [[0, 0], [0, 1], [1, 1], [1, 2]],
#             "LDaL": [
#                 [0, 0],
#                 [0, 1],
#                 [1, 1],
#                 [2, 1],
#                 [0, 2],
#                 [2, 2],
#                 [0, 3],
#                 [2, 3],
#                 [3, 3],
#             ],
#         },
#     )
# )


def show_me_planet(planets: list[tuple[str, str, int]]) -> None:
    dot = graphviz.Graph(comment="Planets")
    planets_name = {planet[0] for planet in planets} | {planet[1] for planet in planets}
    for planet_name in planets_name:
        dot.node(planet_name, planet_name)
    for edge in planets:
        head_planet, tail_planet, distance = edge
        # dot.edges([[planet[0], planet[1]] for planet in planets])
        dot.edge(tail_planet, head_planet, label=str(distance))
    dot.render("./graphs/dotgraph_" + datetime.now().isoformat(), view=True)
