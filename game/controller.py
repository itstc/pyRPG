import pygame as pg
import random
from sprite import EntityGroup

class EntityController:
    def __init__(self,player):
        self.entities = EntityGroup()
        self.entities.add(player)

    def spawnMobs(self,mobs,world):
        count = 0
        while count < 5 * world.level:
            # Get a random room and a random mob in a spawnable space in the room
            room = random.choice(world.getRooms())
            new_mob = random.choice(mobs)(room.getSpawnableSpace())

            # Spawn the mob if there are no other mobs on the tile
            if not pg.sprite.spritecollideany(new_mob,self.entities):
                self.entities.add(new_mob)

            count += 1

    def spawnItems(self,items,world):
        count = 0
        while count < 2 * world.level:
            room = random.choice(world.getRooms())
            new_item = random.choice(items).drop(room.getSpawnableSpace())

            if not pg.sprite.spritecollideany(new_item,self.entities):
                self.entities.add(new_item)

            count += 1

    def update(self,world,dt):
        self.entities.update(world,dt)

    def draw(self,surface,camera):
        self.entities.draw(surface,camera)