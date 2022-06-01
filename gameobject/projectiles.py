import pygame as pg
import math

from game.settings import ATTACKSHEET
from sprite.sprite import Spritesheet

class Projectile(pg.sprite.Sprite):

    type = 'projectile'
    collidable = False

    def __init__(self, image, angle, pos, range, speed):
        super().__init__()

        self.image = pg.transform.rotate(image, 360 - math.degrees(angle))
        self.rect = self.image.get_rect(center=pos)
        hypo = math.sqrt(self.rect.width + self.rect.height)
        self.rate = (speed * math.cos(angle), speed * math.sin(angle))

        quad = math.pi / 2
        collidePos = self.rect.topleft

        # 270 - 360 deg
        if angle >= 0 and angle <= quad:
            collidePos = (self.rect.right - 16, self.rect.bottom - 16)
        # 180 - 270 deg
        elif angle >= quad and angle <= quad * 2:
            collidePos = (self.rect.left, self.rect.bottom - 16)
        # 0 - 90 deg
        elif angle < 0 and angle >= -quad:
            collidePos = (self.rect.right - 16, self.rect.top)
           
        self.collidingRect = pg.Rect(collidePos, (16, 16))

        self.time = 60

        self.fov = None

    def update(self, dt):

        self.time -= dt
        self.rect.move_ip(self.rate[0] * dt, self.rate[1] * dt)
        self.collidingRect.move_ip(self.rate[0] * dt, self.rate[1] * dt)


        if self.time <= 0 or self.isColliding():
            self.kill()


    def draw(self,surface,camera):
        pass

    def isColliding(self):
        pass

class Arrow(Projectile):
    def __init__(self, host, angle, pos):
        super().__init__(pg.transform.scale(Spritesheet(ATTACKSHEET).getSprite((16, 16), (0, 0)), (64, 32)), angle, pos, 500, 6)

        self.host = host
        self.damage = host.stats.ad

    def isColliding(self):

        # Checks if projectile is colliding with any entities other than player
        for obj in [o for o in self.fov if o != self.host]:
            collideBox = obj.rect

            if self.collidingRect.colliderect(collideBox) and obj.collidable:
                if obj.type == 'gameobject':
                    self.host.stats.damage(obj)
                return True

        return False
