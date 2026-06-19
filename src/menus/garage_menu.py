import time

import pygame

import data.variables as var
from data.constants import PATH_IMAGE
from menus.rect_garage import RectGarage
from render.button import Button
from render.resizing import convert_to_new_window, scale_image

debug = 0


class Garage:
    def __init__(self):
        self.x, self.y = convert_to_new_window((500, 125))
        self.image = scale_image(pygame.image.load(PATH_IMAGE + "/garage_menu.png"))
        self.rect = pygame.rect.Rect(self.x, self.y, self.image.get_width(), self.image.get_height())

        self.nb_rectangles = 0
        self.rectangles = []
        self.selected_rects = [False] * len(var.MEMORY_CARS)

        self.actual_page = 0
        self.reload_page = True

        self.trash_button = Button(
            x=930, y=135, image_name="garage_menu/trash", scale=0.2, text_displayed="Supprimer toutes les voitures"
        )
        self.time_since_last_delete = 0
        self.next_button = Button(
            x=940, y=623, image_name="garage_menu/next_page", scale=0.2, text_displayed="Page suivante"
        )
        self.previous_button = Button(
            x=520, y=623, image_name="garage_menu/previous_page", scale=0.2, text_displayed="Page précédente"
        )

    def __str__(self):
        string = f"Garage : {self.nb_rectangles} rectangles :"
        for rect in self.rectangles:
            string += f"\n{rect}"
        return string

    def reset(self):
        self.rectangles = []
        self.nb_rectangles = 0

    def draw(self):
        var.WINDOW.blit(self.image, (self.x, self.y))
        self.draw_rects_garage()
        self.draw_trash_button()

        if self.reload_page:
            self.reload()

        self.draw_arrows()

    def draw_rects_garage(self):
        for rect_garage in self.rectangles:
            deleted, selected = rect_garage.draw(self.time_since_last_delete)

            if deleted:
                self.reload_page = True
                self.time_since_last_delete = time.time()
                self.update_selected_rects(rect_garage.id_rect)

            elif selected:
                self.selected_rects[self.get_index_rect(rect_garage.id_rect)] = not self.selected_rects[
                    self.get_index_rect(rect_garage.id_rect)
                ]

    def update_selected_rects(self, id_rect_to_delete):
        index_rect_to_delete = self.get_index_rect(id_rect_to_delete)
        for i in range(index_rect_to_delete, len(var.MEMORY_CARS) - 1):
            self.selected_rects[i] = self.selected_rects[i + 1]
        self.selected_rects.pop(len(var.MEMORY_CARS) - 1)

    def draw_trash_button(self):
        self.trash_button.draw()
        if self.trash_button.activated:
            var.MEMORY_CARS = []
            var.SELECTED_MEMORY_CARS = []
            var.ACTUAL_IDS_MEMORY_CARS = 1
            self.selected_rects = []
            self.reload_page = True

    def reload(self):
        if len(var.MEMORY_CARS) > len(self.selected_rects):
            for _ in range(len(var.MEMORY_CARS) - len(self.selected_rects)):
                self.selected_rects.append(False)

        self.reset()
        id_rect = 0
        for memory_car in var.MEMORY_CARS:
            if 10 * self.actual_page <= self.nb_rectangles < 10 * (self.actual_page + 1):
                self.rectangles.append(
                    RectGarage(
                        id_rect=id_rect,
                        memory_car=memory_car,
                        selected=self.selected_rects[self.get_index_rect(id_rect)],
                    )
                )
                id_rect += 1
            self.nb_rectangles += 1

        self.reload_page = False

    def draw_arrows(self):
        if (self.actual_page + 1) * 10 < self.nb_rectangles:
            self.next_button.draw()
            if self.next_button.just_clicked:
                self.actual_page += 1
                self.reload_page = True

        if self.actual_page > 0:
            self.previous_button.draw()
            if self.previous_button.just_clicked:
                self.actual_page -= 1
                self.reload_page = True

    def get_index_rect(self, id_rect):
        return 10 * self.actual_page + id_rect

    def resize(self):
        self.x, self.y = convert_to_new_window((500, 125))
        self.image = scale_image(pygame.image.load(PATH_IMAGE + "/garage_menu.png"))
        self.rect = pygame.rect.Rect(self.x, self.y, self.image.get_width(), self.image.get_height())
        self.trash_button = Button(x=930, y=135, image_name="garage_menu/trash", scale=0.2)
        self.next_button = Button(x=940, y=623, image_name="garage_menu/next_page", scale=0.2)
        self.previous_button = Button(x=520, y=623, image_name="garage_menu/previous_page", scale=0.2)
        self.reload()

    def erase_garage(self):
        var.WINDOW.blit(var.BACKGROUND, self.rect, self.rect)


GARAGE = Garage()
