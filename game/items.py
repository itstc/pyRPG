import pygame as pg
import random
import sprite
from mobs import Player

class Item:
    stackable = False
    def __init__(self,name,image):
        self.name = name
        self.image = image
        self.amount = 1

    def drop(self,x,y):
        return ItemSprite(self,[x,y])

    def __eq__(self, other):
        return self.name == other.name



class ItemSprite(pg.sprite.Sprite):
    collidable = False
    def __init__(self,item,pos):
        super().__init__()
        self.image = pg.transform.scale(item.image,[32,32])
        self.size = [32,32]
        self.position = pos
        self.rect = pg.Rect(pos,[32,32])
        self.fov = []
        self.bouncing = True
        self.time = 0

        self.item = item

    def update(self,dt):
        self.time += dt
        if self.time / 500 > 1:
            self.bouncing = not self.bouncing
            self.bounce(dt,self.bouncing)
            self.time = 0

        for obj in self.fov:
            if self.rect.colliderect(obj.rect) and isinstance(obj,Player):
                obj.inventory.addItem(self.item)
                self.kill()

    def draw(self, surface, camera, offset):
        pass

    def bounce(self, dt, bounce):
        if bounce: self.position[1] -= (dt/1000) * 40
        else: self.position[1] += (dt/1000) * 40

class StackableItem(Item):
    stackable = True
    def __init__(self,name,image):
        super().__init__(name,image)


class UsableItem:
    def use(self,player):
        pass

class Consumables(StackableItem,UsableItem):
    def __init__(self,name,image):
        super().__init__(name,image)

class Potion(Consumables):
    name = 'Potion'
    def __init__(self):
        super().__init__(Potion.name,sprite.Spritesheet('items.png').getSprite([8,8],0,0))

    def use(self,player):
        if player.stats.hp + 50 > player.stats.maxHP:
            player.stats.hp = player.stats.maxHP
        else:
            player.stats.hp += 50

class Sword(Item):
    name = 'Sword'
    def __init__(self):
        super().__init__(Sword.name,sprite.Spritesheet('items.png').getSprite([8,8],2,0))
