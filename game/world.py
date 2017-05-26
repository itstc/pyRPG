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


class dMap:
    tile_size = [64,64]

    def __init__(self):
        self.roomList = []
        self.cList = []

        sheet = spritesheet('tilesheet.png')
        self.tiles = {
            0: pg.transform.scale(sheet.getSprite([16, 16], [3, 0]), Dungeon.tile_size),
            1: pg.Surface(dMap.tile_size),
            2: pg.transform.scale(sheet.getSprite([16, 16], [2, 0]), Dungeon.tile_size),
            3: pg.transform.scale(sheet.getSprite([16, 16], [5, 0]), Dungeon.tile_size),
            4: pg.transform.scale(sheet.getSprite([16, 16], [5, 0]), Dungeon.tile_size),
            5: pg.transform.scale(sheet.getSprite([16, 16], [1, 0]), Dungeon.tile_size),
            6: pg.transform.scale(sheet.getSprite([16, 16], [5, 0]), Dungeon.tile_size),
            7: pg.transform.scale(sheet.getSprite([16, 16], [4, 0]), Dungeon.tile_size)
                      }

    def makeMap(self, xsize, ysize, fail, b1, mrooms):
        """Generate random layout of rooms, corridors and other features"""
        # makeMap can be modified to accept arguments for values of failed, and percentile of features.
        # Create first room
        self.size_x = xsize
        self.size_y = ysize
        # initialize map to all walls
        self.mapArr = []
        for y in range(ysize):
            tmp = []
            for x in range(xsize):
                tmp.append(1)
            self.mapArr.append(tmp)

        w, l, t = self.makeRoom()
        while len(self.roomList) == 0:
            y = random.randrange(ysize - 1 - l) + 1
            x = random.randrange(xsize - 1 - w) + 1
            p = self.placeRoom(l, w, x, y, xsize, ysize, 6, 0)
        failed = 0
        while failed < fail:  # The lower the value that failed< , the smaller the dungeon
            chooseRoom = random.randrange(len(self.roomList))
            ex, ey, ex2, ey2, et = self.makeExit(chooseRoom)
            feature = random.randrange(100)
            if feature < b1:  # Begin feature choosing (more features to be added here)
                w, l, t = self.makeCorridor()
            else:
                w, l, t = self.makeRoom()
            roomDone = self.placeRoom(l, w, ex2, ey2, xsize, ysize, t, et)
            if roomDone == 0:  # If placement failed increase possibility map is full
                failed += 1
            elif roomDone == 2:  # Possiblilty of linking rooms
                if self.mapArr[ey2][ex2] == 0:
                    if random.randrange(100) < 7:
                        self.makePortal(ex, ey)
                    failed += 1
            else:  # Otherwise, link up the 2 rooms
                self.makePortal(ex, ey)
                failed = 0
                if t < 5:
                    tc = [len(self.roomList) - 1, ex2, ey2, t]
                    self.cList.append(tc)
                    self.joinCorridor(len(self.roomList) - 1, ex2, ey2, t, 50)
            if len(self.roomList) == mrooms:
                failed = fail
        self.finalJoins()
        self.spawn = self.getCenterTile(self.roomList[0])

        finalRoom = self.getCenterTile(self.roomList[-1])
        self.mapArr[finalRoom[1]//dMap.tile_size[1]][finalRoom[0]//dMap.tile_size[1]] = 6

        walls = [(y,x) for y in range(self.size_y) for x in range(self.size_x) if self.mapArr[y][x] == 7]
        print(walls)
        for wall in walls:
            try:
                if self.mapArr[wall[0]+1][wall[1]] == 0:
                    self.mapArr[wall[0]][wall[1]] = 2
            except:
                continue

    def getCenterTile(self,room):
        return ((room[2] * 2 + room[1])//2 * dMap.tile_size[0],(room[3] * 2 + room[0])//2 * dMap.tile_size[0])

    def makeRoom(self):
        """Randomly produce room size"""
        rtype = 5
        rwide = random.randrange(8) + 3
        rlong = random.randrange(8) + 3
        return rwide, rlong, rtype

    def makeCorridor(self):
        """Randomly produce corridor length and heading"""
        clength = random.randrange(18) + 3
        heading = random.randrange(4)
        if heading == 0:  # North
            wd = 1
            lg = -clength
        elif heading == 1:  # East
            wd = clength
            lg = 1
        elif heading == 2:  # South
            wd = 1
            lg = clength
        elif heading == 3:  # West
            wd = -clength
            lg = 1
        return wd, lg, heading

    def placeRoom(self, ll, ww, xposs, yposs, xsize, ysize, rty, ext):
        """Place feature if enough space and return canPlace as true or false"""
        # Arrange for heading
        xpos = xposs
        ypos = yposs
        if ll < 0:
            ypos += ll + 1
            ll = abs(ll)
        if ww < 0:
            xpos += ww + 1
            ww = abs(ww)
        # Make offset if type is room
        if rty == 5:
            if ext == 0 or ext == 2:
                offset = random.randrange(ww)
                xpos -= offset
            else:
                offset = random.randrange(ll)
                ypos -= offset
        # Then check if there is space
        canPlace = 1
        if ww + xpos + 1 > xsize - 1 or ll + ypos + 1 > ysize:
            canPlace = 0
            return canPlace
        elif xpos < 1 or ypos < 1:
            canPlace = 0
            return canPlace
        else:
            for j in range(ll):
                for k in range(ww):
                    if self.mapArr[(ypos) + j][(xpos) + k] != 1:
                        canPlace = 2
        # If there is space, add to list of rooms
        if canPlace == 1:
            temp = [ll, ww, xpos, ypos]
            self.roomList.append(temp)
            for j in range(ll + 2):  # Then build walls
                for k in range(ww + 2):
                    wall_orientation = 7
                    self.mapArr[(ypos - 1) + j][(xpos - 1) + k] = wall_orientation
            for j in range(ll):  # Then build floor
                for k in range(ww):
                    self.mapArr[ypos + j][xpos + k] = 0
        return canPlace  # Return whether placed is true/false

    def makeExit(self, rn):
        """Pick random wall and random point along that wall"""
        room = self.roomList[rn]
        while True:
            rw = random.randrange(4)
            if rw == 0:  # North wall
                rx = random.randrange(room[1]) + room[2]
                ry = room[3] - 1
                rx2 = rx
                ry2 = ry - 1
            elif rw == 1:  # East wall
                ry = random.randrange(room[0]) + room[3]
                rx = room[2] + room[1]
                rx2 = rx + 1
                ry2 = ry
            elif rw == 2:  # South wall
                rx = random.randrange(room[1]) + room[2]
                ry = room[3] + room[0]
                rx2 = rx
                ry2 = ry + 1
            elif rw == 3:  # West wall
                ry = random.randrange(room[0]) + room[3]
                rx = room[2] - 1
                rx2 = rx - 1
                ry2 = ry
            if self.mapArr[ry][rx] == 7:  # If space is a wall, exit
                break
        return rx, ry, rx2, ry2, rw

    def makePortal(self, px, py):
        """Create doors in walls"""
        ptype = random.randrange(100)
        if ptype > 95:  # Secret door
            self.mapArr[py][px] = 5
            return
        elif ptype > 75:  # Closed door
            self.mapArr[py][px] = 4
            return
        elif ptype > 40:  # Open door
            self.mapArr[py][px] = 3
            return
        else:  # Hole in the wall
            self.mapArr[py][px] = 2
            self.mapArr[py][px] = 0

    def joinCorridor(self, cno, xp, yp, ed, psb):
        """Check corridor endpoint and make an exit if it links to another room"""
        cArea = self.roomList[cno]
        if xp != cArea[2] or yp != cArea[3]:  # Find the corridor endpoint
            endx = xp - (cArea[1] - 1)
            endy = yp - (cArea[0] - 1)
        else:
            endx = xp + (cArea[1] - 1)
            endy = yp + (cArea[0] - 1)
        checkExit = []
        if ed == 0:  # North corridor
            if endx > 1:
                coords = [endx - 2, endy, endx - 1, endy]
                checkExit.append(coords)
            if endy > 1:
                coords = [endx, endy - 2, endx, endy - 1]
                checkExit.append(coords)
            if endx < self.size_x - 2:
                coords = [endx + 2, endy, endx + 1, endy]
                checkExit.append(coords)
        elif ed == 1:  # East corridor
            if endy > 1:
                coords = [endx, endy - 2, endx, endy - 1]
                checkExit.append(coords)
            if endx < self.size_x - 2:
                coords = [endx + 2, endy, endx + 1, endy]
                checkExit.append(coords)
            if endy < self.size_y - 2:
                coords = [endx, endy + 2, endx, endy + 1]
                checkExit.append(coords)
        elif ed == 2:  # South corridor
            if endx < self.size_x - 2:
                coords = [endx + 2, endy, endx + 1, endy]
                checkExit.append(coords)
            if endy < self.size_y - 2:
                coords = [endx, endy + 2, endx, endy + 1]
                checkExit.append(coords)
            if endx > 1:
                coords = [endx - 2, endy, endx - 1, endy]
                checkExit.append(coords)
        elif ed == 3:  # West corridor
            if endx > 1:
                coords = [endx - 2, endy, endx - 1, endy]
                checkExit.append(coords)
            if endy > 1:
                coords = [endx, endy - 2, endx, endy - 1]
                checkExit.append(coords)
            if endy < self.size_y - 2:
                coords = [endx, endy + 2, endx, endy + 1]
                checkExit.append(coords)
        for xxx, yyy, xxx1, yyy1 in checkExit:  # Loop through possible exits
            if self.mapArr[yyy][xxx] == 0:  # If joins to a room
                if random.randrange(100) < psb:  # Possibility of linking rooms
                    self.makePortal(xxx1, yyy1)

    def finalJoins(self):
        """Final stage, loops through all the corridors to see if any can be joined to other rooms"""
        for x in self.cList:
            self.joinCorridor(x[0], x[1], x[2], x[3], 10)

    def render(self,surface,camera):
        offset = camera.getView()
        renderDistance = [surface.get_width(),surface.get_height()]
        render_x = [offset[0] // dMap.tile_size[0], math.ceil((offset[0] + renderDistance[0]) / dMap.tile_size[0])]
        render_y = [offset[1] // dMap.tile_size[1], math.ceil((offset[1] + renderDistance[1]) / dMap.tile_size[1])]

        for y in range(render_y[0],render_y[1]):
            for x in range(render_x[0],render_x[1]):
                try:
                    tile_id = self.mapArr[y][x]
                    image = self.tiles[tile_id]
                    if tile_id == 1: image.fill(pg.Color(51,51,51))
                except:
                    continue
                px = x * dMap.tile_size[0] - offset[0]
                py = y * dMap.tile_size[1] - offset[1]
                surface.blit(image,(px,py))

    def getCollidableTiles(self, rect):
        return []

    def getWorldSize(self):
        return (self.size_x * dMap.tile_size[0], self.size_y * dMap.tile_size[1])

