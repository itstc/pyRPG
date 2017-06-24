import pygame as pg
import random
import settings
from sprite import EntityGroup
from gameobjects import Chest

class EntityController:
    def __init__(self):
        self.entities = EntityGroup()

    def spawnMobs(self,mobs,world):
        count = 0
        while count < 2 * world.level:
            # Get a random room and a random mob in a spawnable space in the room
            room = random.choice(world.getRooms())
            new_mob = random.choice(mobs)(self.entities, room.getSpawnableSpace())

            # Spawn the mob if there are no other mobs on the tile
            if not pg.sprite.spritecollideany(new_mob,self.entities):
                self.entities.add(new_mob)
            else:
                new_mob.kill()

            count += 1

    def spawnItems(self,items,world):
        count = 0
        while count < 4 * world.level:
            room = random.choice(world.getRooms())
            new_item = random.choice(items).drop(room.getSpawnableSpace())

            if not pg.sprite.spritecollideany(new_item,self.entities):
                self.entities.add(new_item)

            count += 1

    def spawnChest(self, game, itemManager, world):
        count = 0
        while count < 3 * world.level:
            room = random.choice(world.getRooms())
            corners = random.choice(room.getCornerTiles()[:1]) # Get top corners only and select random corner after
            chest = Chest(game, itemManager, self.entities, (corners[0] * settings.TILE_SIZE[0], corners[1] * settings.TILE_SIZE[1]))

            # If no entities are in that position and there are at least 2 walls surrounding it then add it to the game
            if not pg.sprite.spritecollideany(chest,self.entities): #and len([wall for wall in room.getSurroundingTiles(corners[0], corners[1]) if wall in (3,4)]) >= 2:
                self.entities.add(chest)

            count += 1

    def update(self,world,dt):
        self.entities.update(world,dt)

    def draw(self,surface,camera):
        self.entities.draw(surface,camera)