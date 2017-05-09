import pygame as pg
import random
from entity.mobs import Player
from sprites import sprite

class Item(pg.sprite.Sprite):
    collidable = False
    name = 'Item'
    def __init__(self,image,size,pos):
        super().__init__()
        self.image = pg.transform.scale(image,size)
        self.size = size
        self.position = pos
        self.rect = pg.Rect(pos,size)
        self.fov = []
        self.bouncing = random.choice([True,False])
        self.time = 0

    def update(self,dt):
        self.time += dt
        if self.time / 500 > 1:
            self.bouncing = not self.bouncing
            self.time = 0
            self.bounce(dt,self.bouncing)
        for obj in self.fov:
            if self.rect.colliderect(obj.rect) and isinstance(obj,Player):
                self.kill()

    def draw(self,surface,camera,offset):
        pass

    def bounce(self,dt,bounce):
        if bounce: self.position[1] -= (dt/1000) * 40
        else: self.position[1] += (dt/1000) * 40

class Potion(Item):
    name = 'Potion'
    def __init__(self,x,y):
        super().__init__(sprite.Spritesheet('items.png').getSprite([8,8],0,0),[24,24],[x,y])


class Bow(Item):
    name = 'Bow'
    def __init__(self,x,y):
        super().__init__(sprite.Spritesheet('items.png').getSprite([8,8],1,0),[32,32],[x,y])


class Club(Item):
    name = 'Club'
    def __init__(self,x,y):
        super().__init__(sprite.Spritesheet('items.png').getSprite([8,8],2,0),[32,32],[x,y])


class Axe(Item):
    name = 'Axe'
    def __init__(self,x,y):
        super().__init__(sprite.Spritesheet('items.png').getSprite([8,8],3,0),[32,32],[x,y])

class Sword(Item):
    name = 'Sword'
    def __init__(self,x,y):
        super().__init__(sprite.Spritesheet('items.png').getSprite([8,8],4,0),[32,32],[x,y])

class Spear(Item):
    name = 'Spear'
    def __init__(self,x,y):
        super().__init__(sprite.Spritesheet('items.png').getSprite([8,8],5,0),[32,32],[x,y])