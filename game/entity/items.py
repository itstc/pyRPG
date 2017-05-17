import pygame as pg
import random
from entity.mobs import Player
from sprites import sprite

class Item(pg.sprite.Sprite):
    collidable = False
    def __init__(self,name,image,size,pos):
        super().__init__()
        self.image = pg.transform.scale(image,size)
        self.size = size
        self.position = pos
        self.rect = pg.Rect(pos,size)
        self.fov = []
        self.bouncing = True
        self.time = 0

    def update(self,dt):
        self.time += dt
        if self.time / 500 > 1:
            self.bouncing = not self.bouncing
            self.bounce(dt,self.bouncing)
            self.time = 0

        for obj in self.fov:
            if self.rect.colliderect(obj.rect) and isinstance(obj,Player):
                obj.inventory.addItem(self)
                self.kill()

    def draw(self,surface,camera,offset):
        pass

    def bounce(self,dt,bounce):
        if bounce: self.position[1] -= (dt/1000) * 40
        else: self.position[1] += (dt/1000) * 40

class UsableItem:
    def use(self,player):
        pass

class Consumables(Item,UsableItem):
    def __init__(self,name,image,pos):
        super().__init__(name, image, [24,24], pos)

class Potion(Consumables):
    name = 'Potion'
    def __init__(self,x,y):
        super().__init__(Potion.name,sprite.Spritesheet('items.png').getSprite([8,8],0,0),[x,y])

    def use(self,player):
        if player.stats.hp + 50 > player.stats.maxHP:
            player.stats.hp = player.stats.maxHP
        else:
            player.stats.hp += 50
