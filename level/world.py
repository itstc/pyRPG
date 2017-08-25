import pygame as pg
import math, random, numpy

from game.settings import TILE_SIZE
from game.tile import TileManager

class World:

    VOID = 0
    GRASS = 1
    FLOOR_1 = 2
    WALL = 3
    WATER = 4
    EXIT = 5

    def __init__(self, game, width, height):
        self.level = 1

        self.size_x = width
        self.size_y = height

        self.game = game
        self.tileset = TileManager()

        self.mapArr = numpy.array([[0]*width]*height)
        self.roomList = []


    def setTile(self, x, y, tile):
        try:
            self.mapArr[y][x] = tile
        except:
            pass

    def randomizeTiles(self, chance, base, new):

        if random.randrange(100) < chance:
            return new
        return base

    def getNeighbourData(self, x, y):
        # Returns a list of tile data around the position
        tiles = []
        y_range = (max(0, y - 1), min(y + 1, self.size_y - 1))
        x_range = (max(0, x - 1), min(x + 1, self.size_x - 1))

        for yy in range(y_range[0], y_range[1] + 1):
            for xx in range(x_range[0], x_range[1] + 1):
                if xx == x and yy == y:
                    continue
                else:
                    tiles.append(self.mapArr[yy][xx])

        return tiles

    def getNeighbourPosition(self, x, y):
        # Returns a list of tile positions around the tile[x,y]

        y_range = (max(0, y - 1), min(y + 1, self.size_y - 1))
        x_range = (max(0, x - 1), min(x + 1, self.size_x - 1))

        return [(x_range[0], y), (x_range[1], y),
                (x, y_range[0]), (x, y_range[1])]

    def carvePath(self, start, end, tile):
        current = start

        while current[0] != end[0] or current[1] != end[1]:
            angle = math.atan2((end[1] - current[1]), (end[0] - current[0]))
            new_x = current[0] + round(1 * math.cos(angle))
            new_y = current[1] + round(1 * math.sin(angle))

            self.setTile(new_x, new_y, Forest.GRASS)
            self.setTile(new_x - 1, new_y, Forest.GRASS)
            self.setTile(new_x, new_y - 1, Forest.GRASS)

            current = (new_x, new_y)

    def floodFill(self, position, target, new):
        if self.mapArr[position[1]][position[0]] != target:
            return

        self.setTile(position[0], position[1], new)
        self.floodFill((position[0],min(position[1] + 1, self.size_y - 1)), target, new)
        self.floodFill((position[0], max(0, position[1] - 1)), target, new)
        self.floodFill((min(position[0] + 1, self.size_x - 1), position[1]), target, new)
        self.floodFill((max(0, position[0] - 1), position[1]), target, new)

    def borderFill(self, position, target, new):
        for pos in self.getNeighbourPosition(position[0], position[1]):
            if self.mapArr[pos[1]][pos[0]] == target:
                self.setTile(position[0], position[1], new)

    def drawCircle(self, x, y, radius, tile):
        for yy in range(-radius, radius + 1):
            for xx in range(-radius, radius + 1):
                if xx**2 + yy**2 <= radius**2:
                    self.setTile(x + xx, y + yy, tile)

        self.roomList.append(World.Room(self, x - radius//4, y - radius//4, radius, radius))


    def cellGeneration(self, dead, live):
        # Goes through every tile on the map and uses the neighbours to determine the tile data

        for y in range(self.size_y):
            for x in range(self.size_x):
                if self.mapArr[y][x] in (dead, live):
                    count = 0
                    for neighbour in self.getNeighbourData(x, y):
                        if neighbour == live:
                            count += 1

                    self.setTile(x, y, self.cellRule(self.mapArr[y][x], count, dead, live))

    def cellRule(self, tile, count, dead, live):

        if tile == live and count >= 4:
            return live

        if tile == dead and count >= 5:
            return live

        return dead

    def spreadPoints(self, checkpoints):
        # Use Llyod's algorithm to spread the points by averaging centroid every iteration

        regions = [[i] for i in checkpoints]

        for cell in [(x,y) for x in range(self.size_x) for y in range(self.size_y)]:

            nearestDistanceSquared = 100000

            for i in range(len(checkpoints)):
                offset = (checkpoints[i][0] - cell[0]) ** 2 + (checkpoints[i][1] - cell[1]) ** 2
                if offset < nearestDistanceSquared:
                    nearestDistanceSquared = offset
                    nearest = i

            regions[nearest].append(cell)

            new_checkpoint = []

            for area in regions:
                x = 0
                y = 0

                for points in area:
                    x += points[0]
                    y += points[1]

                new_checkpoint.append((round(x/len(area)), round(y/len(area))))

        return new_checkpoint

    def render(self,surface,camera):
        start = camera.rect.topleft
        end = camera.rect.bottomright

        # amount of tiles to render on x and y
        render_x = [start[0] // TILE_SIZE[0], math.ceil(end[0] / TILE_SIZE[0])]
        render_y = [start[1] // TILE_SIZE[1], math.ceil(end[1] / TILE_SIZE[1])]

        for y in range(max(0,render_y[0]), min(render_y[1], self.size_y)):
            for x in range(max(0,render_x[0]), min(render_x[1], self.size_x)):
                px = x * TILE_SIZE[0] - start[0]
                py = y * TILE_SIZE[1] - start[1]
                surface.blit(self.tileset[self.mapArr[y][x]], (px,py))

    def getCollidableTiles(self, rect):
        start_pos = rect.topleft
        end_pos =  rect.bottomright
        render_x = [start_pos[0]//TILE_SIZE[0], end_pos[0]//TILE_SIZE[0]]
        render_y = [start_pos[1]//TILE_SIZE[1], end_pos[1]//TILE_SIZE[1]]

        for y in range(max(0,render_y[0] - 1), min(render_y[1] + 1,self.size_y)):
            for x in range(max(0,render_x[0] -  1), min(render_x[1] + 1,self.size_x)):
                if self.mapArr[y][x] in [World.WALL, World.WATER, World.EXIT]:
                    if self.mapArr[y][x] == Forest.EXIT:
                        obj = World.ExitObject(self.game, x, y)
                    else:
                        obj = World.WorldObject(x, y)
                    yield obj

    def getSpawn(self):
        return(self.spawnx, self.spawny)

    def getRooms(self):
        return self.roomList[1:]

    class WorldObject():

        type = 'wall'
        collidable = True

        def __init__(self, x, y):
            self.rect = pg.Rect((x * TILE_SIZE[0], y * TILE_SIZE[1]), TILE_SIZE)

    class ExitObject(WorldObject):

        type = 'world'
        collidable = False

        def __init__(self, game, x, y):
            super().__init__(x, y)
            self.game = game

        def interact(self):
            self.game.generateLevel()

    class Room():
        def __init__(self, world, x, y, w, h):
            self.world = world
            self.x1 = x
            self.y1 = y
            self.x2 = x + w - 1
            self.y2 = y + h - 1
            self.w = w
            self.h = h

        def center(self):
            return ((self.x1 + self.x2) // 2, (self.y1 + self.y2) // 2)

        def getSpawnableSpace(self):
            mapData = self.world.mapArr
            spawnable = False
            x = 0
            y = 0
            while not spawnable:
                x = random.randrange(self.x1, self.x2)
                y = random.randrange(self.y1, self.y2)
                floor_tiles = (World.GRASS, World.FLOOR_1)
                if mapData[y - 1][x] in floor_tiles and mapData[y + 1][x] in floor_tiles and mapData[y][
                            x - 1] in floor_tiles and mapData[y][x + 1] in floor_tiles:
                    spawnable = True

            return [x * TILE_SIZE[0], y * TILE_SIZE[1]]

        def getSurroundingTiles(self, x, y):
            mapData = self.world.mapArr
            return (mapData[y - 1][x], mapData[y + 1][x], mapData[y][x - 1], mapData[y][x + 1])

        def getCorner(self):
            return (self.x1 * TILE_SIZE[0], self.y1 * TILE_SIZE[1])

        def getCornerTile(self):
            return random.choice([(self.x1, self.y1), (self.x2, self.y1), (self.x1, self.y2), (self.x2, self.y2)])

        def getCornerTiles(self):
            return ((self.x1, self.y1), (self.x2, self.y1), (self.x1, self.y2), (self.x2, self.y2))


class Forest(World):

    def __init__(self, game):
        super().__init__(game, 48, 32)

        self.mapArr = [[self.randomizeTiles(45, Forest.WALL, Forest.WATER) for x in range(self.size_x)] for y in range(self.size_y)]

        for i in range(10):
            self.cellGeneration(Forest.WALL, Forest.WATER)

        checkpoints = [(random.randrange(self.size_x), random.randrange(self.size_y)) for i in range(3)]

        for i in range(5):
            checkpoints = self.spreadPoints(checkpoints)

        for i in range(len(checkpoints)):
            self.drawCircle(checkpoints[i][0], checkpoints[i][1], 5, Forest.GRASS)
            self.carvePath(checkpoints[i], checkpoints[min(i + 1, len(checkpoints) - 1)], Forest.GRASS)

        wall = ((x, y) for x in range(self.size_x) for y in range(self.size_y) if self.mapArr[y][x] == Forest.WATER)

        for point in wall:
            self.borderFill(point, Forest.GRASS, Forest.WALL)

        for i in range(5):
            self.cellGeneration(Forest.WALL, Forest.WATER)

        self.spawnx = self.roomList[0].center()[0] * TILE_SIZE[0]
        self.spawny = self.roomList[0].center()[1] * TILE_SIZE[1]

        lastRoom = self.getRooms()[-1].center()
        self.setTile(lastRoom[0], lastRoom[1], Forest.EXIT)