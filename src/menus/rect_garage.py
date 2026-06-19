import random
import time

import pygame

import data.variables as var
from data.constants import CAR_COLORS
from menus.dice_menu import DICE_MENU
from render.button import Button
from render.resizing import convert_to_new_window


class RectGarage:
    def __init__(self, id_rect, memory_car, selected):
        self.id_rect = id_rect
        self.x, self.y = get_coordinates(self.id_rect)
        self.memory_car = memory_car
        self.selected = selected
        self.last_time_color_clicked = 0

        self.edit_button = Button(
            x=self.x + 188,
            y=self.y + 40,
            image_name="garage_menu/pen",
            scale=0.15,
            text_displayed="Modifier les paramètres",
        )
        self.select_button = Button(
            x=self.x + 188, y=self.y + 8, image_name="checkbox", scale=0.07, text_displayed="Sélectionner"
        )
        if self.selected:
            self.select_button.activated = True
        self.delete_button = Button(
            x=self.x + 153, y=self.y + 5, image_name="garage_menu/trash", scale=0.14, text_displayed="Supprimer"
        )
        self.name_button = Button(
            x=self.x + 10,
            y=self.y + 10,
            only_one_image=True,
            image_name="garage_menu/grey",
            writing_button=True,
            variable=self.memory_car.name,
            name="car_name",
            scale=6,
            text_displayed="Changer le nom",
        )

        self.text_displayed_rect_color = var.FONT.render("Modifier la couleur", False, (0, 0, 0), (255, 255, 255))
        self.time_mouse_over_rect_color = None

    def __str__(self):
        return (
            f"RectGarage {self.id_rect} : Checked = {self.select_button.activated}, Name = {self.name_button.variable}"
        )

    def draw(self, time_since_last_delete):
        pygame.draw.rect(var.WINDOW, (1, 1, 1), (convert_to_new_window((self.x, self.y, 225, 75))), 2)

        state_select_before = self.selected

        self.draw_rect_color()
        self.draw_name_button()
        self.draw_score()
        self.draw_select_button()
        self.draw_edit_button()
        delete_car = self.draw_delete_button(time_since_last_delete)

        updated_car_state_select = self.selected != state_select_before

        return delete_car, updated_car_state_select

    def draw_rect_color(self):
        rect_color = pygame.rect.Rect(convert_to_new_window((self.x + 154, self.y + 40, 26, 26)))
        pygame.draw.rect(var.WINDOW, CAR_COLORS[self.memory_car.color], rect_color, 0)

        if rect_color.collidepoint(pygame.mouse.get_pos()):
            if self.time_mouse_over_rect_color is None:
                self.time_mouse_over_rect_color = time.time()

            pygame.draw.rect(var.WINDOW, (1, 1, 1), rect_color, 4)

            if pygame.mouse.get_pressed()[0] and time.time() - self.last_time_color_clicked > 0.15:
                self.last_time_color_clicked = time.time()
                self.memory_car.color = random.choice(list(CAR_COLORS.keys()))

            if time.time() - self.time_mouse_over_rect_color > 0.5:
                var.TEXT_BUTTON = self.text_displayed_rect_color
        else:
            if self.time_mouse_over_rect_color is not None:
                self.time_mouse_over_rect_color = None
            pygame.draw.rect(var.WINDOW, (1, 1, 1), rect_color, 2)

    def draw_name_button(self):
        self.name_button.draw()
        if self.name_button.just_clicked:
            self.name_button.text = ""

    def draw_score(self):
        if var.NUM_MAP == 5:  # map 5 scores are distances, divide by 100 for readability
            text = var.SMALL_FONT.render(
                f"Score : {int(self.memory_car.best_scores[var.NUM_MAP] / 100)}", True, (0, 0, 0)
            )
        else:
            text = var.SMALL_FONT.render(f"Score : {self.memory_car.best_scores[var.NUM_MAP]}", True, (0, 0, 0))
        var.WINDOW.blit(text, convert_to_new_window((self.x + 20, self.y + 45)))

    def draw_select_button(self):
        self.select_button.draw()
        if self.select_button.just_clicked:
            if self.select_button.activated:
                var.SELECTED_MEMORY_CARS.append(self.memory_car)
                self.selected = True
            else:
                for selected_memory_car in var.SELECTED_MEMORY_CARS:
                    if selected_memory_car.id == self.memory_car.id:
                        var.SELECTED_MEMORY_CARS.remove(selected_memory_car)
                        break
                self.selected = False

    def draw_edit_button(self):
        if self.edit_button.draw():
            DICE_MENU.init(values=self.memory_car.genetic.dice_values, id_memory_car=self.memory_car.id)
            var.DISPLAY_DICE_MENU = True

    def draw_delete_button(self, time_since_last_delete):
        if self.delete_button.draw() and time.time() - time_since_last_delete > 0.15:
            var.MEMORY_CARS.remove(self.memory_car)

            if self.selected:
                for selected_car in var.SELECTED_MEMORY_CARS:
                    if selected_car.id == self.memory_car.id:
                        var.SELECTED_MEMORY_CARS.remove(selected_car)
                        break
                self.selected = False
            return True
        return False

    def save_new_car_name(self):
        for memory_car in var.MEMORY_CARS:
            if memory_car.id == self.memory_car.id:
                memory_car.name = self.name_button.variable
                break


def get_coordinates(id_rect):
    x = 515 if id_rect % 2 == 0 else 755
    y = 185 + 90 * (id_rect // 2)
    return x, y
