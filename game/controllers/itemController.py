import pygame as pg
import random, json

from game.settings import TILE_SIZE
from gameobject.objectgroup import EntityGroup
from gameobject.gameobjects import Chest

from item.items import Consumable, Head, Body, Leg, Weapon

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
            itemClass = cls(item['name'],item['desc'],item['rarity'],item['imageData'],item['spriteID'],item['attributes'])
        else:
            itemClass =  cls(item['name'],item['desc'],item['rarity'],item['imageData'],item['attributes'])

        return itemClass

    def getItems(self):
        return [self.getItem(id) for id in range(self.amount)]

    def getRandomItem(self):
        return self.getItem(random.randrange(self.amount))
