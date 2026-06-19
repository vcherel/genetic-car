import os
from statistics import mean

import matplotlib.pyplot as plt
import numpy as np
import pygame
import pylab

import data.variables as var
from data.constants import CAR_SIZES, PATH_DATA, PATH_IMAGE

number_checkpoints = [143, 131, 144, 113, 57, 0, 146, 156]


class BestCar:
    def __init__(self, data):
        data = [int(data) for data in data]
        self.x1, self.y1, self.x2, self.y2, self.x3, self.y3, self.score = data
        self.tab = [self.x1, self.y1, self.x2, self.y2, self.x3, self.y3]

    def __str__(self):
        return f"({self.x1}, {self.y1}, {self.x2}, {self.y2}, {self.x3}, {self.y3}) ; Score : {self.score}"

    def __getitem__(self, item):
        return self.tab[item]


def analyze_test_all_cars(num_map):
    nb_checkpoints = number_checkpoints[num_map]

    scores = []
    cars = []
    best_cars = []

    with open(f"{PATH_DATA}tests/all_cars/results/{num_map}", "r") as file_read:
        for line in file_read:
            data = line.split(" ")

            if num_map == 5:
                return
            else:
                score = int(data[6][:-1])
            scores.append(score)
            cars.append(BestCar(data))

            if score > nb_checkpoints:
                best_cars.append(BestCar(data))

        scores.sort(reverse=True)
        best_cars.sort(key=lambda x: x.score, reverse=True)

    with open(f"{PATH_DATA}tests/all_cars/analysis/{num_map}", "w") as file_write:
        multiplier = 1
        end_loop = False
        nb_cars = 0
        while not end_loop:
            for car in best_cars:
                if car.score >= multiplier * nb_checkpoints:
                    nb_cars += 1
            if nb_cars > 0:
                if multiplier == 1:
                    file_write.write(f"Cars that completed at least one lap : {nb_cars}\n")
                else:
                    file_write.write(f"Cars that completed at least {multiplier} lap : {nb_cars}\n")
                multiplier += 1
                nb_cars = 0
            else:
                end_loop = True

        file_write.write(f"\nMean score : {mean(scores)}\n")
        file_write.write(f"Max score : {max(scores)}\n")
        file_write.write(f"Min score : {min(scores)}\n")
        file_write.write(f"Median score : {scores[len(scores) // 2]}\n")

        name_parameters = ["Length slow", "Length medium", "Length fast", "Width slow", "Width medium", "Width fast"]
        file_write.write("\nCorrelation between the parameters and the score:\n")
        for j in range(0, 6):
            file_write.write(f"{name_parameters[j]} : {np.corrcoef([car[j] for car in cars], scores)[0][1]}\n")

        file_write.write("\nParameters of the cars that completed at least one lap:\n")
        for car in best_cars:
            file_write.write(f"{car}\n")


def show_graph(num_map):
    scores = []

    with open(f"{PATH_DATA}tests/all_cars/results/{num_map}", "r") as file_read:
        for line in file_read:
            data = line.split(" ")

            if num_map == 5:
                score = int(float(data[6][:-1]) / 100)
                data[6] = str(score)
            else:
                score = int(data[6][:-1])
            scores.append(score)

    scores.sort(reverse=True)

    plt.plot(scores, range(1, len(scores) + 1))
    plt.xlabel("Score")
    plt.ylabel("Number of cars")
    plt.title("Cars remaining on the track /number of checkpoints passed")
    fig = pylab.gcf()
    fig.canvas.manager.set_window_title(f"Map {num_map}")
    plt.show()


def analyze_genetic_algorithm():
    mutation_only = []
    crossover_mutation = []
    with open(f"{PATH_DATA}tests/mutation_only", "r") as file:
        for line in file:
            data = line.split()
            mutation_only.append(int(data[0]))

    with open(f"{PATH_DATA}tests/crossover_mutation", "r") as file:
        for line in file:
            data = line.split()
            crossover_mutation.append(int(data[0]))

    data = [mutation_only, crossover_mutation]
    red_square = dict(marker="2", markeredgecolor="red")
    plt.boxplot(data, showmeans=True, meanprops=red_square)
    plt.title(
        "Box-plot du nombre de générations nécessaire pour compléter un tour\n"
        " avec 2 algorithmes génétiques différents (sur 150 essais)"
    )
    plt.ylim(0, 15)
    plt.ylabel("Nombre de générations")
    pylab.xticks([1, 2], ["Mutations seulement", "Croisements puis mutations"])

    fig = plt.gcf()
    fig.set_size_inches(5.2, 3.2)
    plt.savefig("algo.pgf")


def analyze_value_genetic_parameters():
    dict_mean_values = {}

    for filename in os.listdir(PATH_DATA + "tests/genetic_parameters/"):
        f = f"{PATH_DATA}tests/genetic_parameters/" + filename
        list_values = []
        with open(f, "r") as file:
            for line in file:
                list_values.append(int(line.split()[0]))
        if len(list_values) == 50:
            dict_mean_values[filename] = mean(list_values)
        else:
            print(f"Le fichier {filename} ne contient pas 50 valeurs")

    dict_mean_values = {k: v for k, v in sorted(dict_mean_values.items(), key=lambda item: item[1])}
    for key in dict_mean_values.keys():
        print(f"{key} : {dict_mean_values[key]}")


def show_heat_map(num_map):
    scores = []
    nb_checkpoints = number_checkpoints[num_map]

    with open(f"{PATH_DATA}tests/all_cars/results/{num_map}", "r") as file_read:
        for line in file_read:
            data = line.split(" ")

            if num_map == 5:
                return
            else:
                score = int(data[6][:-1])

            if score > nb_checkpoints:
                scores.append(score // nb_checkpoints)
            else:
                scores.append(score)

        scores.sort(reverse=True)

    with open(f"{PATH_DATA}checkpoints/{num_map}", "r") as file_read:
        checkpoints = []
        for line in file_read:
            data = line.split(" ")
            checkpoints.append((int(data[0]), int(data[1])))

    coordinate_list = [(checkpoints[scores[i] - 1][0], checkpoints[scores[i] - 1][1] - 115) for i in range(len(scores))]

    heat_map = np.zeros((1500, 585))

    for coord in coordinate_list:
        heat_map[coord] += 1
    max_value = np.amax(heat_map)

    heat_map_surface = pygame.image.load(f"{PATH_IMAGE}background/background_{str(num_map)}.png")
    result_surface = pygame.image.load(f"{PATH_IMAGE}background/background_{str(num_map)}.png")

    circles_to_draw = []
    for i, x in enumerate(heat_map):
        for j, y in enumerate(x):
            if y != 0:
                alpha = min(y / max_value * 255 * 1.5, 255)
                circles_to_draw.append(((i, j), alpha))

    circles_to_draw.sort(key=lambda item: item[1])
    for circle in circles_to_draw:
        pygame.draw.circle(
            heat_map_surface, (255, 255 - circle[1], 255 - circle[1]), circle[0], CAR_SIZES[var.NUM_MAP] * 6
        )

    for x in range(result_surface.get_width()):
        for y in range(result_surface.get_height()):
            pixel_color = result_surface.get_at((x, y))
            if pixel_color == (255, 255, 255, 255):
                result_surface.set_at((x, y), heat_map_surface.get_at((x, y)))
            else:
                result_surface.set_at((x, y), pixel_color)

    pygame.image.save(result_surface, f"images/background/heatmap_{num_map}.png")


if __name__ == "__main__":
    for number_map in range(8):
        print(number_map)
        show_heat_map(number_map)
