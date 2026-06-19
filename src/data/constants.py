import os.path

# order: yellow, orange, red, dark_yellow, green, black
RGB_VALUES_DICE = [(220, 220, 0), (250, 120, 0), (204, 0, 0), (240, 170, 25), (0, 175, 0), (0, 0, 0), (255, 255, 255)]

CAR_COLORS = {
    "black": (0, 0, 0),
    "blue": (0, 0, 255),
    "brown": (153, 76, 0),
    "gray": (128, 128, 128),
    "light_blue": (0, 255, 255),
    "light_green": (0, 255, 0),
    "orange": (255, 128, 0),
    "pink": (204, 0, 204),
    "purple": (102, 0, 204),
}

NB_MAPS = 8
START_POSITIONS = [(718, 168), (760, 180), (355, 184), (730, 170), (734, 241), (820, 395), (310, 680), (397, 607)]
START_ANGLES = [0, 0, 0, 0, 0, 0, 190, 210]
CAR_SIZES = [13, 10, 12, 11, 20, 15, 5, 5]

PATH_DATA = os.path.dirname(__file__) + "/../../data/"
PATH_IMAGE = os.path.dirname(__file__) + "/../../images/"
