import pygame as pg

from .settings import TILESHEET, TILE_SIZE
from sprite.sprite import Spritesheet

TILE_COLOR_MAP = {
    0: pg.Color('gray'),
    1: pg.Color('white'),
    2: pg.Color('white'),
    3: pg.Color('gray'),
    4: pg.Color('cyan'),
    5: pg.Color('brown')
}

class TileManager():

    sprite_size = (16,16)

    def __init__(self):
        self.spritesheet = Spritesheet(TILESHEET)
        self.tileset = {
            0: pg.transform.scale(self.spritesheet.getSprite(TileManager.sprite_size, (0, 2)), TILE_SIZE),
            1: pg.transform.scale(self.spritesheet.getSprite(TileManager.sprite_size, (0, 0)), TILE_SIZE),
            2: pg.transform.scale(self.spritesheet.getSprite(TileManager.sprite_size, (0, 1)), TILE_SIZE),
            3: pg.transform.scale(self.spritesheet.getSprite(TileManager.sprite_size, (0, 3)), TILE_SIZE),
            4: pg.transform.scale(self.spritesheet.getSprite(TileManager.sprite_size, (1, 0)), TILE_SIZE),
            5: pg.transform.scale(self.spritesheet.getSprite(TileManager.sprite_size, (5, 0)), TILE_SIZE)
        }

    def __getitem__(self, item):
        return self.tileset[item]
