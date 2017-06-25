import pygame as pg
import os
import mobs

class Spritesheet:
    def __init__(self,path):
        self.image = pg.image.load(os.path.join('res/', path)).convert_alpha()
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
        self.image = pg.image.load(os.path.join('res/', path)).convert()


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



class EntityGroup(pg.sprite.Group):
    def __init__(self):
        super().__init__()
        self.renderables = []

    def getProximityObjects(self,target,proximity):
        # Returns a list of proximity objects EXCEPT the target object
        sprites = self.renderables
        return [spr for spr in sprites if proximity.colliderect(spr.rect) and spr != target]

    def update(self,world,dt):
        # Adds objects into fov if they are collidables
        for spr in self.renderables:
            proximity = pg.Rect(spr.rect.x - 32, spr.rect.y, 128, 128)
            spr.fov = self.getProximityObjects(spr,proximity) + world.getCollidableTiles(proximity)
            spr.update(dt)


    def draw(self,surface,camera):
        '''

        :param surface: pygame.Surface
        :param camera:  camera object
        :return: None

        draws the sprite based on camera position using:
        sprite position[x,y] - camera_position[x,y]

        '''

        sprites = self.sprites()
        surface_blit = surface.blit

        # Sorts renderables by y position in ascending order
        self.renderables = sorted([spr for spr in sprites if camera.isVisible(spr.rect.center)], key = lambda spr: spr.rect.bottom)

        for spr in self.renderables:
            # Draws sprite
            self.spritedict[spr] = surface_blit(spr.image, camera.apply(spr))
            spr.draw(surface,camera)

        self.lostsprites = []
