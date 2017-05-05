import pygame as pg
from sprites import sprite


class Mob(sprite.MobSprite):
    sprite_size = [16,32]
    def __init__(self,image,size,position):
        super().__init__(image,size,position)

class Goblin(Mob):
    name = 'Goblin'
    def __init__(self,x,y):
        super().__init__(sprite.Spritesheet('mobsheet.png').getSprite(Mob.sprite_size,0,0),(64,96),(x,y))

class Skeleton(Mob):
    name = 'Skeleton'
    def __init__(self,x,y):
        super().__init__(sprite.Spritesheet('mobsheet.png').getSprite(Mob.sprite_size,1,0),(64,128),(x,y))

class Player(Mob):
    # TODO: Create a player and place it on the map
    def __init__(self,x,y):
        super().__init__(sprite.Spritesheet('playersheet.png').getSprite([16,24],3,1), (64,96), (x,y))

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
                print('Attacked Mob:', obj.name)
