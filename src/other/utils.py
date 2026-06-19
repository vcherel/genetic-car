import math

import pygame


def compute_detection_cone_points(angle, front_of_car, width, length):
    angle_cone = math.degrees(math.atan(width / (2 * length)))
    top = (
        front_of_car[0] + math.cos(math.radians(angle)) * length,
        front_of_car[1] - math.sin(math.radians(angle)) * length,
    )
    left = (
        front_of_car[0] + math.cos(math.radians(angle + angle_cone)) * length,
        front_of_car[1] - math.sin(math.radians(angle + angle_cone)) * length,
    )
    right = (
        front_of_car[0] + math.cos(math.radians(angle - angle_cone)) * length,
        front_of_car[1] - math.sin(math.radians(angle - angle_cone)) * length,
    )
    return [left, top, right]


def point_out_of_window(point):
    return point[0] < 0 or point[0] >= 1500 or point[1] < 0 or point[1] >= 700


def union_rect(rects):
    if len(rects) == 0:
        return pygame.Rect(0, 0, 0, 0)
    elif len(rects) == 1:
        return rects[0]

    offset = 5
    return_rect = pygame.Rect(min([rect.x for rect in rects]), min([rect.y for rect in rects]), 0, 0)
    return_rect.width = max([rect.x + rect.width for rect in rects]) - return_rect.x + 2 * offset
    return_rect.height = max([rect.y + rect.height for rect in rects]) - return_rect.y + 2 * offset
    return_rect.x -= offset
    return_rect.y -= offset
    return return_rect


def text_rec(text, pos):
    rect = text.get_rect()
    rect.x, rect.y = pos[0], pos[1]
    return rect


def change_color_car(image, str_color):
    if str_color == "red":
        return image

    new_image = pygame.Surface(image.get_size(), flags=image.get_flags(), depth=image.get_bitsize()).convert_alpha()

    for x in range(image.get_width()):
        for y in range(image.get_height()):
            color = image.get_at((x, y))

            if color.a != 0:
                average_value = sum(color[:3]) // 3

                if str_color == "black":
                    r, g, b = average_value // 2, average_value // 2, average_value // 2
                elif str_color == "blue":
                    r, g, b = 0, 0, average_value
                elif str_color == "brown":
                    orange_value = min(average_value, 255)
                    r, g, b = orange_value, orange_value // 2, 0
                elif str_color == "gray":
                    r, g, b = average_value, average_value, average_value
                elif str_color == "green":
                    r, g, b = 0, average_value, 0
                elif str_color == "light_blue":
                    light_blue_value = min(average_value + 100, 255)
                    r, g, b = 0, light_blue_value, light_blue_value
                elif str_color == "light_gray":
                    light_gray_value = min(average_value + 75, 255)
                    r, g, b = light_gray_value, light_gray_value, light_gray_value
                elif str_color == "light_green":
                    light_green_value = min(average_value + 100, 255)
                    r, g, b = 0, light_green_value, 0
                elif str_color == "orange":
                    orange_value = min(average_value + 125, 255)
                    r, g, b = orange_value, orange_value // 2, 0
                elif str_color == "pink":
                    pink_value = min(average_value + 100, 255)
                    r, g, b = pink_value, 0, pink_value
                elif str_color == "purple":
                    r, g, b = average_value, 0, average_value
                elif str_color == "yellow":
                    yellow_value = min(average_value + 50, 255)
                    r, g, b = yellow_value, yellow_value, 0
                else:
                    r, g, b = 0, 0, 0

                new_image.set_at((x, y), (r, g, b, color.a))

    return new_image


def create_rect_from_points(points):
    if not points:
        return None

    min_x = max_x = points[0][0]
    min_y = max_y = points[0][1]

    for point in points:
        x, y = point
        min_x = min(min_x, x)
        max_x = max(max_x, x)
        min_y = min(min_y, y)
        max_y = max(max_y, y)

    return pygame.Rect(min_x, min_y, max_x - min_x, max_y - min_y)


def add_offset_to_rect(rect, offset):
    return pygame.Rect(rect.x - offset, rect.y - offset, rect.width + 2 * offset, rect.height + 2 * offset)
