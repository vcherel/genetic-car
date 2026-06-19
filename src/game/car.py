import math

import pygame

import data.variables as var
from data.constants import NB_MAPS
from data.variables_functions import checkpoint_reached
from game.genetic import Genetic
from other.utils import change_color_car, compute_detection_cone_points, create_rect_from_points, point_out_of_window
from render.display import draw_detection_cone
from render.explosion import Explosion
from render.resizing import convert_to_new_window, scale_image

MIN_SPEED = 1
ADD_TO_SPEED_ANGLE = 2
# When at high speed, the car turns TURN_DECREASE_FACTOR times slower
TURN_DECREASE_FACTOR = 1


class Car:
    def __init__(self, genetic=None, best_scores=None, color="red", id_memory_car=None):
        if genetic is None:
            self.genetic = Genetic()
        else:
            self.genetic = genetic.copy()

        self.best_scores = best_scores if best_scores else [0] * NB_MAPS
        self.id_memory_car = id_memory_car
        self.color = color

        self.speed, self.acceleration = 0, 0
        self.angle = var.START_ANGLE
        # drift_angle lags behind angle to simulate drift — the speed vector turns more slowly than the car body
        self.drift_angle = var.START_ANGLE
        self.pos = var.START_POSITION
        self.front_of_car = self.pos

        self.image = change_color_car(var.RED_CAR_IMAGE, self.color)
        self.rotated_image = self.image
        self.rotated_rect = self.image.get_rect()
        self.rotated_rect_shown = self.image.get_rect()

        self.score = 0
        self.next_checkpoint = 0
        self.turn_without_checkpoint = 0
        self.dead = False
        self.reverse = False

    def __str__(self):
        return (
            f"Car: genetic : {self.genetic} ; color : {self.color} ; position : {self.pos} ;"
            f" angle : {self.angle} ; speed : {self.speed} ; acceleration : {self.acceleration}"
            f" ; score : {self.score}"
        )

    def __eq__(self, other):
        return self.genetic == other.genetic

    def copy(self):
        return Car(genetic=self.genetic)

    def move(self):
        memory_drift_factor = var.DRIFT_FACTOR
        if var.RAIN_MODE:
            var.DRIFT_FACTOR *= 1.5

        if self.reverse:
            self.update_acceleration(wall_top=False)
            self.update_speed()
            self.update_drift_angle(turn_angle=0)
            self.update_pos()
            self.detect_collision()
        else:
            self.update_score()

            wall_left, wall_top, wall_right = self.detect_walls()

            self.update_acceleration(wall_top)
            self.update_speed()

            turn_angle = self.update_angle(wall_left, wall_right)
            self.update_drift_angle(turn_angle)

            self.update_pos()
            self.detect_collision()

            self.detect_reverse()
            self.update_best_scores()

        var.DRIFT_FACTOR = memory_drift_factor

    def update_score(self):
        if var.NUM_MAP == 5:  # map 5 is a straight road where score = distance driven
            self.score += self.speed
        else:
            self.detect_checkpoint()

    def detect_checkpoint(self):
        checkpoint_found = False
        actual_checkpoint = var.CHECKPOINTS[self.next_checkpoint]
        if checkpoint_reached(self.front_of_car, actual_checkpoint):
            self.score += 1
            self.next_checkpoint += 1
            self.turn_without_checkpoint = -1
            checkpoint_found = True
            if self.next_checkpoint == len(var.CHECKPOINTS):
                self.next_checkpoint = 0

        if checkpoint_found:
            self.detect_checkpoint()
        else:
            self.turn_without_checkpoint += 1

    def detect_walls(self):
        width, length = self.determine_size_cone()
        self.front_of_car = self.compute_front_of_car()
        left, top, right = compute_detection_cone_points(self.angle, self.front_of_car, width, length)
        return self.detect_wall(left), self.detect_wall(top), self.detect_wall(right)

    def detect_wall(self, point):
        x1, y1 = self.front_of_car
        x2, y2 = point

        if x1 == x2:
            for y in range(int(min(y1, y2)), int(max(y1, y2))):
                x1 = int(x1)
                if point_out_of_window((x1, y)) or var.BACKGROUND_MASK.get_at((x1, y)):
                    return True

        a = (y2 - y1) / (x2 - x1)
        b = y1 - a * x1

        for x in range(int(min(x1, x2)), int(max(x1, x2))):
            y = int(a * x + b)
            if point_out_of_window((x, y)) or var.BACKGROUND_MASK.get_at((x, y)):
                return math.sqrt((x1 - x) ** 2 + (y1 - y) ** 2)
        return False

    def determine_size_cone(self):
        if self.speed < var.MIN_MEDIUM_SPEED:
            width = self.genetic.width_slow()
            length = self.genetic.length_slow()
        elif self.speed < var.MIN_HIGH_SPEED:
            width = self.genetic.width_medium()
            length = self.genetic.length_medium()
        else:
            width = self.genetic.width_fast()
            length = self.genetic.length_fast()
        return width, length

    def compute_front_of_car(self):
        return self.pos[0] + math.cos(math.radians(-self.angle)) * self.image.get_width() / 2, self.pos[1] + math.sin(
            math.radians(-self.angle)
        ) * self.image.get_width() / 2

    def update_acceleration(self, wall_top):
        if wall_top:
            self.acceleration -= var.DECELERATION
        else:
            self.acceleration = var.ACCELERATION

    def update_speed(self):
        self.speed += self.acceleration
        self.speed = max(min(self.speed, var.MAX_SPEED), MIN_SPEED)

    def update_angle(self, wall_left, wall_right):
        if self.speed == 0:
            turn_angle = var.TURN_ANGLE
        else:
            turn_angle = min(var.TURN_ANGLE, var.TURN_ANGLE * var.MAX_SPEED / (TURN_DECREASE_FACTOR * self.speed))

        if not wall_left and not wall_right:
            turn_angle = 0
        elif wall_left:
            if wall_right:
                if wall_left < wall_right:
                    turn_angle = -turn_angle
            else:
                turn_angle = -turn_angle

        self.angle += turn_angle
        return turn_angle

    def update_drift_angle(self, turn_angle):
        if not math.isclose(self.drift_angle, self.angle):
            if self.angle - ADD_TO_SPEED_ANGLE < self.drift_angle < self.angle + ADD_TO_SPEED_ANGLE:
                self.drift_angle = self.angle
            elif self.drift_angle > self.angle:
                self.drift_angle -= ADD_TO_SPEED_ANGLE
            else:
                self.drift_angle += ADD_TO_SPEED_ANGLE

        self.drift_angle += turn_angle / var.DRIFT_FACTOR

    def update_pos(self):
        radians = math.radians(-self.drift_angle)
        self.pos = self.pos[0] + math.cos(radians) * self.speed, self.pos[1] + math.sin(radians) * self.speed
        self.front_of_car = self.compute_front_of_car()
        self.rotated_image = pygame.transform.rotate(self.image, self.angle)
        self.rotated_rect = self.rotated_image.get_rect(center=self.image.get_rect(center=self.pos).center)

    def detect_collision(self):
        if self.pos[0] < 0 or self.pos[0] > 1500 or self.pos[1] < 0 or self.pos[1] > 700:
            self.kill()

        if (
            var.BACKGROUND_MASK.overlap(pygame.mask.from_surface(self.rotated_image), self.rotated_rect.topleft)
            is not None
        ):
            self.kill()

    def detect_reverse(self):
        if var.NUM_MAP != 5 and self.turn_without_checkpoint > 150:
            if self.id_memory_car is None and not self.color == "yellow":
                self.image = change_color_car(self.image, "light_gray")
            self.reverse = True

    def update_best_scores(self):
        if self.score > self.best_scores[var.NUM_MAP]:
            self.best_scores[var.NUM_MAP] = self.score

    def draw(self, surface=var.WINDOW):
        image_shown = scale_image(self.rotated_image, var.SCALE_RESIZE_X)
        self.rotated_rect_shown = image_shown.get_rect(center=convert_to_new_window(self.pos))
        surface.blit(image_shown, self.rotated_rect_shown)
        var.RECTS_BLIT_CAR.append(self.rotated_rect_shown)

        if var.SHOW_DETECTION_CONES:
            self.draw_detection_cone()

    def draw_detection_cone(self):
        if self.speed < var.MIN_MEDIUM_SPEED:
            actual_mode = "slow"
        elif self.speed > var.MIN_HIGH_SPEED:
            actual_mode = "fast"
        else:
            actual_mode = "medium"

        points_detection_cone = draw_detection_cone(
            pos=self.front_of_car, dice_values=self.genetic.dice_values, angle=self.angle, actual_mode=actual_mode
        )
        var.RECTS_BLIT_CAR.append(create_rect_from_points(points_detection_cone))

    def reset(self):
        self.__init__(
            genetic=self.genetic, best_scores=self.best_scores, color=self.color, id_memory_car=self.id_memory_car
        )

    def kill(self):
        self.dead = True
        var.NB_CARS_ALIVE -= 1
        self.draw(var.BACKGROUND)
        if var.SHOW_EXPLOSIONS:
            var.EXPLOSIONS.add(Explosion(self.pos))


def add_garage_cars(cars):
    for memory_car in var.SELECTED_MEMORY_CARS:
        cars.append(
            Car(
                genetic=memory_car.genetic,
                best_scores=memory_car.best_scores,
                color=memory_car.color,
                id_memory_car=memory_car.id,
            )
        )
    return cars
