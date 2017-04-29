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


class MobSprite(pg.sprite.Sprite):

    def __init__(self,image,size,position):
        super().__init__()

        self.size = size
        self.position = position
        self.image = image
        self.image = pg.transform.scale(image,size)
        self.rect = pg.Rect(position,size)

    def update(self,camera):
        offset = camera.getView()
        self.rect.topleft = [self.position[0] - offset[0], self.position[1] - offset[1]]

class MobGroup(pg.sprite.Group):
    def __init__(self):
        super().__init__()

    def update(self,camera):
        pg.sprite.Group.update(self,camera)
