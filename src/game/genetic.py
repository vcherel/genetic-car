import random

import data.variables as var


class Genetic:
    def __init__(self, list_parameters=None):
        if list_parameters is None:
            self.dice_values = [random.randint(1, 6) for _ in range(6)]
        else:
            self.dice_values = list_parameters.copy()

    def __str__(self):
        str_to_return = ""
        for value in self.dice_values:
            str_to_return += str(value) + " "
        return str_to_return[:-1]

    def __eq__(self, other):
        return self.dice_values == other.dice_values

    def copy(self):
        return Genetic(self.dice_values)

    def length_slow(self):
        return self.dice_values[0] * var.LENGTH_CONE

    def length_medium(self):
        return self.dice_values[1] * var.LENGTH_CONE

    def length_fast(self):
        return self.dice_values[2] * var.LENGTH_CONE

    def width_slow(self):
        return self.dice_values[3] * var.WIDTH_CONE

    def width_medium(self):
        return self.dice_values[4] * var.WIDTH_CONE

    def width_fast(self):
        return self.dice_values[5] * var.WIDTH_CONE
