import pygame as pg
import random,json,settings
import sprite
from mobs import Player
from particles import BouncyText as Text

class Item:
    type = 'item'
    stackable = False
    def __init__(self, name, desc, rarity, imageData):
        self.name = name
        self.desc = desc
        self.rarity = rarity
        self.image = sprite.Spritesheet(settings.ITEMSHEET).getSprite(imageData[0], imageData[1])
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
            if self.rect.colliderect(obj.rect) and isinstance(obj,Player):
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
    def __init__(self,name,desc,rarity,imageData,attribute):
        super().__init__(name,desc,rarity,imageData)

        self.attribute = attribute

    def use(self,player):
        player.stats.statQueue.append(Text(player.stats,self.attribute,[player.rect.centerx,player.rect.top],2,pg.Color(76, 243, 94),pg.Color(101, 199, 2)))
        if player.stats.hp + self.attribute > player.stats.maxHP:
            player.stats.hp = player.stats.maxHP
        else:
            player.stats.hp += self.attribute

class Equipment(Item, UsableItem):

    type = 'equipment'

    def __init__(self, name, desc, rarity, imageData, spriteID, attribute):
        super().__init__(name, desc, rarity, imageData)
        self.attribute = attribute

    def use(self,player):
        player.stats.ad += self.attribute

    def unequip(self, player):
        player.stats.ad -= self.attribute

class Head(Equipment):
    equipment_type = 'head'

    def __init__(self, name, desc, rarity, imageData, spriteID, attribute):
        super().__init__(name,desc,rarity,imageData, spriteID, attribute)
        sheet = sprite.Spritesheet(settings.ARMORSPRITE)
        self.sprite = {
            'idle_left': sprite.AnimatedSprite(sheet, [(0, spriteID)], (16, 16), (64, 64), 12),
            'idle_right': sprite.AnimatedSprite(sheet, [(1, spriteID)], (16, 16), (64, 64), 12),
            'walk_left': sprite.AnimatedSprite(sheet, [(0, spriteID)], (16, 16), (64, 64), 12),
            'walk_right': sprite.AnimatedSprite(sheet, [(1, spriteID)], (16, 16), (64, 64), 12),
            'attack_left': sprite.AnimatedSprite(sheet, [(0, spriteID)], (16, 16), (64, 64), 9),
            'attack_right': sprite.AnimatedSprite(sheet, [(1, spriteID)], (16, 16), (64, 64), 9)
        }

class Body(Equipment):
    equipment_type = 'body'

    def __init__(self, name, desc, rarity, imageData, spriteID, attribute):
        super().__init__(name,desc,rarity,imageData, spriteID, attribute)
        sheet = sprite.Spritesheet(settings.ARMORSPRITE)
        self.sprite = {
            'idle_left': sprite.AnimatedSprite(sheet, [(2, spriteID)], (16, 16), (64, 64), 12),
            'idle_right': sprite.AnimatedSprite(sheet, [(3, spriteID)], (16, 16), (64, 64), 12),
            'walk_left': sprite.AnimatedSprite(sheet, [(2, spriteID)], (16, 16), (64, 64), 12),
            'walk_right': sprite.AnimatedSprite(sheet, [(3, spriteID)], (16, 16), (64, 64), 12),
            'attack_left': sprite.AnimatedSprite(sheet, [(2, spriteID), (4, spriteID), (5, spriteID)], (16, 16), (64, 64), 9),
            'attack_right': sprite.AnimatedSprite(sheet, [(3, spriteID), (6, spriteID), (7, spriteID)], (16, 16), (64, 64), 9)
        }

class Leg(Equipment):
    equipment_type = 'leg'

    def __init__(self, name, desc, rarity, imageData, spriteID, attribute):
        super().__init__(name,desc,rarity,imageData, spriteID, attribute)
        sheet = sprite.Spritesheet(settings.ARMORSPRITE)
        self.sprite = {
            'idle_left': sprite.AnimatedSprite(sheet, [(8, spriteID)], (16, 16), (64, 64), 12),
            'idle_right': sprite.AnimatedSprite(sheet, [(9, spriteID)], (16, 16), (64, 64), 12),
            'walk_left': sprite.AnimatedSprite(sheet, [(8, spriteID),(10, spriteID),(11, spriteID),(12, spriteID)], (16, 16), (64, 64), 12),
            'walk_right': sprite.AnimatedSprite(sheet, [(9, spriteID),(13, spriteID),(14, spriteID),(15, spriteID)], (16, 16), (64, 64), 12),
            'attack_left': sprite.AnimatedSprite(sheet, [(8, spriteID)], (16, 16), (64, 64), 9),
            'attack_right': sprite.AnimatedSprite(sheet, [(9, spriteID)], (16, 16), (64, 64), 9)
        }

class Weapon(Equipment):

    type = 'equipment'
    equipment_type = 'weapon'

    def __init__(self,name, desc, rarity, imageData, spriteID, attribute):
        super().__init__(name,desc,rarity,imageData, spriteID, attribute)
        sheet = sprite.Spritesheet(settings.ITEMSPRITE)
        self.sprite = {
            'idle_left': sprite.AnimatedSprite(sheet, [(0, spriteID)], (16, 16), (64, 64), 12),
            'idle_right': sprite.AnimatedSprite(sheet, [(1, spriteID)], (16, 16), (64, 64), 12),
            'walk_left': sprite.AnimatedSprite(sheet, [(0, spriteID)], (16, 16), (64, 64), 12),
            'walk_right': sprite.AnimatedSprite(sheet, [(1, spriteID)], (16, 16), (64, 64), 12),
            'attack_left': sprite.AnimatedSprite(sheet, [(0, spriteID),(2, spriteID),(3, spriteID)], (16, 16), (64, 64), 9),
            'attack_right': sprite.AnimatedSprite(sheet, [(1, spriteID),(4, spriteID),(5, spriteID)], (16, 16), (64, 64), 9)
        }

class ItemController():
    itemClass = {'Consumable': Consumable,
                 'Head': Head,
                 'Body': Body,
                 'Leg': Leg,
                 'Weapon': Weapon}

    def __init__(self,file):
        self.amount = 0
        with open(file,'r') as f:
            self.data = json.load(f)

            for i in self.data:
                self.amount += 1

    def getItem(self,id):
        # Creates a item class for the item based on 'class' key in id
        item = self.data[str(id)]
        cls = ItemController.itemClass[item['class']]

        if cls.type == 'equipment':
            itemClass = cls(item['name'],item['desc'],item['rarity'],item['imageData'],item['spriteID'],item['attribute'])
        else:
            itemClass =  cls(item['name'],item['desc'],item['rarity'],item['imageData'],item['attribute'])

        return itemClass

    def getItems(self):
        return [self.getItem(id) for id in range(self.amount)]

    def getRandomItem(self):
        return self.getItem(random.randrange(self.amount))




