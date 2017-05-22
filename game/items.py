import pygame as pg
import random,json
import sprite
from mobs import Player
from particles import BouncyText as Text
class Item:
    stackable = False
    def __init__(self,name,imageData):
        self.name = name
        self.image = sprite.Spritesheet('items.png').getSprite(imageData[0], imageData[1])
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
    def __init__(self,name,imageData):
        super().__init__(name,imageData)


class UsableItem:
    def use(self,player):
        pass

class Consumable(StackableItem,UsableItem):
    desc = ["A Consumable that", "heals you"]
    def __init__(self,name,imageData,attribute):
        super().__init__(name,imageData)
        self.attribute = attribute

    def use(self,player):
        player.stats.statQueue.append(Text(player.stats,self.attribute,[player.rect.centerx,player.rect.top],24,pg.Color(76, 243, 94),pg.Color(101, 199, 2)))
        if player.stats.hp + self.attribute > player.stats.maxHP:
            player.stats.hp = player.stats.maxHP
        else:
            player.stats.hp += self.attribute

class Weapon(Item,UsableItem):
    desc = ["A stackable item that","increases a players", "defence by 5" ]
    def __init__(self,name,imageData,attribute):
        super().__init__(name,imageData)
        self.attribute = attribute

    def use(self,player):
        player.stats.ad += self.attribute

class ItemController():
    itemClass = {'Consumable': Consumable,
                 'Weapon': Weapon}

    def __init__(self,file):
        with open(file,'r') as f:
            self.data = json.load(f)

    def getItem(self,id):
        item = self.data[str(id)]
        cls = ItemController.itemClass[item['class']]
        return cls(item['name'],item['imageData'],item['attribute'])


