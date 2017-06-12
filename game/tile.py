import random, settings, sprite
import pygame as pg

class TileManager():

    sprite_size = (16,16)

    def __init__(self):
        self.spritesheet = sprite.Spritesheet(settings.TILESHEET)
        self.tileset = {
            0: pg.transform.scale(self.spritesheet.getSprite(TileManager.sprite_size, (0, 2)), settings.TILE_SIZE),
            1: pg.transform.scale(self.spritesheet.getSprite(TileManager.sprite_size, (0, 0)), settings.TILE_SIZE),
            2: pg.transform.scale(self.spritesheet.getSprite(TileManager.sprite_size, (0, 1)), settings.TILE_SIZE),
            3: pg.transform.scale(self.spritesheet.getSprite(TileManager.sprite_size, (0, 2)), settings.TILE_SIZE),
            4: pg.transform.scale(self.spritesheet.getSprite(TileManager.sprite_size, (0, 3)), settings.TILE_SIZE),
            5: pg.transform.scale(self.spritesheet.getSprite(TileManager.sprite_size, (5, 0)), settings.TILE_SIZE)
        }

    def __getitem__(self, item):
        return self.tileset[item]
