import itertools
import random
import time
import traceback

import pygame

import data.variables as var
import render.display as display
import render.ui as ui
from data.constants import PATH_DATA, PATH_IMAGE
from data.variables_functions import blit_circuit, change_map, exit_game, init_variables, load_cars, load_parameters
from game.car import Car, add_garage_cars
from game.genetic import Genetic
from game.genetic_algorithm import apply_genetic
from menus.settings_menu import SETTINGS
from other.camera import change_camera
from other.utils import union_rect


def open_window():
    var.WINDOW.blit(var.BACKGROUND, (0, 0))

    while 1:
        if var.CHANGE_CHECKPOINTS:
            change_checkpoints()

        ui.handle_events()
        ui.erase()
        ui.display()

        if var.SHOW_CHECKPOINTS:
            display.show_checkpoints()

        pygame.display.flip()

        if var.START:
            play()

        var.CLOCK.tick(25)


def play(cars=None):
    blit_circuit()
    cars = init_cars_to_play(cars)

    while var.PLAY:
        ui.handle_events(cars)

        if not var.PAUSE and not var.FPS_TOO_HIGH:
            play_turn(cars)

            var.EXPLOSIONS.draw(var.WINDOW)
            var.EXPLOSIONS.update()

            if var.PLAY_LAST_RUN:
                replay_last_run()

            if var.NB_CARS_ALIVE == 0 or var.TICKS_REMAINING == 0 or var.CHANGE_GENERATION:
                stop_play(cars)
                if var.TEST_ALL_CARS:
                    return
                if (var.TEST_VALUE_GENETIC_PARAMETERS or var.TEST_MUTATION_CROSSOVER) and var.TEST_FINISHED:
                    return

        ui.erase()
        ui.display(cars)

        pygame.display.flip()

        update_fps()

    open_window()


def init_cars_to_play(cars):
    random.seed(var.SEED)

    if not cars:
        cars = []
        for i in range(var.NB_CARS):
            added = False
            while not added:
                car = Car()
                if car not in cars:
                    added = True
                    cars.append(car)

        cars = add_garage_cars(cars)
        init_variables(len(cars))
    else:
        cars = add_garage_cars(cars)
        init_variables(len(cars), replay=True)

    return cars


def play_turn(cars):
    var.TIME_LAST_TURN = time.time()

    rect_blit_car = union_rect(var.RECTS_BLIT_CAR)
    var.WINDOW.blit(var.BACKGROUND, rect_blit_car, rect_blit_car)
    var.RECTS_BLIT_CAR = []

    rect_blit_explosion = union_rect(var.RECTS_BLIT_EXPLOSION)
    var.WINDOW.blit(var.BACKGROUND, rect_blit_explosion, rect_blit_explosion)
    var.RECTS_BLIT_EXPLOSION = []

    if var.SHOW_CHECKPOINTS:
        display.show_checkpoints()

    for car in cars:
        if not car.dead:
            car.move()
            car.draw()

    var.TICKS_REMAINING -= 1


def replay_last_run():
    var.WINDOW.blit(var.BACKGROUND, (0, 0))
    var.PLAY_LAST_RUN = False
    var.NUM_GENERATION -= 1

    cars = []
    for car in var.CARS_LAST_RUN:
        car.reset()
        cars.append(car)
    play(cars)


def stop_play(cars):
    time_before = time.time()

    if not var.TEST_MUTATION_CROSSOVER and not var.TEST_ALL_CARS:
        while time.time() - time_before < 1:
            rect_blit_explosion = union_rect(var.RECTS_BLIT_EXPLOSION)
            var.WINDOW.blit(var.BACKGROUND, rect_blit_explosion, rect_blit_explosion)
            var.RECTS_BLIT_EXPLOSION = []

            rect_blit_car = union_rect(var.RECTS_BLIT_CAR)
            var.WINDOW.blit(var.BACKGROUND, rect_blit_car, rect_blit_car)
            var.RECTS_BLIT_CAR = []

            for car in cars:
                car.draw()

            var.EXPLOSIONS.draw(var.WINDOW)
            var.EXPLOSIONS.update()

            ui.handle_events(cars)
            ui.erase()
            ui.display(cars)

            pygame.display.flip()

    var.CHANGE_GENERATION = False
    var.WINDOW.blit(var.BACKGROUND, (0, 0))

    var.CARS_LAST_RUN = cars
    if var.LAST_RUN_PLAYING:
        var.PLAY_LAST_RUN = False

    if var.TEST_ALL_CARS:
        for car in cars:
            var.FILE_TEST.write(f"{car.genetic} {car.score}\n")
        return

    else:
        if var.TEST_MUTATION_CROSSOVER or var.TEST_VALUE_GENETIC_PARAMETERS:
            var.LAP_COMPLETED = False
            for car in cars:
                if car.score > 150:
                    var.FILE_TEST.write(f"{var.NUM_GENERATION}\n")
                    var.TEST_FINISHED = True
                    return
            if var.NUM_GENERATION > 24:
                var.FILE_TEST.write(f"{var.NUM_GENERATION}\n")
                var.TEST_FINISHED = True
                return

        cars = apply_genetic(cars)
        play(cars)


def update_fps():
    try:
        var.ACTUAL_FPS = int(1 / (time.time() - var.TIME_LAST_TURN))
    except ZeroDivisionError:
        var.ACTUAL_FPS = 0

    if time.time() - var.TIME_LAST_TURN < 1 / var.FPS:
        var.ACTUAL_FPS = var.FPS
        var.FPS_TOO_HIGH = True
    else:
        var.FPS_TOO_HIGH = False


def change_checkpoints():
    image_checkpoint = pygame.image.load(f"{PATH_IMAGE}checkpoints/checkpoint.png")
    var.WINDOW.blit(image_checkpoint, (450, 25))
    pygame.display.flip()
    with open(f"{PATH_DATA}checkpoints/{var.NUM_MAP}", "w") as file_checkpoint_write:
        while 1:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit_game()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = event.pos
                    file_checkpoint_write.write(str(x) + " " + str(y) + "\n")


def run_test_all_cars():
    var.FPS = 9999
    var.SHOW_EXPLOSIONS = False

    var.FILE_TEST = open(f"{PATH_DATA}tests/all_cars/results/{var.NUM_MAP}", "w")
    var.WINDOW.blit(var.BACKGROUND, (0, 0))
    var.PLAY = True

    tab_cars = []
    genetic_combinations = itertools.product(range(1, 7), repeat=6)
    for combination in genetic_combinations:
        genetic = Genetic(list(combination))
        tab_cars.append(Car(genetic))
        if len(tab_cars) == 10000:
            play(tab_cars)
            tab_cars = []
    play(tab_cars)


def run_test_mutation_crossover():
    var.WINDOW.blit(var.BACKGROUND, (0, 0))
    var.PLAY = True

    for var.TEST_MODE in ["crossover_mutation"]:
        var.FILE_TEST = open(f"{PATH_DATA}tests/genetic_parameters/{var.TEST_MODE}_{var.NUM_MAP}", "a")
        for var.SEED in range(100, 200):
            play()
            var.NUM_GENERATION = 0


def run_test_value_genetic_parameters():
    var.FPS = 9999
    var.SHOW_EXPLOSIONS = False

    path_test = f"{PATH_DATA}tests/"
    var.WINDOW.blit(var.BACKGROUND, (0, 0))
    var.PLAY = True

    for var.CHANCE_MUTATION, var.CHANCE_CROSSOVER, var.PROPORTION_CARS_KEPT in [(0.3, 0.1, 0.2)]:
        var.FILE_TEST = open(
            f"{path_test}tests/genetic_parameters/{var.CHANCE_MUTATION}_{var.CHANCE_CROSSOVER}_{var.PROPORTION_CARS_KEPT}",
            "a",
        )
        for var.SEED in range(50):
            play()
            var.NUM_GENERATION = 0


def main():
    try:
        load_parameters()
        change_camera(first_time=True)
        change_map(first_time=True)
        load_cars()
        ui.init()
        SETTINGS.init()

        if var.TEST_ALL_CARS:
            run_test_all_cars()
        elif var.TEST_MUTATION_CROSSOVER:
            run_test_mutation_crossover()
        elif var.TEST_VALUE_GENETIC_PARAMETERS:
            run_test_value_genetic_parameters()
        else:
            open_window()

    except Exception as e:
        traceback.print_exc()
        exit_game()
        raise e


if __name__ == "__main__":
    main()
