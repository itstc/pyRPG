import pygame as pg

from sprite.sprite import Spritesheet, AnimatedSprite
from game.settings import ITEMSHEET, ARMORSPRITE, ITEMSPRITE
from gameobject.player import Player
from gameobject.particles import BouncyText
from .effect import ITEM_EFFECT_MAP

class Item:
    type = 'item'
    stackable = False
    def __init__(self, name, desc, rarity, imageData):
        self.name = name
        self.desc = desc
        self.rarity = rarity
        self.image = Spritesheet(ITEMSHEET).getSprite(imageData[0], imageData[1])
        self.image_size = imageData[0]
        self.amount = 1

    def drop(self,pos):
        return ItemSprite(self,pos)

    def __eq__(self, other):
        return self.name == other.name

class ItemSprite(pg.sprite.Sprite):

    type = 'item'
    collidable = False


    def __init__(self,item,pos):
        super().__init__()
        self.size = [item.image_size[0] * (32//item.image_size[0]), item.image_size[1] * (32//item.image_size[1])]
        self.image = pg.transform.scale(item.image,self.size)
        self.position = list(pos)
        self.rect = pg.Rect(pos,self.size)
        self.fov = []

        self.item = item

    def update(self,dt):
        self.rect.topleft = self.position

        for obj in self.fov:
            if self.rect.colliderect(obj.rect) and isinstance(obj,Player) and not obj.inventory.isFull():
                obj.inventory.addItem(self.item)
                self.kill()

    def draw(self, surface, camera):
        pass

class StackableItem(Item):
    stackable = True
    def __init__(self,name,desc,rarity,imageData):
        super().__init__(name,desc,rarity,imageData)

class UsableItem:
    def use(self,player):
        pass

class Consumable(StackableItem,UsableItem):
    def __init__(self,name,desc,rarity,imageData,attributes):
        super().__init__(name,desc,rarity,imageData)

        self.attributes = attributes

    def use(self,player):
        for k,v in self.attributes.items():
            ITEM_EFFECT_MAP[k](player, v)

class Equipment(Item, UsableItem):

    type = 'equipment'

    def __init__(self, name, desc, rarity, imageData, spriteID, attributes):
        super().__init__(name, desc, rarity, imageData)
        self.attributes = attributes

    def use(self,player):
        for k,v in self.attributes.items():
            ITEM_EFFECT_MAP[k](player, v)

    def unequip(self, player):
        for k,v in self.attributes.items():
            ITEM_EFFECT_MAP[k](player, -v)

class Head(Equipment):
    equipment_type = 'head'

    def __init__(self, name, desc, rarity, imageData, spriteID, attributes):
        super().__init__(name,desc,rarity,imageData, spriteID, attributes)
        sheet = Spritesheet(ARMORSPRITE)
        self.sprite = {
            'idle_left': AnimatedSprite(sheet, [(0, spriteID)], (16, 16), (64, 64), 12),
            'idle_right': AnimatedSprite(sheet, [(1, spriteID)], (16, 16), (64, 64), 12),
            'walk_left': AnimatedSprite(sheet, [(0, spriteID)], (16, 16), (64, 64), 12),
            'walk_right': AnimatedSprite(sheet, [(1, spriteID)], (16, 16), (64, 64), 12),
            'attack_left': AnimatedSprite(sheet, [(0, spriteID)], (16, 16), (64, 64), 9),
            'attack_right': AnimatedSprite(sheet, [(1, spriteID)], (16, 16), (64, 64), 9)
        }

class Body(Equipment):
    equipment_type = 'body'

    def __init__(self, name, desc, rarity, imageData, spriteID, attributes):
        super().__init__(name,desc,rarity,imageData, spriteID, attributes)
        sheet = Spritesheet(ARMORSPRITE)
        self.sprite = {
            'idle_left': AnimatedSprite(sheet, [(2, spriteID)], (16, 16), (64, 64), 12),
            'idle_right': AnimatedSprite(sheet, [(3, spriteID)], (16, 16), (64, 64), 12),
            'walk_left': AnimatedSprite(sheet, [(2, spriteID)], (16, 16), (64, 64), 12),
            'walk_right': AnimatedSprite(sheet, [(3, spriteID)], (16, 16), (64, 64), 12),
            'attack_left': AnimatedSprite(sheet, [(2, spriteID), (4, spriteID), (5, spriteID)], (16, 16), (64, 64), 9),
            'attack_right': AnimatedSprite(sheet, [(3, spriteID), (6, spriteID), (7, spriteID)], (16, 16), (64, 64), 9)
        }

class Leg(Equipment):
    equipment_type = 'leg'

    def __init__(self, name, desc, rarity, imageData, spriteID, attributes):
        super().__init__(name,desc,rarity,imageData, spriteID, attributes)
        sheet = Spritesheet(ARMORSPRITE)
        self.sprite = {
            'idle_left': AnimatedSprite(sheet, [(8, spriteID)], (16, 16), (64, 64), 12),
            'idle_right': AnimatedSprite(sheet, [(9, spriteID)], (16, 16), (64, 64), 12),
            'walk_left': AnimatedSprite(sheet, [(8, spriteID),(10, spriteID),(11, spriteID),(12, spriteID)], (16, 16), (64, 64), 12),
            'walk_right': AnimatedSprite(sheet, [(9, spriteID),(13, spriteID),(14, spriteID),(15, spriteID)], (16, 16), (64, 64), 12),
            'attack_left': AnimatedSprite(sheet, [(8, spriteID)], (16, 16), (64, 64), 9),
            'attack_right': AnimatedSprite(sheet, [(9, spriteID)], (16, 16), (64, 64), 9)
        }

class Weapon(Equipment):

    type = 'equipment'
    equipment_type = 'weapon'

    def __init__(self,name, desc, rarity, imageData, spriteID, attributes):
        super().__init__(name ,desc ,rarity ,imageData, spriteID, attributes)
        sheet = Spritesheet(ITEMSPRITE)

        spriteSpeed = attributes.get("speed", 15)
        self.sprite = {
            'idle_left': AnimatedSprite(sheet, [(0, spriteID)], (16, 16), (64, 64), 12),
            'idle_right': AnimatedSprite(sheet, [(1, spriteID)], (16, 16), (64, 64), 12),
            'walk_left': AnimatedSprite(sheet, [(0, spriteID)], (16, 16), (64, 64), 12),
            'walk_right': AnimatedSprite(sheet, [(1, spriteID)], (16, 16), (64, 64), 12),
            'attack_left': AnimatedSprite(sheet, [(0, spriteID),(2, spriteID),(3, spriteID)], (16, 16), (64, 64), spriteSpeed),
            'attack_right': AnimatedSprite(sheet, [(1, spriteID),(4, spriteID),(5, spriteID)], (16, 16), (64, 64), spriteSpeed)
        }

