import pygame
from graphics import Sprite
import math
from enum import Enum

class Game:

    def __init__(self, surface):
        self.surface = surface
        self.running = True
        self.SPRITESHEETS = Enum('SPRITESHEETS', {
            'TILES': Sprite.Spritesheet('tilesheet.png')
        })
        self.SPRITES = Enum('SPRITES',{
            'GRASS': self.SPRITESHEETS.TILES.value.getSprite((16, 16), 0, 0),
            'WATER': self.SPRITESHEETS.TILES.value.getSprite((16, 16), 1, 0),
            'STONE': self.SPRITESHEETS.TILES.value.getSprite((16, 16), 2, 0),
            'SAND':  self.SPRITESHEETS.TILES.value.getSprite((16, 16), 3, 0),
            'ICE': self.SPRITESHEETS.TILES.value.getSprite((16, 16), 4, 0),
            'LAVA': self.SPRITESHEETS.TILES.value.getSprite((16, 16), 5, 0)
        })
        self.spriteList = pygame.sprite.Group()

    def run(self):
        clock = pygame.time.Clock()
        for x in range(math.ceil(self.surface.get_width() / 32)):
            for y in range(math.ceil(self.surface.get_height() / 32)):
                self.spriteList.add(Sprite.Sprite(self.SPRITES.WATER.value,(32,32), (x * 32 , y * 32 )))

        while self.running:

            self.render()
            clock.tick(60)
            self.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    pygame.quit()
                    exit()

    def update(self):
        pass

    def render(self):
        self.spriteList.draw(self.surface)
        pygame.display.update()
