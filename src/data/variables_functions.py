import sys

import pygame

import data.variables as var
from data.constants import CAR_SIZES, PATH_DATA, PATH_IMAGE, START_ANGLES, START_POSITIONS
from data.data_classes import MemoryCar
from game.genetic import Genetic
from menus.settings_menu import SETTINGS
from render.display import edit_background
from render.resizing import convert_to_new_window, scale_image


def init_variables(nb_cars, replay=False):
    var.NB_CARS_ALIVE = nb_cars
    var.TICKS_REMAINING = var.TIME_GENERATION * 60
    var.DISPLAY_GARAGE = False
    if replay:
        var.NUM_GENERATION += 1
    else:
        var.NUM_GENERATION = 1


def resize_window(dimensions):
    var.WIDTH_SCREEN, var.HEIGHT_SCREEN = dimensions
    var.WINDOW = pygame.display.set_mode((var.WIDTH_SCREEN, var.HEIGHT_SCREEN), pygame.RESIZABLE)
    update_visual_variables()
    pygame.display.flip()
    var.BIG_RED_CAR_IMAGE = pygame.transform.rotate(scale_image(pygame.image.load(PATH_IMAGE + "/car.png"), 1.5), 90)
    load_explosions()


def update_visual_variables():
    var.SCALE_RESIZE_X = var.WIDTH_SCREEN / 1500
    var.SCALE_RESIZE_Y = var.HEIGHT_SCREEN / 700
    create_background()
    var.WINDOW.blit(var.BACKGROUND, (0, 0))
    pygame.display.flip()


def load_explosions():
    var.EXPLOSION_IMAGES = []
    for num in range(1, 10):
        image = pygame.image.load(f"{PATH_IMAGE}explosion/{num}.png")
        image = scale_image(image, CAR_SIZES[var.NUM_MAP] / 25 * var.SCALE_RESIZE_X)
        var.EXPLOSION_IMAGES.append(image)


def change_map(first_time=False, reverse=False):
    if not first_time:
        if not reverse:
            if var.NUM_MAP >= var.NB_MAPS - 1:
                var.NUM_MAP = 0
            else:
                var.NUM_MAP += 1
        else:
            if var.NUM_MAP == 0:
                var.NUM_MAP = var.NB_MAPS - 1
            else:
                var.NUM_MAP -= 1

    var.START_POSITION = START_POSITIONS[var.NUM_MAP]
    var.START_ANGLE = START_ANGLES[var.NUM_MAP]
    var.RADIUS_CHECKPOINT = 7.5 * CAR_SIZES[var.NUM_MAP]

    background = pygame.Surface((1500, 700))
    background.blit(
        pygame.transform.scale(
            pygame.image.load(f"{PATH_IMAGE}background/background_{str(var.NUM_MAP)}.png"), (1500, 585)
        ),
        (0, 115),
    )
    var.BACKGROUND_MASK = pygame.mask.from_threshold(background, (0, 0, 0, 255), threshold=(1, 1, 1, 1))

    var.RED_CAR_IMAGE = scale_image(pygame.image.load(PATH_IMAGE + "car.png"), CAR_SIZES[var.NUM_MAP] / 75)
    create_background()
    var.WINDOW.blit(var.BACKGROUND, (0, 0))

    var.CHECKPOINTS = []
    with open(f"{PATH_DATA}/checkpoints/{var.NUM_MAP}", "r") as file_checkpoint_read:
        checkpoints = file_checkpoint_read.readlines()
        for checkpoint in checkpoints:
            a, b = checkpoint.split(" ")
            var.CHECKPOINTS.append((int(a), int(b)))

    update_cars_parameters()
    if SETTINGS.x is not None:
        SETTINGS.update_parameters()
    load_explosions()


def update_cars_parameters():
    var.NB_CARS = var.LIST_NB_CARS[var.NUM_MAP]
    var.TIME_GENERATION = var.LIST_TIME_GENERATION[var.NUM_MAP]
    var.SEED = var.LIST_SEED[var.NUM_MAP]
    var.MAX_SPEED = var.LIST_MAX_SPEED[var.NUM_MAP]
    var.MIN_MEDIUM_SPEED = var.MAX_SPEED / 3
    var.MIN_HIGH_SPEED = var.MAX_SPEED / 1.5
    var.TURN_ANGLE = var.LIST_TURN_ANGLE[var.NUM_MAP]
    var.ACCELERATION = var.LIST_ACCELERATION[var.NUM_MAP]
    var.DECELERATION = var.LIST_DECELERATION[var.NUM_MAP]
    var.DRIFT_FACTOR = var.LIST_DRIFT_FACTOR[var.NUM_MAP]
    var.WIDTH_CONE = var.LIST_WIDTH_CONE[var.NUM_MAP]
    var.LENGTH_CONE = var.LIST_LENGTH_CONE[var.NUM_MAP]
    var.CHANCE_CROSSOVER = var.LIST_CHANCE_CROSSOVER[var.NUM_MAP]
    var.CHANCE_MUTATION = var.LIST_CHANCE_MUTATION[var.NUM_MAP]
    var.PROPORTION_CARS_KEPT = var.LIST_PROPORTION_CARS_KEPT[var.NUM_MAP]


def create_background():
    var.BACKGROUND = pygame.Surface((var.WIDTH_SCREEN, var.HEIGHT_SCREEN))
    var.BACKGROUND.fill((128, 128, 128))
    edit_background()
    blit_circuit()


def blit_circuit():
    if not var.SHOW_HEATMAP or var.NUM_MAP == 5:
        var.BACKGROUND.blit(
            scale_image(pygame.image.load(f"{PATH_IMAGE}background/background_{str(var.NUM_MAP)}.png")),
            convert_to_new_window((0, 115)),
        )
    else:
        var.BACKGROUND.blit(
            scale_image(pygame.image.load(f"{PATH_IMAGE}background/heatmap_{str(var.NUM_MAP)}.png")),
            convert_to_new_window((0, 115)),
        )


def load_parameters():
    with open(PATH_DATA + "num_camera", "r") as file_num_camera_read:
        var.NUM_CAMERA = int(file_num_camera_read.readline())

    with open(PATH_DATA + "parameters_map", "r") as file_parameters_read:
        lines = file_parameters_read.readlines()
        actual_map = -1
        for line in lines:
            if line[0] == "#":
                actual_map += 1
            else:
                line_split = line.split()
                if line_split:
                    param = line.split()[0]
                    if param == "nombre_voitures":
                        var.LIST_NB_CARS[actual_map] = int(line.split()[2])
                    elif param == "temps_par_generation":
                        var.LIST_TIME_GENERATION[actual_map] = int(line.split()[2])
                    elif param == "seed":
                        var.LIST_SEED[actual_map] = int(line.split()[2])
                    elif param == "vitesse_max":
                        var.LIST_MAX_SPEED[actual_map] = int(line.split()[2])
                    elif param == "angle_rotation":
                        var.LIST_TURN_ANGLE[actual_map] = int(line.split()[2])
                    elif param == "force_acceleration":
                        var.LIST_ACCELERATION[actual_map] = float(line.split()[2])
                    elif param == "force_freinage":
                        var.LIST_DECELERATION[actual_map] = float(line.split()[2])
                    elif param == "coef_derapage":
                        var.LIST_DRIFT_FACTOR[actual_map] = float(line.split()[2])
                    elif param == "largeur_cone":
                        var.LIST_WIDTH_CONE[actual_map] = int(line.split()[2])
                    elif param == "longueur_cone":
                        var.LIST_LENGTH_CONE[actual_map] = int(line.split()[2])
                    elif param == "chance_croisement":
                        var.LIST_CHANCE_CROSSOVER[actual_map] = float(line.split()[2])
                    elif param == "chance_mutation":
                        var.LIST_CHANCE_MUTATION[actual_map] = float(line.split()[2])
                    elif param == "proportion_selection":
                        var.LIST_PROPORTION_CARS_KEPT[actual_map] = float(line.split()[2])


def load_cars():
    with open(PATH_DATA + "cars", "r") as file_cars_read:
        lines = file_cars_read.readlines()
        for line in lines:
            line = line.split(" ")

            id_car = int(line[0])
            name = line[1]
            color = line[2]
            genetic = Genetic([int(line[i]) for i in range(3, 9)])
            scores = [int(line[i]) for i in range(9, 9 + var.NB_MAPS)]

            var.MEMORY_CARS.append(MemoryCar(id_car, name, color, genetic, scores))
            if var.ACTUAL_IDS_MEMORY_CARS <= id_car:
                var.ACTUAL_IDS_MEMORY_CARS = id_car + 1

    var.BIG_RED_CAR_IMAGE = pygame.transform.rotate(scale_image(pygame.image.load(PATH_IMAGE + "/car.png"), 1.5), 90)


def save_cars():
    with open(PATH_DATA + "cars", "w") as file_cars_write:
        for memory_car in var.MEMORY_CARS:
            str_to_write = f"{memory_car.id} {memory_car.name} {memory_car.color} {memory_car.genetic}"
            for score in memory_car.best_scores:
                str_to_write += f" {int(score)}"  # cast: map 5 scores can be floats
            str_to_write += "\n"
            file_cars_write.write(str_to_write)


def exit_game():
    save_cars()
    sys.exit()


def checkpoint_reached(pos, checkpoint):
    return (
        checkpoint[0] - var.RADIUS_CHECKPOINT < pos[0] < checkpoint[0] + var.RADIUS_CHECKPOINT
        and checkpoint[1] - var.RADIUS_CHECKPOINT < pos[1] < checkpoint[1] + var.RADIUS_CHECKPOINT
    )
