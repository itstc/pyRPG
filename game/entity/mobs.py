import pygame as pg
from sprites import sprite


class Mob(sprite.MobSprite):
    sprite_size = [16,32]
    def __init__(self,image,size,position):
        super().__init__(image,size,position)

    def update(self,dt):
        # Update collision box position
        self.rect.center = [self.position[0],self.position[1]]

        if self.attacking:
            self.cooldown += dt
            if self.cooldown // 500 > 0:
                self.attacking = False
                self.cooldown = 0

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
        super().__init__(sprite.Spritesheet('mobsheet.png').getSprite(Mob.sprite_size,0,0),(64,96),(x,y))
        self.stats = Mob.Stats(25,8)

class Skeleton(Mob):
    name = 'Skeleton'
    def __init__(self,x,y):
        super().__init__(sprite.Spritesheet('mobsheet.png').getSprite(Mob.sprite_size,1,0),(64,128),(x,y))
        self.stats = Mob.Stats(25, 10)

class Player(Mob):
    # TODO: Create a player and place it on the map
    def __init__(self,x,y):
        super().__init__(sprite.Spritesheet('playersheet.png').getSprite([16,24],3,1), (64,96), (x,y))
        self.stats = Mob.Stats(100,5)

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
                print('Attacked Mob >', obj.name, obj.stats.hp, '/', obj.stats.maxHP)
