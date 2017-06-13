import pygame as pg
import math
import settings, sprite, mobs

class Projectile(pg.sprite.Sprite):

    type = 'projectile'
    collidable = False

    def __init__(self, image, angle, pos, range, speed):
        super().__init__()

        self.image = pg.transform.rotate(image, 360 - math.degrees(angle))
        self.rect = self.image.get_bounding_rect()
        self.rect.center = pos
        self.end = (pos[0] + range * math.cos(angle), pos[1] + range * math.sin(angle))
        self.rate = (speed * math.cos(angle), speed * math.sin(angle))

        self.time = 1500

        self.fov = None

    def update(self, dt):

        self.time -= dt
        self.rect.move_ip(self.rate[0] * dt, self.rate[1] * dt)


        if self.time <= 0 or self.isColliding():
            self.kill()


    def draw(self,surface,camera):
        pass

    def isColliding(self):
        pass

class Arrow(Projectile):
    def __init__(self, host, angle, pos):
        super().__init__(pg.transform.scale(sprite.Spritesheet(settings.ATTACKSHEET).getSprite((16, 16), (1, 0)), (64, 32)), angle, pos, 500, 0.5)

        self.host = host
        self.damage = 6

    def isColliding(self):

        # Checks if projectile is colliding with any entities other than player
        for obj in [o for o in self.fov if o != self.host]:
            collideBox = obj.rect

            if self.rect.colliderect(collideBox) and obj.collidable:
                if obj.type == 'mob':
                    obj.stats.hurt(self.damage)
                return True

        return False
