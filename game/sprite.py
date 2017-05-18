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

class AnimatedSprite:
    def __init__(self,sheet,sequence,size,scale,rate):
        self.images = []
        self.rate = rate
        self.time = 0
        self.frame = 0
        for pos in sequence:
            self.images.append(pg.transform.scale(sheet.getSprite(size,pos[0],pos[1]),scale))

    def update(self,dt):
        self.time += dt
        if self.time / self.rate >= 1:
            self.time = 0
            self.frame = (self.frame + 1) % len(self.images)
        return self.images[self.frame]

    def reset(self):
        self.time = 0
        self.frame = 0

    def currentFrame(self):
        return self.images[self.frame]


class EntityGroup(pg.sprite.Group):
    def __init__(self):
        super().__init__()

    def getProximityObjects(self,target,proximity):
        # Returns a list of proximity objects EXCEPT the target object
        sprites = self.sprites()
        return [spr for spr in sprites if proximity.colliderect(spr.rect) and spr != target]

    def update(self,world,dt):
        # Adds objects into fov if they are collidables
        for spr in self.sprites():
            proximity = pg.Rect(spr.position[0] - 64, spr.position[1] - 64, 128, 128)
            spr.fov = world.getCollidableTiles(proximity) + self.getProximityObjects(spr,proximity)
            spr.update(dt)

    def draw(self,surface,camera):
        '''

        :param surface: pygame.Surface
        :param camera:  camera object
        :return: None

        draws the sprite based on camera position using:
        sprite position[x,y] - camera_position[x,y]

        '''
        offset = camera.getView()
        sprites = self.sprites()
        surface_blit = surface.blit
        for spr in sprites:
            # Offset the player position to be based on camera
            drawRect = (spr.position[0] - spr.size[0]//2 - offset[0], spr.position[1] - spr.size[1]//2 - offset[1])

            # Draws sprite
            self.spritedict[spr] = surface_blit(spr.image, drawRect)
            spr.draw(surface,camera,drawRect)

        self.lostsprites = []
