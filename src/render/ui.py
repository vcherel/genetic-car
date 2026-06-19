import time

import pygame

import data.variables as var
from data.constants import PATH_IMAGE
from data.variables_functions import blit_circuit, change_map, exit_game, resize_window
from data.variables_functions_ui import add_to_rects_blit_ui
from menus.dice_menu import DICE_MENU
from menus.garage_menu import GARAGE
from menus.settings_menu import SETTINGS
from other.camera import capture_dice
from other.utils import add_offset_to_rect, union_rect
from render.button import Button
from render.display import display_text_ui, erase_car_window, show_car_window
from render.resizing import convert_to_new_window, scale_image

stop_button = Button()
pause_button = Button()
start_button = Button()
nb_cars_button = Button()
garage_button = Button()
dice_button = Button()
restart_button = Button()
settings_button = Button()
skip_button = Button()
previous_map_button = Button()
next_map_button = Button()
heatmap_button = Button()
rain_button = Button()

image_rain = pygame.image.load(PATH_IMAGE + "/rain_activated.png")
rect_rain = image_rain.get_rect(topleft=(convert_to_new_window((335, 92))))


def init():
    global \
        stop_button, \
        pause_button, \
        start_button, \
        nb_cars_button, \
        garage_button, \
        dice_button, \
        restart_button, \
        settings_button, \
        skip_button, \
        previous_map_button, \
        next_map_button, \
        heatmap_button, \
        rain_button

    stop_button = Button(x=1425, y=4, image_name="main_menu/stop", scale=0.25, text_displayed="Arrêter")
    pause_button = Button(x=1425, y=56, image_name="main_menu/pause", checkbox=True, scale=0.25, text_displayed="Pause")
    start_button = Button(x=1330, y=18, image_name="main_menu/start", scale=0.35, text_displayed="Démarrer")
    nb_cars_button = Button(
        x=1095,
        y=58,
        image_name="writing",
        variable=var.NB_CARS,
        name="nb_cars",
        text_displayed="Changer nombre de voitures",
    )
    garage_button = Button(x=350, y=30, image_name="main_menu/garage", checkbox=True, text_displayed="Ouvrir le garage")
    dice_button = Button(x=500, y=30, image_name="main_menu/dice", text_displayed="Allumer la caméra")
    restart_button = Button(
        x=1287, y=4, image_name="main_menu/restart", scale=0.2, text_displayed="Rejouer dernière run"
    )
    settings_button = Button(
        x=285, y=5, image_name="main_menu/settings", checkbox=True, scale=0.65, text_displayed="Paramètres"
    )
    skip_button = Button(x=1290, y=80, image_name="main_menu/skip", scale=0.45, text_displayed="Passer la génération")
    previous_map_button = Button(
        x=820, y=70, image_name="main_menu/previous_map", scale=0.45, text_displayed="Circuit précédent"
    )
    next_map_button = Button(x=920, y=70, image_name="main_menu/next_map", scale=0.45, text_displayed="Circuit suivant")
    heatmap_button = Button(
        x=240, y=77, image_name="main_menu/heatmap", scale=0.25, text_displayed="Afficher emplacements des crashs"
    )
    rain_button = Button(
        x=285,
        y=75,
        image_name="main_menu/rain",
        checkbox=True,
        scale=0.22,
        text_displayed="Activer la pluie (fais déraper les voitures)",
    )


def handle_events(cars=None):
    if var.RESIZE and not pygame.mouse.get_pressed()[0] and time.time() - var.TIME_RESIZE > 0.05:
        delete_all_windows()
        var.RESIZE = False
        resize_window(var.RESIZE_DIMENSIONS)
        init()
        SETTINGS.init()
        GARAGE.resize()

    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            exit_game()

        elif event.type == pygame.VIDEORESIZE:
            var.RESIZE = True
            var.RESIZE_DIMENSIONS = (event.w, event.h)
            var.TIME_RESIZE = time.time()

        elif event.type == pygame.MOUSEBUTTONDOWN:
            handle_clicks(cars)

        elif event.type == pygame.KEYDOWN:
            handle_key_press(event)


def handle_clicks(cars):
    if nb_cars_button.activated:
        nb_cars_button.deactivate()
        var.NB_CARS = nb_cars_button.variable

    if var.DISPLAY_DICE_MENU:
        for index, writing_button in enumerate(DICE_MENU.values_button):
            if writing_button.activated:
                writing_button.deactivate()
                DICE_MENU.save_values(index, writing_button)

        if not DICE_MENU.rect.collidepoint(pygame.mouse.get_pos()):
            DICE_MENU.erase_dice_menu()

    if GARAGE.rectangles:
        for rect_garage in GARAGE.rectangles:
            if rect_garage.name_button.activated and not rect_garage.name_button.rect.collidepoint(
                pygame.mouse.get_pos()
            ):
                rect_garage.name_button.deactivate()
                rect_garage.save_new_car_name()

    if (
        var.DISPLAY_GARAGE
        and not GARAGE.rect.collidepoint(pygame.mouse.get_pos())
        and not garage_button.rect.collidepoint(pygame.mouse.get_pos())
        and not var.DISPLAY_DICE_MENU
    ):
        delete_garage()

    if var.DISPLAY_SETTINGS:
        for button in SETTINGS.writing_buttons:
            if button.activated:
                button.deactivate()
                setattr(var, button.name, button.variable)

        if not SETTINGS.rect.collidepoint(pygame.mouse.get_pos()):
            settings_button.deactivate()
            SETTINGS.erase()
            unpause()

    if var.SHOW_CLICS_INFO:
        print("Click at position", pygame.mouse.get_pos())
        print("Color of the pixel", var.WINDOW.get_at(pygame.mouse.get_pos()))

    if var.DISPLAY_CAR_WINDOW:
        unpause()

    if cars and not var.DISPLAY_SETTINGS and not var.DISPLAY_GARAGE and not var.DISPLAY_DICE_MENU:
        found = False
        for car in cars:
            if not found and car.rotated_rect_shown.collidepoint(pygame.mouse.get_pos()):
                found = True
                pause()
                show_car_window(car)


def handle_key_press(event):
    if nb_cars_button.activated:
        if nb_cars_button.update_after_key_press(event):
            var.NB_CARS = nb_cars_button.variable

    if var.DISPLAY_DICE_MENU:
        for index, value_button in enumerate(DICE_MENU.values_button):
            if value_button.activated:
                if value_button.update_after_key_press(event):
                    DICE_MENU.save_values(index, value_button)

    if GARAGE.rectangles:
        for rect_garage in GARAGE.rectangles:
            if rect_garage.name_button.activated:
                if rect_garage.name_button.update_after_key_press(event):
                    rect_garage.save_new_car_name()

    if var.DISPLAY_SETTINGS:
        for button in SETTINGS.writing_buttons:
            if button.activated and button.update_after_key_press(event):
                setattr(var, button.name, button.variable)


def display(cars=None):
    display_text()
    display_buttons(cars)
    display_text_mouse()


def display_buttons(cars):
    display_stop_button()
    display_pause_button()
    display_start_button()
    display_nb_cars_button()
    display_garage_button()
    display_map_button(cars)
    display_restart_button()
    display_settings_button()
    display_skip_button()
    display_dice_button()
    display_heatmap_button()
    display_rain_button()


def display_stop_button():
    stop_button.draw()
    if stop_button.mouse_over_button:
        add_to_rects_blit_ui(stop_button.rect)
    if stop_button.just_clicked:
        if var.PLAY:
            var.PLAY = False
            blit_circuit()
        if var.DISPLAY_GARAGE:
            delete_garage()


def display_pause_button():
    var.PAUSE = pause_button.draw()
    if pause_button.mouse_over_button:
        add_to_rects_blit_ui(pause_button.rect, offset=1)
    if pause_button.just_clicked:
        if var.PAUSE:
            pause(from_button=True)
        else:
            unpause(from_button=True)


def display_start_button():
    var.START = start_button.draw()
    if start_button.mouse_over_button:
        add_to_rects_blit_ui(start_button.rect, offset=5)
    if start_button.just_clicked and (var.NB_CARS != 0 or var.SELECTED_MEMORY_CARS):
        var.PLAY = True
        if var.DISPLAY_GARAGE:
            delete_garage()
        if var.DISPLAY_DICE_MENU:
            DICE_MENU.erase_dice_menu()
    if var.START and var.PAUSE:
        unpause()


def display_nb_cars_button():
    nb_cars_button.draw()
    if nb_cars_button.just_clicked:
        nb_cars_button.text = ""


def display_garage_button():
    var.DISPLAY_GARAGE = garage_button.draw()
    if garage_button.mouse_over_button:
        add_to_rects_blit_ui(garage_button.rect, offset=3)
    if garage_button.just_clicked:
        if var.DISPLAY_GARAGE:
            pause()
        else:
            unpause()
            GARAGE.erase_garage()
    if var.DISPLAY_GARAGE and not var.DISPLAY_DICE_MENU:
        GARAGE.draw()


def display_dice_button():
    dice_button.draw()
    if dice_button.mouse_over_button:
        add_to_rects_blit_ui(dice_button.rect, offset=1)
    if dice_button.just_clicked:
        if var.DISPLAY_GARAGE:
            delete_garage()

        if var.DISPLAY_DICE_MENU:
            DICE_MENU.erase_dice_menu()
            unpause()
        else:
            pause()
            DICE_MENU.init(values=capture_dice(), by_camera=True)
            var.DISPLAY_DICE_MENU = True
            GARAGE.reload_page = True

    if var.DISPLAY_DICE_MENU:
        if DICE_MENU.display_dice_menu():
            DICE_MENU.erase_dice_menu()


def display_map_button(cars):
    previous_map_button.draw()
    if previous_map_button.mouse_over_button:
        add_to_rects_blit_ui(previous_map_button.rect, offset=6)
    if previous_map_button.just_clicked:
        change_map(reverse=True)
        pygame.display.flip()
        update_value_nb_cars_button()
        if cars:
            for car in cars:
                car.reset()
            var.NB_CARS_ALIVE = len(cars)

    next_map_button.draw()
    if next_map_button.mouse_over_button:
        add_to_rects_blit_ui(next_map_button.rect, offset=6)
    if next_map_button.just_clicked:
        change_map()
        pygame.display.flip()
        update_value_nb_cars_button()
        if cars:
            for car in cars:
                car.reset()
            var.NB_CARS_ALIVE = len(cars)


def display_restart_button():
    if restart_button.draw() and var.CARS_LAST_RUN:
        var.PLAY_LAST_RUN = True
        blit_circuit()
        if not var.LAST_RUN_PLAYING:
            var.NUM_GENERATION -= 1
        var.LAST_RUN_PLAYING = True
    if restart_button.mouse_over_button:
        add_to_rects_blit_ui(restart_button.rect)


def display_settings_button():
    var.DISPLAY_SETTINGS = settings_button.draw()
    if settings_button.just_clicked:
        if var.DISPLAY_SETTINGS:
            pause()
        else:
            unpause()
            SETTINGS.erase()
    if var.DISPLAY_SETTINGS:
        SETTINGS.draw()
    if settings_button.mouse_over_button:
        add_to_rects_blit_ui(settings_button.rect)


def display_skip_button():
    skip_button.draw()
    if skip_button.just_clicked:
        var.CHANGE_GENERATION = True
    if skip_button.mouse_over_button:
        add_to_rects_blit_ui(skip_button.rect, offset=2)


def display_heatmap_button():
    heatmap_button.draw()
    if heatmap_button.just_clicked:
        var.SHOW_HEATMAP = not var.SHOW_HEATMAP
        blit_circuit()
        var.WINDOW.blit(var.BACKGROUND, (0, 0))
    if heatmap_button.mouse_over_button:
        add_to_rects_blit_ui(heatmap_button.rect)


def display_rain_button():
    var.RAIN_MODE = rain_button.draw()
    if var.RAIN_MODE:
        var.WINDOW.blit(scale_image(image_rain), (convert_to_new_window((335, 92))))
        var.RECTS_BLIT_UI.append(rect_rain)


def display_text():
    if var.PLAY and var.ACTUAL_FPS != 0:
        time_remaining = int(var.TICKS_REMAINING / var.ACTUAL_FPS)
        var.LAST_TIME_REMAINING.append(time_remaining)
        if len(var.LAST_TIME_REMAINING) > 50:
            var.LAST_TIME_REMAINING.pop(0)
        time_remaining = max(set(var.LAST_TIME_REMAINING), key=var.LAST_TIME_REMAINING.count)
    else:
        time_remaining = int(var.TICKS_REMAINING / var.FPS)

    display_text_ui(
        f"Tours restants : {var.TICKS_REMAINING} ({time_remaining}s)", convert_to_new_window((1, 20)), var.FONT
    )
    display_text_ui(f"Nombre de voitures restantes : {var.NB_CARS_ALIVE}", convert_to_new_window((1, 50)), var.FONT)
    display_text_ui(f"Génération : {var.NUM_GENERATION}", convert_to_new_window((1, 80)), var.FONT)

    if var.PLAY:
        fps = str(var.ACTUAL_FPS)
    else:
        fps = str(int(var.CLOCK.get_fps()))
    display_text_ui("FPS : " + fps, convert_to_new_window((1, 1)), var.VERY_SMALL_FONT)


def display_text_mouse():
    mouse_pos = pygame.mouse.get_pos()
    if var.TEXT_BUTTON is not None:
        var.WINDOW.blit(var.TEXT_BUTTON, (mouse_pos[0], mouse_pos[1] + 20))
        rect = var.TEXT_BUTTON.get_rect(topleft=(mouse_pos[0], mouse_pos[1] + 20))
        pygame.draw.rect(var.WINDOW, (0, 0, 0), add_offset_to_rect(rect, 2), 1)
        var.RECTS_BLIT_UI.append(rect)
    var.TEXT_BUTTON = None


def pause(from_button=False):
    if not from_button:
        var.PAUSE = True
        pause_button.activated = True


def unpause(from_button=False):
    if not from_button:
        var.PAUSE = False
        pause_button.activated = False
        add_to_rects_blit_ui(pause_button.rect)

    if var.DISPLAY_CAR_WINDOW:
        erase_car_window()


def delete_all_windows():
    if var.DISPLAY_CAR_WINDOW:
        erase_car_window()
    if var.DISPLAY_GARAGE:
        delete_garage()
    if var.DISPLAY_DICE_MENU:
        DICE_MENU.erase_dice_menu()
    if var.DISPLAY_SETTINGS:
        delete_settings()


def delete_garage():
    var.DISPLAY_GARAGE = False
    garage_button.deactivate()
    GARAGE.erase_garage()
    unpause()


def delete_settings():
    var.DISPLAY_SETTINGS = False
    settings_button.deactivate()
    SETTINGS.erase()
    unpause()


def erase():
    rect_blit_ui = union_rect(var.RECTS_BLIT_UI)
    var.WINDOW.blit(var.BACKGROUND, rect_blit_ui, rect_blit_ui)
    var.RECTS_BLIT_UI = []


def update_value_nb_cars_button():
    nb_cars_button.update_text(var.NB_CARS)
