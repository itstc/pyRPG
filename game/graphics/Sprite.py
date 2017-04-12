import pygame as pg
import os


class Spritesheet:
    def __init__(self,path):
        self.image = pg.image.load(os.path.join('res/', path)).convert_alpha()
        self.width = self.image.get_width()
        self.height = self.image.get_height()

    def getSprite(self,size,startX,startY):
        x = startX * size[0]
        y = startY * size[1]
        sheetArray = pg.PixelArray(self.image)
        return sheetArray[x:x + size[0],y:y + size[1]].make_surface()


class Sprite(pg.sprite.Sprite):

    def __init__(self,surface,size,position):
        pg.sprite.Sprite.__init__(self)

        self.size = size
        self.position = position
        self.image = pg.Surface(size)
        self.image = pg.transform.scale(surface,size)
        self.rect = pg.Rect(position,size)

    def update(self):
        pass