import pygame

import data.variables as var


def convert_to_new_window(x):
    if isinstance(x, float):
        return x * var.WIDTH_SCREEN * var.HEIGHT_SCREEN / (1500 * 700)
    elif len(x) == 2:
        return int(x[0] * var.WIDTH_SCREEN / 1500), int(x[1] * var.HEIGHT_SCREEN / 700)
    else:
        return (
            int(x[0] * var.WIDTH_SCREEN / 1500),
            int(x[1] * var.HEIGHT_SCREEN / 700),
            int(x[2] * var.SCALE_RESIZE_X),
            int(x[3] * var.SCALE_RESIZE_Y),
        )


def scale_image(img, factor=None):
    if factor is None:
        x, y = var.SCALE_RESIZE_X, var.SCALE_RESIZE_Y
    elif isinstance(factor, float) or isinstance(factor, int):
        x, y = factor, factor
    else:
        x, y = factor[0], factor[1]

    size = round(img.get_width() * x), round(img.get_height() * y)
    return pygame.transform.scale(img, size)


def scale_positions(x, y, positions, factor):
    new_positions = []
    for i, position in enumerate(positions):
        new_positions.append(convert_to_new_window((x + int(position[0] * factor), y + int(position[1] * factor))))
    return new_positions
