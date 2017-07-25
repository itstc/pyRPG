import pygame as pg

from .player import Player

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
        self.renderables = sorted([spr for spr in sprites if camera.isVisible(spr.rect.center) or isinstance(spr, Player)], key = lambda spr: spr.rect.bottom)

        for spr in self.renderables:
            # Draws sprite
            self.spritedict[spr] = surface_blit(spr.image, camera.apply(spr))
            spr.draw(surface,camera)

        self.lostsprites = []
