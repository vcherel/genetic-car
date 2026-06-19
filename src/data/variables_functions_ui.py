import pygame

import data.variables as var


def add_to_rects_blit_ui(rect, offset=0):
    rect_to_add = pygame.Rect(rect.x, rect.y, rect.width + offset, rect.height + offset)
    var.RECTS_BLIT_UI.append(rect_to_add)
