import pygame

import data.variables as var
from data.constants import PATH_IMAGE
from render.button import Button
from render.resizing import convert_to_new_window, scale_image


class Settings:
    def __init__(self):
        self.image = None
        self.rect = None
        self.x = self.y = None

        self.show_clics_button = None

        self.fps_button = None
        self.seed_button = None
        self.camera_button = None

        self.show_cones_button = None
        self.show_explosions_button = None
        self.show_checkpoints_button = None

        self.max_speed_button = None
        self.turn_angle_button = None
        self.acceleration_button = None
        self.deceleration_button = None
        self.drift_button = None

        self.crossover_button = None
        self.mutation_button = None
        self.proportion_button = None
        self.time_generation_button = None

        self.width_cone_button = None
        self.length_cone_button = None

        self.writing_buttons = []

    def init(self):
        self.x, self.y = convert_to_new_window((175, 125))
        self.image = scale_image(pygame.image.load(PATH_IMAGE + "/settings_menu.png"))
        self.rect = pygame.rect.Rect(self.x, self.y, self.image.get_width(), self.image.get_height())

        self.show_clics_button = Button(x=1340, y=650, image_name="checkbox", scale=0.02)

        self.fps_button = Button(
            x=292,
            y=221,
            image_name="writing",
            variable=var.FPS,
            name="FPS",
            scale_x=0.5,
            text_displayed="Nombre d'images par seconde",
        )
        self.seed_button = Button(
            x=300,
            y=267,
            image_name="writing",
            variable=var.SEED,
            name="SEED",
            scale_x=0.5,
            text_displayed="Permet de rejouer la même simulation plusieurs fois",
        )
        self.camera_button = Button(
            x=330,
            y=311,
            image_name="writing",
            variable=var.NUM_CAMERA,
            name="CAMERA",
            scale_x=0.5,
            text_displayed="Changer de caméra",
        )

        self.show_cones_button = Button(
            x=474, y=455, image_name="checkbox", scale=0.1, text_displayed="Afficher les triangles devant les voitures"
        )
        self.show_explosions_button = Button(
            x=401, y=524, image_name="checkbox", scale=0.1, text_displayed="Ça sert à rien mais c'est rigolo"
        )
        self.show_explosions_button.activated = var.SHOW_EXPLOSIONS
        self.show_checkpoints_button = Button(
            x=412, y=597, image_name="checkbox", scale=0.1, text_displayed="Afficher les checkpoints"
        )

        self.max_speed_button = Button(
            x=847,
            y=222,
            image_name="writing",
            variable=var.MAX_SPEED,
            name="MAX_SPEED",
            scale_x=0.5,
            text_displayed="Changer vitesse maximale des voitures",
        )
        self.turn_angle_button = Button(
            x=864,
            y=279,
            image_name="writing",
            variable=var.TURN_ANGLE,
            name="TURN_ANGLE",
            scale_x=0.5,
            text_displayed="Changer angle de rotation des voitures",
        )
        self.acceleration_button = Button(
            x=791,
            y=342,
            image_name="writing",
            name="ACCELERATION",
            variable=var.ACCELERATION,
            scale_x=0.5,
            text_displayed="Plus ce paramètre est grand, plus les voitures accélèrent vite",
        )
        self.deceleration_button = Button(
            x=742,
            y=402,
            image_name="writing",
            name="DECELERATION",
            variable=var.DECELERATION,
            scale_x=0.5,
            text_displayed="Plus ce paramètre est grand, plus les voitures freinent vite",
        )
        self.drift_button = Button(
            x=777,
            y=460,
            image_name="writing",
            name="DRIFT_FACTOR",
            variable=var.DRIFT_FACTOR,
            scale_x=0.5,
            text_displayed="Plus ce paramètre est grand, plus les voitures dérapent",
        )

        self.proportion_button = Button(
            x=1280,
            y=222,
            image_name="writing",
            variable=var.PROPORTION_CARS_KEPT,
            name="PROPORTION_CARS_KEPT",
            scale_x=0.5,
            text_displayed="Voitures gardées entre deux runs",
        )
        self.crossover_button = Button(
            x=1240,
            y=295,
            image_name="writing",
            variable=var.CHANCE_CROSSOVER,
            name="CHANCE_CROSSOVER",
            scale_x=0.5,
            text_displayed="Probabilité de crossover",
        )
        self.mutation_button = Button(
            x=1222,
            y=369,
            image_name="writing",
            variable=var.CHANCE_MUTATION,
            name="CHANCE_MUTATION",
            scale_x=0.5,
            text_displayed="Probabilité de mutation",
        )
        self.time_generation_button = Button(
            x=1280,
            y=446,
            image_name="writing",
            variable=var.TIME_GENERATION,
            name="TIME_GENERATION",
            scale_x=0.5,
            text_displayed="Durée d'une génération",
        )

        self.width_cone_button = Button(
            x=718,
            y=610,
            image_name="writing",
            variable=var.WIDTH_CONE,
            name="WIDTH_CONE",
            scale_x=0.5,
            text_displayed="Largeur des triangles devant les voitures",
        )
        self.length_cone_button = Button(
            x=1110,
            y=610,
            image_name="writing",
            variable=var.LENGTH_CONE,
            name="LENGTH_CONE",
            scale_x=0.5,
            text_displayed="Longueur des triangles devant les voitures",
        )

        self.writing_buttons = [
            self.fps_button,
            self.seed_button,
            self.camera_button,
            self.max_speed_button,
            self.turn_angle_button,
            self.acceleration_button,
            self.deceleration_button,
            self.drift_button,
            self.proportion_button,
            self.mutation_button,
            self.crossover_button,
            self.time_generation_button,
            self.width_cone_button,
            self.length_cone_button,
        ]

    def update_parameters(self):
        self.seed_button.update_text(var.SEED)
        self.max_speed_button.update_text(var.MAX_SPEED)
        self.turn_angle_button.update_text(var.TURN_ANGLE)
        self.acceleration_button.update_text(var.ACCELERATION)
        self.deceleration_button.update_text(var.DECELERATION)
        self.drift_button.update_text(var.DRIFT_FACTOR)
        self.crossover_button.update_text(var.CHANCE_CROSSOVER)
        self.mutation_button.update_text(var.CHANCE_MUTATION)
        self.proportion_button.update_text(var.PROPORTION_CARS_KEPT)
        self.time_generation_button.update_text(var.TIME_GENERATION)
        self.width_cone_button.update_text(var.WIDTH_CONE)
        self.length_cone_button.update_text(var.LENGTH_CONE)

    def draw(self):
        var.WINDOW.blit(self.image, (self.x, self.y))

        # To make writing buttons work, handle_key_press in ui.py must iterate over self.writing_buttons
        for button in self.writing_buttons:
            button.draw()
            if button.just_clicked:
                button.text = ""

        var.SHOW_DETECTION_CONES = self.show_cones_button.draw()
        var.SHOW_CLICS_INFO = self.show_clics_button.draw()
        var.SHOW_EXPLOSIONS = self.show_explosions_button.draw()
        var.SHOW_CHECKPOINTS = self.show_checkpoints_button.draw()
        if self.show_checkpoints_button.just_clicked and not var.SHOW_CHECKPOINTS:
            var.WINDOW.blit(var.BACKGROUND, (0, 0))

    def erase(self):
        var.WINDOW.blit(var.BACKGROUND, self.rect, self.rect)


SETTINGS = Settings()
