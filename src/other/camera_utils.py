import math
import warnings

import numpy as np
import pygame

import data.variables as var
from render.resizing import convert_to_new_window


def verif_coordinates(circles, rect, coordinates):
    x, y = rect[:2]
    for circle in circles:
        circle_found = False
        for pos in coordinates:
            if pos[0] - 5 < circle[0] + x < pos[0] + 5 and pos[1] - 5 < circle[1] + y < pos[1] + 5:
                circle_found = True
                break
        if not circle_found:
            return False
    return True


def add_offset(rectangles, offset):
    new_rectangles = []
    for rectangle in rectangles:
        x, y, w, h = rectangle
        new_rectangles.append((x - offset, y - offset, w + 2 * offset, h + 2 * offset))
    return new_rectangles


def overlapping_rectangles(rect1, rect2, area_threshold):
    x1, y1, w1, h1 = rect1
    x2, y2, w2, h2 = rect2

    x_left = max(x1, x2)
    y_top = max(y1, y2)
    x_right = min(x1 + w1, x2 + w2)
    y_bottom = min(y1 + h1, y2 + h2)

    if x_right <= x_left or y_bottom <= y_top:
        return False

    area1 = w1 * h1
    area2 = w2 * h2
    intersection_area = (x_right - x_left) * (y_bottom - y_top)

    return intersection_area > area_threshold * min(area1, area2)


def circles_too_close(circle1, circle2, distance_threshold=7):
    x1, y1, _ = circle1
    x2, y2, _ = circle2
    distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    return distance <= distance_threshold


def compute_mean_bgr(image):
    threshold_distance = 150
    white = np.array([200, 200, 200])
    array = np.array(image)

    mask = np.linalg.norm(array - white, axis=2) > threshold_distance
    new_list = array[mask]

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=RuntimeWarning)
        mean_bgr = np.mean(new_list, axis=0)

    return mean_bgr


def update_pygame_camera_frame(frame):
    frame = pygame.surfarray.make_surface(frame)

    var.CAMERA_FRAME = pygame.transform.flip(
        pygame.transform.rotate(
            pygame.transform.scale(frame, (int(frame.get_width() * 0.75), int(frame.get_height() * 0.75))), -90
        ),
        True,
        False,
    )

    var.RECT_CAMERA_FRAME = var.CAMERA_FRAME.get_rect()
    var.RECT_CAMERA_FRAME.x, var.RECT_CAMERA_FRAME.y = 0, 200

    var.RECT_CAMERA_FRAME = pygame.rect.Rect(convert_to_new_window(var.RECT_CAMERA_FRAME))
    var.CAMERA_FRAME = pygame.transform.scale(
        var.CAMERA_FRAME, (var.RECT_CAMERA_FRAME.width, var.RECT_CAMERA_FRAME.height)
    )
