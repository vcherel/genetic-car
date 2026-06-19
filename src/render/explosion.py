import pygame

import data.variables as var
from render.resizing import convert_to_new_window


class Explosion(pygame.sprite.Sprite):
    def __init__(self, pos):
        pygame.sprite.Sprite.__init__(self)
        self.images = var.EXPLOSION_IMAGES
        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = convert_to_new_window(pos)
        self.timer = 0
        self.delay = 125

    def update(self):
        if pygame.time.get_ticks() - self.timer > self.delay and self.index < len(self.images) - 1:
            self.timer = pygame.time.get_ticks()
            self.index += 1
            self.image = self.images[self.index]
            var.RECTS_BLIT_EXPLOSION.append(self.rect)

        if self.index >= len(self.images) - 1:
            var.RECTS_BLIT_EXPLOSION.append(self.rect)
            self.kill()
