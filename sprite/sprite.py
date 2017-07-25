import pygame as pg
import os

from game.settings import BASE_DIR

class Spritesheet:
    def __init__(self,path):
        self.image = pg.image.load(os.path.join(BASE_DIR, 'res/', path)).convert_alpha()
        self.width = self.image.get_width()
        self.height = self.image.get_height()

    def getSprite(self,size,start):
        '''

        :param size: int (Size to cut out)
        :param startX: int (Starting X)
        :param startY: int (Starting Y)
        :return: pygame.Surface (The image on spritesheet)

        '''
        x = start[0] * size[0]
        y = start[1] * size[1]
        sheetArray = pg.PixelArray(self.image)
        return sheetArray[x:x + size[0],y:y + size[1]].make_surface()

class AlphaSpritesheet(Spritesheet):
    def __init__(self,path):
        super().__init__(path)
        self.image = pg.image.load(os.path.join(BASE_DIR, 'res/', path)).convert()


class AnimatedSprite:
    def __init__(self,sheet,sequence,size,scale,rate):
        self.images = []
        self.rate = rate
        self.time = 0
        self.frame = 0
        for pos in sequence:
            self.images.append(pg.transform.scale(sheet.getSprite(size,pos),scale))

    def update(self,dt):
        self.time += dt
        if self.time / self.rate >= 1:
            self.time = 0
            # Loop through frames as frame increments
            self.frame = (self.frame + 1) % len(self.images)
        return self.images[self.frame]

    def reset(self):
        self.time = 0
        self.frame = 0

    def getFrame(self, frame):
        try:
            return self.images[frame]
        except:
            return self.images[-1]

    def currentFrame(self):
        return self.images[self.frame]
