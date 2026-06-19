import pygame

import data.variables as var
from data.constants import PATH_IMAGE, RGB_VALUES_DICE
from data.variables_functions_ui import add_to_rects_blit_ui
from other.utils import change_color_car, compute_detection_cone_points, text_rec
from render.resizing import convert_to_new_window, scale_image, scale_positions


def edit_background():
    font = pygame.font.SysFont("Arial", int(20 * var.SCALE_RESIZE_X), bold=True)
    var.BACKGROUND.blit(
        font.render("Nombre de voitures", True, (0, 0, 0), (128, 128, 128)), convert_to_new_window((1060, 25))
    )
    pygame.draw.line(var.BACKGROUND, (0, 0, 0), convert_to_new_window((1280, 120)), convert_to_new_window((1280, 0)), 2)
    pygame.draw.line(var.BACKGROUND, (0, 0, 0), convert_to_new_window((325, 120)), convert_to_new_window((325, 0)), 2)
    var.BACKGROUND.blit(scale_image(pygame.image.load(PATH_IMAGE + "map.png")), convert_to_new_window((785, 5)))


def show_checkpoints():
    for checkpoint in var.CHECKPOINTS:
        pygame.draw.circle(
            var.WINDOW, (255, 0, 0), convert_to_new_window(checkpoint), var.RADIUS_CHECKPOINT * var.SCALE_RESIZE_X, 1
        )


def display_text_ui(caption, pos, font, background_color=(128, 128, 128)):
    text = font.render(caption, True, (0, 0, 0), background_color)
    var.WINDOW.blit(text, pos)
    add_to_rects_blit_ui(text_rec(text, pos))


def draw_detection_cone(pos, dice_values, angle=90, factor=1, width_line=2, actual_mode=None):
    pos = convert_to_new_window(pos)
    width_multiplier = var.SCALE_RESIZE_X * var.WIDTH_CONE * factor
    length_multiplier = var.SCALE_RESIZE_Y * var.LENGTH_CONE * factor

    left, top, right = compute_detection_cone_points(
        angle, pos, dice_values[3] * width_multiplier, dice_values[0] * length_multiplier
    )
    points = [pos, left, top, right]
    if actual_mode == "slow":
        pygame.draw.polygon(var.WINDOW, (255, 255, 0), (pos, left, top, right), width_line * 2)
    else:
        pygame.draw.polygon(var.WINDOW, (255, 255, 0), (pos, left, top, right), width_line)

    left, top, right = compute_detection_cone_points(
        angle, pos, dice_values[4] * width_multiplier, dice_values[1] * length_multiplier
    )
    if actual_mode == "medium":
        pygame.draw.polygon(var.WINDOW, (255, 128, 0), (pos, left, top, right), width_line * 2)
    else:
        pygame.draw.polygon(var.WINDOW, (255, 128, 0), (pos, left, top, right), width_line)
    points.append(left)
    points.append(top)
    points.append(right)

    left, top, right = compute_detection_cone_points(
        angle, pos, dice_values[5] * width_multiplier, dice_values[2] * length_multiplier
    )
    if actual_mode == "fast":
        pygame.draw.polygon(var.WINDOW, (255, 0, 0), (pos, left, top, right), width_line * 2)
    else:
        pygame.draw.polygon(var.WINDOW, (255, 0, 0), (pos, left, top, right), width_line)
    points.append(left)
    points.append(top)
    points.append(right)

    return points


def show_car_window(car):
    var.DISPLAY_CAR_WINDOW = True

    rect_x = 300
    rect_y = 190
    rect = pygame.Rect(convert_to_new_window((rect_x, rect_y, 750, 500)))
    pygame.draw.rect(var.WINDOW, (128, 128, 128), rect, 0)
    pygame.draw.rect(var.WINDOW, (1, 1, 1), rect, 2)

    x, y = rect_x + 565, rect_y + 230
    image = change_color_car(var.BIG_RED_CAR_IMAGE, car.color)
    image = scale_image(image, var.SCALE_RESIZE_X)
    var.WINDOW.blit(image, convert_to_new_window((x, y)))

    # Temporarily override cone multipliers so the car window always shows cones at a fixed reference size
    width, length = var.WIDTH_CONE, var.LENGTH_CONE
    var.WIDTH_CONE, var.LENGTH_CONE = 16, 11
    draw_detection_cone((x + 52, y - 3), car.genetic.dice_values, factor=3, width_line=5)
    var.WIDTH_CONE, var.LENGTH_CONE = width, length

    x_distance = 120
    x1 = 160
    x2 = x1 + x_distance
    x3 = x2 + x_distance
    y1, y2 = 225, 350
    draw_dice(
        x=rect_x + x1,
        y=rect_y + y1,
        color=RGB_VALUES_DICE[0],
        value=car.genetic.length_slow() // var.LENGTH_CONE,
        factor=0.75,
        black_dots=True,
    )
    draw_dice(
        x=rect_x + x2,
        y=rect_y + y1,
        color=RGB_VALUES_DICE[1],
        value=car.genetic.length_medium() // var.LENGTH_CONE,
        factor=0.75,
    )
    draw_dice(
        x=rect_x + x3,
        y=rect_y + y1,
        color=RGB_VALUES_DICE[2],
        value=car.genetic.length_fast() // var.LENGTH_CONE,
        factor=0.75,
    )
    draw_dice(
        x=rect_x + x1,
        y=rect_y + y2,
        color=RGB_VALUES_DICE[3],
        value=car.genetic.width_slow() // var.WIDTH_CONE,
        factor=0.75,
    )
    draw_dice(
        x=rect_x + x2,
        y=rect_y + y2,
        color=RGB_VALUES_DICE[4],
        value=car.genetic.width_medium() // var.WIDTH_CONE,
        factor=0.75,
    )
    draw_dice(
        x=rect_x + x3,
        y=rect_y + y2,
        color=RGB_VALUES_DICE[5],
        value=car.genetic.width_fast() // var.WIDTH_CONE,
        factor=0.75,
    )

    var.WINDOW.blit(var.TEXT_SLOW, convert_to_new_window((rect_x + 175, rect_y + 150)))
    var.WINDOW.blit(var.TEXT_MEDIUM, convert_to_new_window((rect_x + 277, rect_y + 150)))
    var.WINDOW.blit(var.TEXT_FAST, convert_to_new_window((rect_x + 400, rect_y + 150)))
    var.WINDOW.blit(var.TEXT_LENGTH, convert_to_new_window((rect_x + 15, rect_y + 250)))
    var.WINDOW.blit(var.TEXT_WIDTH, convert_to_new_window((rect_x + 25, rect_y + 375)))


def erase_car_window():
    var.DISPLAY_CAR_WINDOW = False
    rect = pygame.Rect(convert_to_new_window((300, 190, 750, 500)))
    var.WINDOW.blit(var.BACKGROUND, rect, rect)


def draw_dice(x, y, color, value, factor=1, black_dots=False):
    pygame.draw.rect(var.WINDOW, color, (convert_to_new_window((x, y, int(120 * factor), int(120 * factor)))), 0)
    pygame.draw.rect(
        var.WINDOW, (100, 100, 100), (convert_to_new_window((x, y, int(120 * factor), int(120 * factor)))), 3
    )

    if black_dots:
        draw_dots(x, y, value, factor, (0, 0, 0))
    else:
        draw_dots(x, y, value, factor)


def draw_dots(x, y, nb_dots, factor, color=(255, 255, 255)):
    dot_radius = 10
    dot_offset = 32
    position_dot = []

    if nb_dots == 1:
        position_dot = scale_positions(x, y, [(60, 60)], factor)
    elif nb_dots == 2:
        position_dot = scale_positions(x, y, [(dot_offset, dot_offset), (120 - dot_offset, 120 - dot_offset)], factor)
    elif nb_dots == 3:
        position_dot = scale_positions(
            x, y, [(dot_offset, dot_offset), (60, 60), (120 - dot_offset, 120 - dot_offset)], factor
        )
    elif nb_dots == 4:
        position_dot = scale_positions(
            x,
            y,
            [
                (dot_offset, dot_offset),
                (dot_offset, 120 - dot_offset),
                (120 - dot_offset, dot_offset),
                (120 - dot_offset, 120 - dot_offset),
            ],
            factor,
        )
    elif nb_dots == 5:
        position_dot = scale_positions(
            x,
            y,
            [
                (dot_offset, dot_offset),
                (dot_offset, 120 - dot_offset),
                (120 - dot_offset, dot_offset),
                (120 - dot_offset, 120 - dot_offset),
                (60, 60),
            ],
            factor,
        )
    elif nb_dots == 6:
        position_dot = scale_positions(
            x,
            y,
            [
                (dot_offset, dot_offset),
                (dot_offset, 120 - dot_offset),
                (120 - dot_offset, dot_offset),
                (120 - dot_offset, 120 - dot_offset),
                (dot_offset, 60),
                (120 - dot_offset, 60),
            ],
            factor,
        )

    for dot_pos in position_dot:
        pygame.draw.circle(var.WINDOW, color, dot_pos, int(dot_radius * factor * var.SCALE_RESIZE_X))
