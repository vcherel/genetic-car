import pygame

import data.variables as var
from data.constants import NB_MAPS, RGB_VALUES_DICE
from data.data_classes import MemoryCar
from game.genetic import Genetic
from render.button import Button
from render.display import draw_detection_cone, draw_dice
from render.resizing import convert_to_new_window, scale_image

x1, x2, x3 = 175, 355, 535
y1, y2 = 120, 315


class DiceMenu:
    def __init__(self):
        self.dice_values = None
        self.id_memory_car = None
        self.by_camera = None
        self.camera_activated = None
        self.rect = None
        self.x = self.y = None
        self.values_button = None
        self.check_button = None

    def init(self, values, id_memory_car=None, by_camera=False):
        self.dice_values = values
        self.id_memory_car = id_memory_car
        self.by_camera = by_camera
        if self.by_camera:
            self.camera_activated = True if var.CAMERA_FRAME else False
        else:
            self.camera_activated = False

        if self.camera_activated:
            self.rect = pygame.rect.Rect(convert_to_new_window((480, 125, 1000, 550)))
            self.x = 480
            self.y = 125
        else:
            self.rect = pygame.rect.Rect(convert_to_new_window((300, 125, 1000, 550)))
            self.x = 300
            self.y = 125

        self.values_button = [
            self.dice_button(x1, y1, self.dice_values[0]),
            self.dice_button(x2, y1, self.dice_values[1]),
            self.dice_button(x3, y1, self.dice_values[2]),
            self.dice_button(x1, y2, self.dice_values[3]),
            self.dice_button(x2, y2, self.dice_values[4]),
            self.dice_button(x3, y2, self.dice_values[5]),
        ]

        self.check_button = Button(
            x=self.x + 888, y=self.y + 445, image_name="check", scale=0.4, text_displayed="Valider les dés"
        )

    def dice_button(self, x, y, value):
        return Button(
            x=self.x + x + 45,
            y=self.y + y + 140,
            image_name="writing",
            variable=value,
            name="dice",
            scale_x=0.25,
            text_displayed="Modifier la valeur du dé",
        )

    def display_dice_menu(self):
        pygame.draw.rect(var.WINDOW, (128, 128, 128), self.rect, 0)
        pygame.draw.rect(var.WINDOW, (1, 1, 1), self.rect, 2)

        var.WINDOW.blit(var.TEXT_SLOW, (convert_to_new_window((self.x + x1 + 30, self.y + 50))))
        var.WINDOW.blit(var.TEXT_MEDIUM, (convert_to_new_window((self.x + x2 + 14, self.y + 50))))
        var.WINDOW.blit(var.TEXT_FAST, (convert_to_new_window((self.x + x3 + 14, self.y + 50))))
        var.WINDOW.blit(var.TEXT_LENGTH, (convert_to_new_window((self.x + 22, self.y + 160))))
        var.WINDOW.blit(var.TEXT_WIDTH, (convert_to_new_window((self.x + 35, self.y + 350))))

        x, y = self.x + 750, self.y + 275
        var.WINDOW.blit(scale_image(var.BIG_RED_CAR_IMAGE, var.SCALE_RESIZE_X), (convert_to_new_window((x, y))))
        draw_detection_cone((x + 52, y - 3), self.dice_values, factor=3, width_line=5)

        draw_dice(x=self.x + x1, y=self.y + y1, color=RGB_VALUES_DICE[0], value=self.dice_values[0])
        draw_dice(x=self.x + x2, y=self.y + y1, color=RGB_VALUES_DICE[1], value=self.dice_values[1])
        draw_dice(x=self.x + x3, y=self.y + y1, color=RGB_VALUES_DICE[2], value=self.dice_values[2])
        draw_dice(x=self.x + x1, y=self.y + y2, color=RGB_VALUES_DICE[3], value=self.dice_values[3], black_dots=True)
        draw_dice(x=self.x + x2, y=self.y + y2, color=RGB_VALUES_DICE[4], value=self.dice_values[4])
        draw_dice(x=self.x + x3, y=self.y + y2, color=RGB_VALUES_DICE[5], value=self.dice_values[5])

        for index, writing_button in enumerate(self.values_button):
            writing_button.draw()
            if writing_button.just_clicked:
                self.values_button[index].text = ""

        if self.camera_activated:
            var.WINDOW.blit(var.CAMERA_FRAME, (var.RECT_CAMERA_FRAME.x, var.RECT_CAMERA_FRAME.y))
            pygame.draw.rect(var.WINDOW, (1, 1, 1), var.RECT_CAMERA_FRAME, 2)

        self.check_button.draw()
        return self.check_button.just_clicked

    def erase_dice_menu(self):
        var.DISPLAY_DICE_MENU = False
        var.WINDOW.blit(var.BACKGROUND, self.rect, self.rect)

        if self.camera_activated:
            var.WINDOW.blit(var.BACKGROUND, var.RECT_CAMERA_FRAME, var.RECT_CAMERA_FRAME)
            var.CAMERA_FRAME = None

        var.MEMORY_CARS.append(
            MemoryCar(
                id_car=var.ACTUAL_IDS_MEMORY_CARS,
                name=f"Dé_{var.ACTUAL_IDS_MEMORY_CARS}",
                color="gray",
                genetic=Genetic(self.dice_values),
                best_scores=[0] * NB_MAPS,
            )
        )
        var.ACTUAL_IDS_MEMORY_CARS += 1

    def save_values(self, index, writing_button):
        self.dice_values[index] = writing_button.variable

        if not self.by_camera:
            for memory_car in var.MEMORY_CARS:
                if memory_car.id == self.id_memory_car:
                    memory_car.genetic = Genetic(self.dice_values)


DICE_MENU = DiceMenu()
