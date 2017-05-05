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

    def __init__(self,image,size,pos):
        super().__init__()

        self.size = size
        self.position = pos
        self.image = image
        self.image = pg.transform.scale(image,size)
        self.mask = pg.mask.from_surface(self.image)
        self.rect = pg.Rect(pos,[size[0]//2,size[1]])
        self.fov = []

    def update(self):
        # Update collision box position
        self.rect.center = [self.position[0],self.position[1]]

    def getLegBox(self):
        legBox = pg.Rect(self.position[0]-self.size[0]//4, self.position[1],self.size[0]//2, self.size[1]//2)
        return legBox

    def isColliding(self, x, y):
        # Takes offset x,y and sees if sprite is colliding with any objects in fov
        offset = self.getLegBox()
        offset.center = [offset.center[0] + x, offset.center[1] + y]
        collide = False
        for i in self.fov:
            if offset.colliderect(i):
                collide = True
        return collide

    def move(self,x,y):
        # Moves sprite if not colliding
        if not self.isColliding(x,y):
            self.position = [self.position[0] + x, self.position[1] + y]


class MobGroup(pg.sprite.Group):
    def __init__(self):
        super().__init__()

    def getProximityObjects(self,target,proximity):
        # Returns a list of proximity objects EXCEPT the target object
        sprites = self.sprites()
        return [spr.rect for spr in sprites if proximity.colliderect(spr.rect) and spr != target]

    def update(self,world):
        # Adds objects into fov if they are collidables
        for spr in self.sprites():
            proximity = pg.Rect(spr.position[0] - 64, spr.position[1] - 64, 128, 128)
            spr.fov = world.getCollidableTiles(proximity) + self.getProximityObjects(spr,proximity)
            spr.update()

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

            # Draws collision box
            camera.drawRectangle(surface,pg.Color('cyan'),spr.rect)
            camera.drawRectangle(surface,pg.Color('purple'), spr.getLegBox())
        self.lostsprites = []
