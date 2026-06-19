import itertools
import random

import data.variables as var
from data.data_classes import MemoryCar
from game.car import Car
from menus.garage_menu import GARAGE


def apply_genetic(cars):
    cars = [car for car in cars if not car.id_memory_car]

    if cars:
        cars = sorted(cars, key=lambda c: c.score, reverse=True)

        cars_to_keep = find_cars_to_keep(cars)
        cars = init_cars(cars_to_keep, var.NB_CARS - len(cars_to_keep))

        if var.TEST_MUTATION_CROSSOVER:
            cars = apply_genetic_test(cars, cars_to_keep)
        else:
            crossover(cars)
            cars = mutate(cars, cars_to_keep)
        add_cars_to_keep(cars, cars_to_keep)
    else:
        cars = [Car() for _ in range(var.NB_CARS)]

    return cars


def find_cars_to_keep(cars):
    number_to_keep = max(min(int(var.PROPORTION_CARS_KEPT * len(cars)), var.NB_CARS), 1)
    cars_to_keep = cars[:number_to_keep]

    best_car = cars_to_keep[0]
    var.MEMORY_CARS.append(
        MemoryCar(
            id_car=var.ACTUAL_IDS_MEMORY_CARS,
            name=f"Génération_{var.NUM_GENERATION}",
            color="gray",
            genetic=best_car.genetic,
            best_scores=best_car.best_scores,
        )
    )
    var.ACTUAL_IDS_MEMORY_CARS += 1
    GARAGE.reload_page = True

    return cars_to_keep


def init_cars(cars_to_keep, number_cars):
    weights = [car.score for car in cars_to_keep]
    total_weight = sum(weights)
    if total_weight == 0:
        total_weight = 1
    probabilities = [weight / total_weight for weight in weights]

    selected_cars = random.choices(cars_to_keep, probabilities, k=number_cars)
    return [car.copy() for car in selected_cars]


def apply_genetic_test(cars, cars_to_keep):
    if var.TEST_MODE == "mutation_only":
        cars = mutate(cars, cars_to_keep)
    elif var.TEST_MODE == "crossover_mutation":
        crossover(cars)
        cars = mutate(cars, cars_to_keep)
    return cars


def crossover(cars):
    for car1, car2 in itertools.combinations(cars, 2):
        if random.random() < var.CHANCE_CROSSOVER and car1 != car2:
            ids_changed_attributes = random.sample(range(0, 6), random.randint(1, 6))
            for i, value in enumerate(car1.genetic.dice_values):
                if i in ids_changed_attributes:
                    car1.genetic.dice_values[i], car2.genetic.dice_values[i] = car2.genetic.dice_values[i], value


def mutate(cars, cars_to_keep):
    new_cars = []

    for car in cars:
        added = False
        while not added:
            mutate_one_car(car)
            if car not in new_cars and car not in cars_to_keep:
                added = True
                new_cars.append(car)

    return new_cars


def mutate_one_car(car):
    has_muted = False
    while not has_muted:
        dice_values = car.genetic.dice_values.copy()
        for index, value in enumerate(car.genetic.dice_values):
            if random.random() < var.CHANCE_MUTATION:
                has_muted = True
                dice_values[index] = random_attribution(value)
        car.genetic.dice_values = dice_values


def random_attribution(value):
    random_value = random.random()
    if random_value < 1 / 5:
        value = value + random.uniform(-5, 5)
    elif random_value < 1 / 4:
        value = value + random.uniform(-4, 4)
    elif random_value < 1 / 3:
        value = value + random.uniform(-3, 3)
    elif random_value < 1 / 2:
        value = value + random.uniform(-2, 2)
    else:
        value = value + random.uniform(-1, 1)
    return max(1, min(6, round(value)))


def add_cars_to_keep(cars, cars_to_keep):
    for car in cars_to_keep[1:]:
        cars.append(Car(genetic=car.genetic, best_scores=car.best_scores))

    best_car = cars_to_keep[0]
    cars.append(Car(genetic=best_car.genetic, best_scores=best_car.best_scores, color="yellow"))
