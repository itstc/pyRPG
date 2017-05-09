import pygame as pg
from sprites import sprite


class Mob(sprite.MobSprite):
    sprite_size = [16,32]
    collidable = True
    def __init__(self,image,size,position,health,ad):
        super().__init__(image,size,position)
        self.stats = Mob.Stats(health,ad)

    def update(self,dt):
        # Update collision box position
        self.rect.center = [self.position[0],self.position[1]]

        if self.attacking:
            self.cooldown += dt
            if self.cooldown // 500 > 0:
                self.attacking = False
                self.cooldown = 0

        if self.stats.hp <= 0:
            self.kill()

    def isColliding(self, x, y):
        # Takes offset x,y and sees if sprite is colliding with any objects in fov
        offset = self.getLegBox()
        offset.center = [offset.center[0] + x, offset.center[1] + y]
        collide = False
        for i in self.fov:
            if offset.colliderect(i.rect) and i.collidable:
                collide = True
        return collide

    class Stats:
        def __init__(self,health,ad):
            self.maxHP = health
            self.hp = health
            self.ad = ad

        def damage(self,target):
            target.setHP(self.ad)

        def hurt(self,value):
            self.hp -= value

class Goblin(Mob):
    name = 'Goblin'
    def __init__(self,x,y):
        super().__init__(sprite.Spritesheet('mobsheet.png').getSprite(Mob.sprite_size,0,0),(64,96),(x,y),25,8)

class Skeleton(Mob):
    name = 'Skeleton'
    def __init__(self,x,y):
        super().__init__(sprite.Spritesheet('mobsheet.png').getSprite(Mob.sprite_size,1,0),(64,128),(x,y),30,10)

class Player(Mob):
    # TODO: Create a player and place it on the map
    def __init__(self,x,y):
        sheet = sprite.Spritesheet('playersheet.png')
        super().__init__(sheet.getSprite([16,24],3,1), (64,96), (x,y),100,9)
        self.isWalking = False
        self.states = {
            0:sprite.AnimatedSprite(sheet, [(3, 0), (4, 0), (5, 0)], [16, 24], self.size,300),
            1:sprite.AnimatedSprite(sheet, [(0, 1), (1, 1), (2, 1)], [16, 24], self.size,300),
            2:sprite.AnimatedSprite(sheet, [(0, 0), (1, 0), (2, 0)], [16, 24], self.size,300),
            3:sprite.AnimatedSprite(sheet, [(3, 1), (4, 1), (5, 1)], [16, 24], self.size,300),
            4:sprite.AnimatedSprite(sheet, [(6, 0), (7, 0)], [16, 24], self.size,200),
            5:sprite.AnimatedSprite(sheet, [(6, 1), (7, 1)], [16, 24], self.size,200),
            6:sprite.AnimatedSprite(sheet, [(8, 0), (9, 0)], [16, 24], self.size,200),
            7:sprite.AnimatedSprite(sheet, [(8, 1), (9, 1)], [16, 24], self.size,200)
                       }

    def update(self,dt):
        super().update(dt)
        if self.attacking:
            self.image = self.states[self.direction + 4].update(dt)
        elif self.isWalking:
            self.image = self.states[self.direction].update(dt)
        else:
            self.image = self.states[self.direction].currentFrame()

    def getPosition(self):
        return self.position

    def getSize(self):
        return self.size

    def move(self,x,y):
        if not self.isColliding(x,y):
            self.position = (self.position[0] + x, self.position[1] + y)

    def attack(self):
        self.attacking = True
        for obj in self.fov:
            if self.getAttackRange(self.direction).colliderect(obj) and isinstance(obj,Mob):
                obj.stats.hurt(self.stats.ad)
