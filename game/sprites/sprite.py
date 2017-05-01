import pygame as pg
import os

class Spritesheet:
    def __init__(self,path):
        self.image = pg.image.load(os.path.join('res/', path)).convert_alpha()
        self.width = self.image.get_width()
        self.height = self.image.get_height()

    def getSprite(self,size,startX,startY):
        '''

        :param size: int (Size to cut out)
        :param startX: int (Starting X)
        :param startY: int (Starting Y)
        :return: pygame.Surface (The image on spritesheet)

        '''
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

class MobGroup(pg.sprite.Group):
    def __init__(self):
        super().__init__()

    def draw(self,surface,offset):
        '''

        :param surface: pygame.Surface
        :param offset:  tuple
        :return: None

        draws the sprite based on camera position using:
        sprite position[x,y] - camera_position[x,y]

        '''

        sprites = self.sprites()
        surface_blit = surface.blit
        for spr in sprites:
            spr.rect.center = [spr.position[0] - offset[0], spr.position[1] - offset[1]]
            self.spritedict[spr] = surface_blit(spr.image, spr.rect)
        self.lostsprites = []
