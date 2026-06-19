import random
from typing import Optional

import cv2
import numpy as np
import pygame

import data.variables as var
from data.constants import PATH_DATA
from data.data_classes import ColorDice
from other.camera_utils import (
    add_offset,
    circles_too_close,
    compute_mean_bgr,
    overlapping_rectangles,
    update_pygame_camera_frame,
    verif_coordinates,
)
from render.resizing import convert_to_new_window

memory_rects = {}
colors = {}
memory_circles = {"yellow": {}, "orange": {}, "red": {}, "dark_yellow": {}, "green": {}, "black": {}}
scores_colors = {"yellow": [], "orange": [], "red": [], "dark_yellow": [], "green": [], "black": []}

frame_view = np.empty([2, 2])
frame = np.empty([2, 2])

count_iterations = 0

param_1, param_2, param_dp = 150, 16, 5
max_radius_circle = 7

write_mean_bgr = False
file_write_mean_bgr = None

optimize_hough_circle = False
p1_min, p1_max = 50, 200
p2_min, p2_max = 10, 80
dp_min, dp_max = 30, 150
theorical_values = {}
theorical_coordinates = {}
wait_optimize = 100
dict_p1_opti, dict_p2_opti, dict_dp_opti = {}, {}, {}

cap: Optional[cv2.VideoCapture] = None


def change_camera(first_time=False):
    global cap

    cap = cv2.VideoCapture(var.NUM_CAMERA)

    if not first_time:
        with open(PATH_DATA + "num_camera", "w") as file_write:
            file_write.write(str(var.NUM_CAMERA))


def capture_dice():
    global frame_view, frame

    final_score = {
        "yellow": random.randint(1, 6),
        "orange": random.randint(1, 6),
        "red": random.randint(1, 6),
        "dark_yellow": random.randint(1, 6),
        "green": random.randint(1, 6),
        "black": random.randint(1, 6),
    }

    rect_window = pygame.rect.Rect(convert_to_new_window((425, 175, 640, 480)))

    while True:
        res = find_dice_values(final_score)
        if res is not None:
            return res

        display_frame(rect_window)

        if count_iterations == wait_optimize and optimize_hough_circle:
            display_dictionaries_optimization()

        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                var.WINDOW.blit(var.BACKGROUND, rect_window, rect_window)

                frame_view = cv2.cvtColor(frame_view, cv2.COLOR_BGR2RGB)
                update_pygame_camera_frame(frame_view)

                return list(final_score.values())


def find_dice_values(final_score):
    global count_iterations, frame_view, frame, colors

    count_iterations += 1

    _, frame = cap.read()

    if frame is None:
        print("Aucune caméra détectée")
        return list(final_score.values())

    frame_view = frame.copy()

    rectangles = find_rectangles()

    colors = {}

    for rect in rectangles:
        find_colors(rect)

    for color in colors:
        draw_score(color, final_score)


def find_rectangles():
    contours = find_contours(frame)
    rectangles = get_rectangles_from_contours(contours)
    rectangles = add_offset(rectangles, offset=7)
    rectangles = add_rect_from_memory(rectangles)
    update_memory(memory_rects)
    return rectangles


def find_contours(image):
    param_thresh = {"yellow": 170, "orange": 90, "red": 60, "dark_yellow": 100, "green": 80, "black": 20}

    contours = []

    for str_color, value in param_thresh.items():
        gray_img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray_img = cv2.medianBlur(gray_img, 3)

        thresh = cv2.threshold(gray_img, value, 255, cv2.THRESH_BINARY_INV)[1]
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))

        edges_1 = cv2.Canny(gray_img, 9, 150, 3)
        edges_2 = cv2.Canny(thresh, 9, 150, 3)

        for edges in [edges_1, edges_2]:
            close = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel, iterations=2)
            contour_found, _ = cv2.findContours(close, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            contours += contour_found

    return contours


def get_rectangles_from_contours(contours):
    rectangles = []
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)

        if valid_rectangle(x, y, w, h):
            rectangle_already_in_list = False
            for rectangle in rectangles:
                if overlapping_rectangles((x, y, w, h), rectangle, area_threshold=0.6):
                    rectangle_already_in_list = True
                    if w * h > rectangle[2] * rectangle[3]:
                        rectangles.remove(rectangle)
                        rectangles.append((x, y, w, h))
                    break

            if not rectangle_already_in_list:
                rectangles.append((x, y, w, h))

    return rectangles


def valid_rectangle(x, y, w, h, min_size=40, max_size=75):
    return min_size < w < max_size and min_size < h < max_size and x > 5 and y > 5 and x + w < 635 and y + h < 475


def add_rect_from_memory(rectangles, lifetime=25, area_threshold=0.9):
    new_rectangles = list(memory_rects.keys())

    for rectangle in rectangles:
        rect_already_in_memory = False

        for memory_rect in memory_rects:
            if overlapping_rectangles(rectangle, memory_rect, area_threshold):
                rect_already_in_memory = True
                memory_rects[memory_rect] = lifetime
                break

        if not rect_already_in_memory:
            new_rectangles.append(rectangle)
            memory_rects[rectangle] = lifetime

    return new_rectangles


def search_rectangle(rect, rectangles):
    for rectangle in rectangles:
        if (
            overlapping_rectangles(rect, rectangle, area_threshold=0.6)
            and rect[2] * rect[3] < rectangle[2] * rectangle[3]
        ):
            return rectangle
    return rect


def update_memory(memory):
    memory_to_delete = []
    for key in memory:
        memory[key] -= 1
        if memory[key] == 0:
            memory_to_delete.append(key)

    for key in memory_to_delete:
        del memory[key]


def find_colors(rect):
    x, y, w, h = rect
    image = frame[y : y + h, x : x + w]

    mean_bgr = compute_mean_bgr(image)

    if write_mean_bgr:
        write_mean_bgr_value(rect, mean_bgr)

    determine_color(ColorDice(mean_bgr, rect))


def determine_color(color_dice):
    bgr_values = {
        "yellow": (49, 113, 149),
        "orange": (44, 66, 169),
        "red": (50, 35, 111),
        "dark_yellow": (41, 73, 121),
        "green": (70, 93, 41),
        "black": (44, 38, 39),
    }

    if not color_dice.distances:
        color_dice.distances = {}
        for name, bgr in bgr_values.items():
            color_dice.distances[name] = np.linalg.norm(color_dice.color - bgr)

    if color_dice.bad_colors is None:
        name_color = min(color_dice.distances, key=color_dice.distances.get)
    else:
        min_distance = None
        name_color = ""
        for name, distance in color_dice.distances.items():
            if name not in color_dice.bad_colors and (min_distance is None or distance < min_distance):
                min_distance = distance
                name_color = name
        if min_distance is None:
            return

    if name_color not in colors:
        colors[name_color] = color_dice
    else:
        if np.linalg.norm(colors[name_color].color - bgr_values[name_color]) > np.linalg.norm(
            color_dice.color - bgr_values[name_color]
        ):
            old_dice = colors[name_color]
            colors[name_color] = color_dice
            old_dice.bad_colors.append(name_color)
            determine_color(old_dice)
        else:
            color_dice.bad_colors.append(name_color)
            determine_color(color_dice)


def write_mean_bgr_value(rect, mean_bgr):
    global file_write_mean_bgr

    if file_write_mean_bgr is None:
        file_write_mean_bgr = open(PATH_DATA + "mean_bgr", "a")

    rect_detection = (250, 150, 150, 150)
    draw_rectangle(rect_detection, color=(0, 255, 0), thickness=1)
    if overlapping_rectangles(rect, rect_detection, area_threshold=0.1):
        draw_rectangle(rect, color=(255, 0, 0), thickness=20)
        file_write_mean_bgr.write(f"{mean_bgr[0]} {mean_bgr[1]} {mean_bgr[2]}\n")


def draw_score(color, final_score):
    real_bgr_values = {
        "yellow": (0, 255, 255),
        "orange": (0, 102, 204),
        "red": (0, 0, 204),
        "dark_yellow": (0, 152, 152),
        "green": (0, 204, 0),
        "black": (0, 0, 0),
    }

    rect = x, y, w, h = colors[color].rect
    image = frame[y : y + h, x : x + w]

    if np.size(image) == 0:
        return None

    draw_rectangle((x, y, w, h), real_bgr_values[color])

    score = determine_score(image, rect, color, scores_colors[color])

    if color in final_score:
        final_score[color] = score

    cv2.putText(frame_view, f"Score: {score}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (50, 50, 50), 2)


def determine_score(image, rect, color, scores, len_memory=40):
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    circles = find_circles(gray_image, color)

    if count_iterations == wait_optimize and optimize_hough_circle:
        if color in theorical_values:
            optimize_parameters(gray_image, color, rect)

    if circles:
        score = len(circles)

        circles_to_draw = []
        for circle in circles:
            circles_to_draw.append((circle[0] + rect[0], circle[1] + rect[1], circle[2]))

        draw_circle(circles_to_draw)
    else:
        score = random.randint(1, 6)

    if score > 6:
        score = 6

    scores.append(score)
    if len(scores) > len_memory:
        scores.pop(0)

    score = max(set(scores), key=scores.count)

    return score


def find_circles(gray_image, color):
    circles = []
    circles = add_circles(circles, gray_image)

    blur_image = cv2.medianBlur(gray_image, 3)
    circles = add_circles(circles, blur_image)

    canny_image = cv2.Canny(gray_image, 50, 120)
    circles = add_circles(circles, canny_image)

    circles = add_circle_from_memory(circles, color)

    update_memory(memory_circles[color])

    return circles


def add_circles(actual_circles, image):
    new_circles = cv2.HoughCircles(
        image=image,
        method=cv2.HOUGH_GRADIENT,
        dp=param_dp / 10,
        minDist=3,
        param1=param_1,
        param2=param_2,
        minRadius=0,
        maxRadius=max_radius_circle,
    )

    if new_circles is not None:
        new_circles = [tuple(new_circle.tolist()) for new_circle in new_circles[0, :]]

        for circle_to_add in new_circles:
            circle_already_in_list = False

            for circle in actual_circles:
                if circles_too_close(circle, circle_to_add):
                    circle_already_in_list = True
                    break

            if not circle_already_in_list:
                actual_circles.append(circle_to_add)

    return actual_circles


def add_circle_from_memory(circles, color, lifetime=30):
    new_circles = list(memory_circles[color].keys())

    for circle in circles:
        circle_already_in_memory = False

        for memory_circle in memory_circles[color]:
            if circles_too_close(circle, memory_circle):
                circle_already_in_memory = True
                memory_circles[color][memory_circle] = lifetime
                break

        if not circle_already_in_memory:
            new_circles.append(circle)
            memory_circles[color][circle] = lifetime

    return new_circles


def optimize_parameters(image, color, rect):
    for p1 in range(p1_min, p1_max + 1):
        for p2 in range(p2_min, p2_max + 1):
            for dp in range(dp_min, dp_max + 1):
                if p1 > p2:
                    optimize_hough_circles(image, color, rect, p1, p2, dp)


def optimize_hough_circles(image, color, rect, p1, p2, dp):
    c = cv2.HoughCircles(
        image=image,
        method=cv2.HOUGH_GRADIENT,
        dp=dp / 10,
        minDist=5,
        param1=p1,
        param2=p2,
        minRadius=1,
        maxRadius=max_radius_circle,
    )
    if c is not None and verif_coordinates(c[0, :], rect, theorical_coordinates[color]):
        if p1 not in dict_p1_opti:
            dict_p1_opti[p1] = 1
        else:
            dict_p1_opti[p1] += 1
        if p2 not in dict_p2_opti:
            dict_p2_opti[p2] = 1
        else:
            dict_p2_opti[p2] += 1
        if dp not in dict_dp_opti:
            dict_dp_opti[dp] = 1
        else:
            dict_dp_opti[dp] += 1


def display_dictionaries_optimization():
    global dict_p1_opti, dict_p2_opti, dict_dp_opti

    dict_p1_opti = {k: v for k, v in sorted(dict_p1_opti.items(), key=lambda item: item[1], reverse=True)}
    dict_p2_opti = {k: v for k, v in sorted(dict_p2_opti.items(), key=lambda item: item[1], reverse=True)}
    dict_dp_opti = {k: v for k, v in sorted(dict_dp_opti.items(), key=lambda item: item[1], reverse=True)}

    with open(PATH_DATA + "optimization", "w") as file_write:
        file_write.write(f"p1 : {dict_p1_opti}\np2 : {dict_p2_opti}\ndp : {dict_dp_opti}")


def draw_rectangle(rectangle, color=(0, 0, 0), thickness=3):
    if isinstance(rectangle, tuple):
        rectangle = [rectangle]
    for rect in rectangle:
        x, y, w, h = rect
        cv2.rectangle(frame_view, (x, y), (x + w, y + h), color, thickness)


def draw_circle(circles):
    for circle in circles:
        cv2.circle(frame_view, (int(circle[0]), int(circle[1])), int(circle[2]), (0, 255, 0), 2)
        cv2.circle(frame_view, (int(circle[0]), int(circle[1])), 2, (0, 0, 255), 3)


def display_frame(rect_window):
    image_rgb = cv2.cvtColor(frame_view, cv2.COLOR_BGR2RGB)
    image_pygame = pygame.surfarray.make_surface(image_rgb)
    image_turned = pygame.transform.rotate(image_pygame, -90)
    image = pygame.transform.flip(image_turned, True, False)
    image = pygame.transform.scale(image, (rect_window.width, rect_window.height))
    var.WINDOW.blit(image, rect_window)
    pygame.draw.rect(var.WINDOW, (1, 1, 1), rect_window, 2)
    var.WINDOW.blit(
        var.LARGE_FONT.render("Cliquez n'importe où pour quitter cette fenêtre", True, (255, 0, 255)),
        convert_to_new_window((440, 600)),
    )
    pygame.display.flip()


def end_capture_dice(final_score):
    cv2.destroyAllWindows()
    return list(final_score.values())
