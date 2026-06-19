import time

import pygame

import data.variables as var
from data.constants import PATH_IMAGE
from other.camera import change_camera
from render.resizing import convert_to_new_window


class Button:
    def __init__(
        self,
        x=None,
        y=None,
        image_name=None,
        only_one_image=False,
        checkbox=False,
        writing_button=False,
        variable=None,
        name=None,
        text_displayed=None,
        scale=1,
        scale_x=None,
        scale_y=None,
    ):
        if x is not None:
            if scale_x is None:
                scale_x = scale
            if scale_y is None:
                scale_y = scale
            scale_x, scale_y = scale_x * var.SCALE_RESIZE_X, scale_y * var.SCALE_RESIZE_Y

            self.x, self.y = convert_to_new_window((x, y))
            new_image_name = f"{PATH_IMAGE}buttons/{image_name}"

            if only_one_image:
                image = pygame.image.load(f"{new_image_name}.png")
                self.image_hover = None
                self.image_clicked = None
            else:
                image = pygame.image.load(f"{new_image_name}_1.png")
                image_hover = pygame.image.load(f"{new_image_name}_2.png")
                self.image_hover = pygame.transform.scale(
                    image_hover, (int(image_hover.get_width() * scale_x), int(image_hover.get_height() * scale_y))
                )
                image_clicked = pygame.image.load(f"{new_image_name}_3.png")
                self.image_clicked = pygame.transform.scale(
                    image_clicked, (int(image_clicked.get_width() * scale_x), int(image_clicked.get_height() * scale_y))
                )

            self.image = pygame.transform.scale(
                image, (int(image.get_width() * scale_x), int(image.get_height() * scale_y))
            )
            self.rect = self.image.get_rect()
            self.rect.topleft = (self.x, self.y)

            self.activated = False
            self.just_clicked = 0
            self.time_clicked = 0
            self.mouse_over_button = False

            self.checkbox = checkbox
            if image_name == "checkbox":
                self.checkbox = True

            self.writing_button = writing_button
            if image_name == "writing":
                self.writing_button = True

            self.text = str(variable)
            self.variable = variable
            self.name = name
            self.time_mouse_over_button = None
            if text_displayed is None:
                self.text_displayed = None
            else:
                self.text_displayed = var.FONT.render(text_displayed, False, (0, 0, 0), (255, 255, 255))

    def __str__(self):
        return (
            f"Button : x = {self.x} ; y = {self.y} ; activated = {self.activated} ; just_clicked = {self.just_clicked}"
            f" ; time_clicked = {self.time_clicked} ; check_box = {self.checkbox}"
            f" ; writing_button = {self.writing_button}"
            f" ; text = {self.text} ; variable = {self.variable} ; name = {self.name}"
        )

    def draw(self):
        image = self.image
        mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos):
            self.mouse_over_button = True

            if self.time_mouse_over_button is None:
                self.time_mouse_over_button = time.time()

            if pygame.mouse.get_pressed()[0] == 1 and time.time() - self.time_clicked > 0.15:
                self.time_clicked = time.time()
                if self.checkbox or self.writing_button:
                    self.activated = not self.activated
                else:
                    self.activated = True
                self.just_clicked = 1
            else:
                self.just_clicked = 0
                if not self.checkbox and not self.writing_button:
                    self.activated = False

            if self.image_hover:
                image = self.image_hover
        else:
            if self.time_mouse_over_button is not None:
                self.time_mouse_over_button = None
            self.mouse_over_button = False
            self.just_clicked = 0
            if not self.checkbox and not self.writing_button:
                self.activated = False

        if self.activated and self.image_clicked:
            image = self.image_clicked

        var.WINDOW.blit(image, (self.rect.x, self.rect.y))

        if self.writing_button:
            var.WINDOW.blit(var.FONT.render(self.text, True, (0, 0, 0)), (self.rect.x + 10, self.rect.y + 4))

        if (
            self.mouse_over_button
            and self.text_displayed is not None
            and time.time() - self.time_mouse_over_button > 0.5
        ):
            var.TEXT_BUTTON = self.text_displayed

        return self.activated

    def update_after_key_press(self, event):
        if event.key == pygame.K_RETURN:
            self.deactivate()
            return True
        elif event.key == pygame.K_BACKSPACE:
            self.text = self.text[:-1]
        elif event.unicode == " ":
            self.text += "_"
        else:
            self.text += event.unicode
        return False

    def update_text(self, parameter):
        self.variable = parameter
        self.text = str(parameter)

    def deactivate(self):
        self.activated = False
        self.just_clicked = -1
        self.time_clicked = time.time()
        if self.writing_button:
            self.save_text()

    def save_text(self):
        if self.variable is not None:
            try:
                if self.name == "dice":
                    self.variable = int(self.text)
                    self.variable = max(1, self.variable)
                    self.variable = min(6, self.variable)
                elif self.name == "car_name":
                    self.variable = self.text
                    if self.variable == "":
                        self.variable = "_"
                elif "." in self.text:
                    self.variable = float(self.text)
                    if self.variable <= 0:
                        self.variable = 0.1
                else:
                    self.variable = int(self.text)
                    if self.variable < 0:
                        self.variable = 30
            except ValueError:
                if self.name == "dice":
                    self.variable = 1
                else:
                    self.variable = 30

            self.text = str(self.variable)

            if self.name == "CAMERA":
                var.NUM_CAMERA = self.variable
                change_camera()
