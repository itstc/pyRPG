#TODO: convert tmx file to world object

import pygame as pg
import math, random
from pytmx.util_pygame import load_pygame

from sprite import Spritesheet as spritesheet

class World:
    size = [64,64]
    def __init__(self,surface,file):
        self.surface = surface
        self.mapData = load_pygame(file)
        self.scale = pg.transform.scale

    def render(self,camera):
        # Gets the tiles based on camera location and blits to game.surface
        offset = camera.getView()
        renderDistance = [self.surface.get_width(),self.surface.get_height()]
        for y in range(offset[1]//World.size[1] ,math.ceil((offset[1] + renderDistance[1]) / World.size[1])):
            for x in range(offset[0]//World.size[0], math.ceil((offset[0] + renderDistance[0]) / World.size[0])):
                try:
                    image = self.mapData.get_tile_image(x,y,0)
                    image = self.scale(image,World.size)

                except:
                    continue
                px = x * World.size[0]  - offset[0]
                py = y * World.size[1] - offset[1]
                self.surface.blit(image,(px,py))


    def getCollidableTiles(self, rect):
        collidables = []
        start = rect.topleft
        end = rect.bottomright
        for y in range(start[1] // World.size[1], end[1] // World.size[1] + 1):
            for x in range(start[0] // World.size[0], end[0] // World.size[0] + 1):
                try:
                    tile = self.mapData.get_tile_properties(x,y,0)
                    if tile['collidable'] == 'true':
                        collidables.append(WorldObject(pg.Rect((x * World.size[0], y * World.size[1]),World.size),'collidable'))
                except:
                    continue
        return collidables

    def getData(self):
        return self.mapData

    def getWorldSize(self):
        return (self.mapData.width * World.size[0], self.mapData.height * World.size[1])

class WorldObject:
    collidable = True
    def __init__(self,rect,property):
        self.rect = rect
        self.property = property

class Dungeon():
    tile_size = [64,64]
    def __init__(self,size):
        sheet = spritesheet('test.png')
        self.tiles = {
            0:pg.Surface(Dungeon.tile_size),
            1: pg.transform.scale(sheet.getSprite([16,16],[0,0]),Dungeon.tile_size)
                      }

        self.map = [[0 for x in range(size[0])] for y in range(size[1])]
        self.map_size = size

        self.spawn = [0,0]
        self.exit = [0,0]

        self.createDungeon()

    def create_room(self,room):
        for y in range(room.y1,room.y2 + 1):
            for x in range(room.x1, room.x2 + 1):
                self.map[y][x] = 1

    def create_h_tunnel(self,x1,x2,y):
        for x in range(min(x1,x2),max(x1,x2) + 1):
            self.map[y][x] = 1

    def create_v_tunnel(self,y1,y2,x):
        for y in range(min(y1,y2),max(y1,y2) + 1):
            self.map[y][x] = 1

    def createDungeon(self):
        ROOM_MAX_SIZE = 6
        ROOM_MIN_SIZE = 2
        MAX_ROOMS = 30

        rooms = []
        num_rooms = 0

        for r in range(MAX_ROOMS):
            w = random.randint(ROOM_MIN_SIZE,ROOM_MAX_SIZE)
            h = random.randint(ROOM_MIN_SIZE,ROOM_MAX_SIZE)

            x = random.randint(0,self.map_size[0] - w -1)
            y = random.randint(0,self.map_size[1] - h -1)

            new_room = Dungeon.Room(x,y,w,h)

            failed = False
            for other_room in rooms:
                if new_room.intersect(other_room):
                    failed = True
                    break

            if not failed:
                self.create_room(new_room)
                (new_x,new_y) = new_room.center()

                if num_rooms == 0:
                    self.spawn = (new_x*Dungeon.tile_size[0],new_y*Dungeon.tile_size[1])
                else:
                    # If another room, create a tunnel passage
                    (prev_x,prev_y) = rooms[num_rooms-1].center()
                    if random.randint(0,1) == 1:
                        self.create_h_tunnel(prev_x, new_x, prev_y)
                        self.create_v_tunnel(prev_y, new_y, new_x)
                    else:
                        self.create_v_tunnel(prev_y, new_y, prev_x)
                        self.create_h_tunnel(prev_x, new_x, new_y)

                rooms.append(new_room)
                num_rooms += 1

        self.exit = rooms[num_rooms - 1].center()

    def render(self,surface,camera):
        offset = camera.getView()
        renderDistance = [surface.get_width(),surface.get_height()]
        render_x = [offset[0] // Dungeon.tile_size[0], math.ceil((offset[0] + renderDistance[0]) / World.size[0])]
        render_y = [offset[1] // Dungeon.tile_size[1], math.ceil((offset[1] + renderDistance[1]) / World.size[1])]

        for y in range(render_y[0],render_y[1]):
            for x in range(render_x[0],render_x[1]):
                try:
                    image = self.tiles[self.map[y][x]]
                except:
                    continue
                px = x * Dungeon.tile_size[0] - offset[0]
                py = y * Dungeon.tile_size[1] - offset[1]
                surface.blit(image,(px,py))

    def getCollidableTiles(self, rect):
        return []

    def getWorldSize(self):
        return (self.map_size[0] * World.size[0], self.map_size[1] * World.size[1])

    class Room():
        def __init__(self,x,y,w,h):
            self.x1 = x
            self.y1 = y
            self.x2 = x + w
            self.y2 = y + h

        def center(self):
            x = (self.x1 + self.x2) // 2
            y = (self.y1 + self.y2) // 2
            return (x,y)

        def intersect(self,other):
            return (self.x1 <= other.x2 and self.x2 >= other.x1 and
                    self.y1 <= other.y2 and self.y2 >= other.y1)




