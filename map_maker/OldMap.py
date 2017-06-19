class Map():

    TIME_PER_UPDATE = 60
    GRASS = 0
    WATER = 1
    WALL = 2
    EXIT = 3
    FLOOD_WATER = 4

    def __init__(self):

        self.mapArr = []
        self.time = 60

    def generateMap(self, size_x, size_y):

        self.size_x = size_x
        self.size_y = size_y

        self.roomList = []

        self.mapArr = [[self.randomizeTile() for x in range(size_x)] for y in range(size_y)]
        self.generation = 0


        # Create water streams using Cellular Automata
        while self.generation != 10:
            self.createGeneration(Map.WATER)


        # Pick 50% of Lakes
        for y in range(self.size_y):
            for x in range(self.size_x):
                if self.mapArr[y][x] == Map.WATER:
                    if random.randrange(100) > 50:
                        self.floodFill((x, y), Map.WATER, Map.WALL)
                    else:
                        self.floodFill((x, y), Map.WATER, Map.FLOOD_WATER)


        WATER_TILES = [(x,y) for x in range(self.size_x) for y in range(self.size_y) if self.mapArr[y][x] == Map.FLOOD_WATER]
        self.fillBorders(WATER_TILES, Map.WALL, Map.GRASS)

        # Create checkpoints and connect them with Lloyd's Algorithm
        self.checkpoints = []

        for i in range(4):
            self.checkpoints.append((random.randrange(0, self.size_x), random.randrange(0, self.size_y)))

        self.spreadPoints(5)

        for i in range(len(self.checkpoints)):
            self.mapArr[self.checkpoints[i][1]][self.checkpoints[i][0]] = Map.GRASS

            for tile in self.getMetaTiles(self.checkpoints[i]):
                if self.mapArr[tile[1]][tile[0]] == Map.WATER:
                    self.mapArr[tile[1]][tile[0]] = Map.GRASS

            maxIndex = min(i + 1, len(self.checkpoints) - 1)
            self.carvePath(self.checkpoints[i],self.checkpoints[maxIndex])

        for points in self.checkpoints:
            room = Map.Room(points[0], points[1], 3 + random.randrange(2), 3 + random.randrange(2))
            self.roomList.append(room)

            for y in range(room.y1, room.y2):
                for x in range(room.x1, room.x2):
                    self.mapArr[y][x] = Map.GRASS

        for hy in range(self.size_y):
            self.mapArr[hy][0] = Map.WALL
            self.mapArr[hy][self.size_x - 1] = Map.WALL
        for hx in range(self.size_x):
            self.mapArr[0][hx] = Map.WALL
            self.mapArr[self.size_y - 1][hx] = Map.WALL

        rp = self.roomList[-1].center()
        self.mapArr[rp[1]][rp[0]] = Map.EXIT


    def update(self, dt):
        self.time -= dt

        if self.time <= 0:
            self.time = Map.TIME_PER_UPDATE
            #self.createGeneration(Map.WATER)

    def randomizeTile(self):
        if random.randrange(100) > 45:
            return Map.WALL
        return Map.WATER


    def carvePath(self, start, end):
        current = start
        self.roomList.append(Map.Room(start[0], start[1], (end[0] - start[0]), (end[1] - start[1])))
        while (current[0] != end[0]) or (current[1] != end[1]):
            angle = math.atan2((end[1] - current[1]),(end[0] - current[0]))
            new_x = current[0] + round(1 * math.cos(angle))
            new_y = current[1] + round(1 * math.sin(angle))

            for point in self.getMetaTiles((new_x, new_y)):
                if self.mapArr[point[1]][point[0]] == Map.WALL:
                    self.mapArr[point[1]][point[0]] = Map.GRASS

            current = (new_x, new_y)

    def floodFill(self, position, target, new):
        if self.mapArr[position[1]][position[0]] != target:
            return

        self.mapArr[position[1]][position[0]] = new
        self.floodFill((position[0],min(position[1] + 1, self.size_y - 1)), target, new)
        self.floodFill((position[0], max(0, position[1] - 1)), target, new)
        self.floodFill((min(position[0] + 1, self.size_x - 1), position[1]), target, new)
        self.floodFill((max(0, position[0] - 1), position[1]), target, new)


    def fillBorders(self, areas, targetState, newState):
        for position in areas:
            tile = [(min(position[0] + 1, self.size_y - 1), max(0, position[1] - 1)),(min(position[0] + 1, self.size_y - 1), position[1]),
                    (min(position[0] + 1, self.size_y - 1), min(position[1] + 1, self.size_x - 1)),
                    (position[0], max(0, position[1] - 1)), (position[0], min(position[1] + 1, self.size_x - 1)),
                    (max(0, position[0] - 1), min(position[1] + 1, self.size_x - 1)), (max(0, position[0] - 1), position[1]),
                    (max(0, position[0] - 1), max(0, position[1] - 1))]

            for coord in tile:
                if self.mapArr[coord[1]][coord[0]] == targetState:
                    self.mapArr[coord[1]][coord[0]] = newState


    def getMetaTiles(self, position):
        tiles = []

        lx = max(0, position[0] - 1)
        hx = min(position[0] + 1, self.size_x - 1)
        ly = max(0, position[1] - 1)
        hy = min(position[1] + 1, self.size_y - 1)

        for y in range(ly, hy + 1):
            for x in range(lx, hx + 1):
                tiles.append((x,y))

        return tiles

    def spreadPoints(self, iterations):
        for iteration in range(5):

            regions = [[i] for i in self.checkpoints]

            for cell in [(x,y) for x in range(self.size_x) for y in range(self.size_y)]:

                nearestDistanceSquared = 100000

                for i in range(len(self.checkpoints)):
                    offset = (self.checkpoints[i][0] - cell[0]) ** 2 + (self.checkpoints[i][1] - cell[1]) ** 2
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

            self.checkpoints = new_checkpoint

    def createGeneration(self, live):
        self.generation += 1

        for y in range(self.size_y):
            for x in range(self.size_x):
                count = 0

                for cell in self.getMetaTiles((x,y)):
                    if self.mapArr[cell[1]][cell[0]] != live:
                        count += 1


                self.mapArr[y][x] = self.cellRule(self.mapArr[y][x], count)


    def cellRule(self, current, count):
        live_cell = Map.WATER
        dead_cell = Map.WALL

        if current == dead_cell and count < 4:
            return live_cell

        if current == live_cell and count < 6:
            return live_cell

        return dead_cell

    class Room():
        def __init__(self, x, y, w, h):
            self.x1 = x
            self.y1 = y
            self.x2 = x + w
            self.y2 = y + h
            self.w = w
            self.h = h

        def center(self):
            return ((self.x1 + self.x2 ) // 2, (self.y1 + self.y2) // 2)

class Dungeon:

    VOID = 0
    FLOOR = 1
    FLOOR_1 = 2
    WALL = 3
    WALL_1 = 4
    EXIT = 5

    def __init__(self,game):
        self.level = 0
        self.game = game
        self.tileset = tile.TileManager()

    def makeMap(self, xsize, ysize, fail, b1, mrooms):
        """Generate random layout of rooms, corridors and other features"""
        # makeMap can be modified to accept arguments for values of failed, and percentile of features.
        # Create first room
        self.level += 1
        self.roomList = []
        self.cList = []
        self.size_x = xsize
        self.size_y = ysize

        # initialize map to all walls
        self.mapArr = []

        for y in range(ysize):
            tmp = []
            for x in range(xsize):
                tmp.append(Dungeon.VOID)
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
                if self.mapArr[ey2][ex2] == Dungeon.FLOOR:
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

        spawn = self.getCenterPosition(self.roomList[0])
        self.spawnx = spawn[0]
        self.spawny = spawn[1]

        finalRoom = self.getCenterPosition(self.getRooms()[-1])
        fy = finalRoom[1]//settings.TILE_SIZE[1]
        fx = finalRoom[0]//settings.TILE_SIZE[0]
        # Exit Tile
        self.mapArr[fy][fx] = Dungeon.EXIT

        walls = [(y,x) for y in range(self.size_y) for x in range(self.size_x) if self.mapArr[y][x] == Dungeon.WALL]
        for wall in walls:
            try:
                if self.mapArr[wall[0]+1][wall[1]] in (Dungeon.FLOOR, Dungeon.FLOOR_1):
                    self.mapArr[wall[0]][wall[1]] = Dungeon.WALL_1
            except:
                continue


    def getSpawn(self):
        return (self.spawnx,self.spawny)

    def getCenterPosition(self,room):
        x = room.center()[0] * settings.TILE_SIZE[0]
        y = room.center()[1] * settings.TILE_SIZE[1]
        return [x,y]

    def getTile(self, position):
        mapX = round(position[0] / 96)
        mapY = round(position[1] / 96)
        return pg.Rect(mapX * 96, mapY * 96, 96, 96)

    def getRooms(self):
        return [room for room in self.roomList if isinstance(room,Dungeon.Room)]

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
                    if self.mapArr[(ypos) + j][(xpos) + k] != Dungeon.VOID:
                        canPlace = 2
        # If there is space, add to list of rooms
        if canPlace == 1:
            temp = [ll, ww, xpos, ypos]

            for j in range(ll + 2):  # Then build walls
                for k in range(ww + 2):
                    wx = (xpos - 1) + k
                    wy = (ypos - 1) + j
                    self.mapArr[wy][wx] = Dungeon.WALL
            for j in range(ll):  # Then build floor
                for k in range(ww):
                    if random.randrange(10) > 0:
                        tf = Dungeon.FLOOR
                    else:
                        tf = Dungeon.FLOOR_1

                    self.mapArr[ypos + j][xpos + k] = tf

            if rty == 5:
                self.roomList.append(Dungeon.Room(self, xpos, ypos, ww, ll))
            else:
                self.roomList.append(Dungeon.Hallway(self, xpos, ypos, ww, ll))

        return canPlace  # Return whether placed is true/false

    def makeExit(self, rn):
        """Pick random wall and random point along that wall"""
        room = self.roomList[rn]
        while True:
            rw = random.randrange(4)
            if rw == 0:  # North wall
                rx = random.randrange(room.x1,room.x2)
                ry = room.y1 - 1
                rx2 = rx
                ry2 = ry - 1
            elif rw == 1:  # East wall
                ry = random.randrange(room.y1,room.y2)
                rx = room.x2
                rx2 = rx + 1
                ry2 = ry
            elif rw == 2:  # South wall
                rx = random.randrange(room.x1,room.x2)
                ry = room.y2
                rx2 = rx
                ry2 = ry + 1
            elif rw == 3:  # West wall
                ry = random.randrange(room.y1,room.y2)
                rx = room.x1 - 1
                rx2 = rx - 1
                ry2 = ry
            if self.mapArr[ry][rx] == Dungeon.WALL:  # If space is a wall, exit
                break
        return rx, ry, rx2, ry2, rw

    def makePortal(self, px, py):
        """Create doors in walls"""
        self.mapArr[py][px] = Dungeon.FLOOR

    def joinCorridor(self, cno, xp, yp, ed, psb):
        """Check corridor endpoint and make an exit if it links to another room"""
        cArea = self.roomList[cno]
        if xp != cArea.x1 or yp != cArea.y1:  # Find the corridor endpoint
            endx = xp - (cArea.w - 1)
            endy = yp - (cArea.h - 1)
        else:
            endx = xp + (cArea.w - 1)
            endy = yp + (cArea.h - 1)
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
            if self.mapArr[yyy][xxx] == Dungeon.FLOOR:  # If joins to a room
                if random.randrange(100) < psb:  # Possibility of linking rooms
                    self.makePortal(xxx1, yyy1)

    def finalJoins(self):
        """Final stage, loops through all the corridors to see if any can be joined to other rooms"""
        for x in self.cList:
            self.joinCorridor(x[0], x[1], x[2], x[3], 10)

    def render(self,surface,camera):
        start = camera.rect.topleft
        end = camera.rect.bottomright

        # amount of tiles to render on x and y
        render_x = [start[0] // settings.TILE_SIZE[0], math.ceil(end[0] / settings.TILE_SIZE[0])]
        render_y = [start[1] // settings.TILE_SIZE[1], math.ceil(end[1] / settings.TILE_SIZE[1])]

        for y in range(max(0,render_y[0]), min(render_y[1], self.size_y)):
            for x in range(max(0,render_x[0]), min(render_x[1], self.size_x)):
                px = x * settings.TILE_SIZE[0] - start[0]
                py = y * settings.TILE_SIZE[1] - start[1]
                surface.blit(self.tileset[self.mapArr[y][x]], (px,py))

    def drawRoomOutline(self,surface,camera):
        for room in self.getRooms():
            rect = pg.Rect(room.x1*settings.TILE_SIZE[0],room.y1*settings.TILE_SIZE[1],room.w*settings.TILE_SIZE[0],room.h*settings.TILE_SIZE[1])
            camera.drawRectangle(surface,pg.Color('purple'),rect)

    def getCollidableTiles(self, rect):
        collidables = []
        start_pos = rect.topleft
        end_pos =  rect.bottomright
        render_x = [start_pos[0]//settings.TILE_SIZE[0], end_pos[0]//settings.TILE_SIZE[0]]
        render_y = [start_pos[1]//settings.TILE_SIZE[1], end_pos[1]//settings.TILE_SIZE[1]]

        for y in range(max(0,render_y[0] - 1), min(render_y[1] + 1,self.size_y)):
            for x in range(max(0,render_x[0] -  1), min(render_x[1] + 1,self.size_x)):
                if self.mapArr[y][x] in [Dungeon.WALL, Dungeon.WALL_1, Dungeon.EXIT]:
                    if self.mapArr[y][x] == Dungeon.EXIT:
                        obj = Dungeon.ExitObject(self.game, x, y)
                    else:
                        obj = Dungeon.WorldObject(x, y)

                    collidables.append(obj)

        return collidables

    def getWorldSize(self):
        return (self.size_x * settings.TILE_SIZE[0], self.size_y * settings.TILE_SIZE[1])

    class WorldObject():

        type = 'wall'
        collidable = True

        def __init__(self, x, y):
            self.rect = pg.Rect((x * settings.TILE_SIZE[0], y * settings.TILE_SIZE[1]), settings.TILE_SIZE)

    class ExitObject(WorldObject):

        type = 'world'
        collidable = False

        def __init__(self, game, x, y):
            super().__init__(x, y)
            self.game = game

        def interact(self):
            self.game.generateLevel()

    class Room():
        def __init__(self,world,x,y,w,h):
            self.world = world
            self.x1 = x
            self.y1 = y
            self.x2 = x + w - 1
            self.y2 = y + h - 1
            self.w = w
            self.h = h

        def center(self):
            return ((self.x1 + self.x2)//2,(self.y1 + self.y2)//2)

        def getSpawnableSpace(self):
            mapData = self.world.mapArr
            spawnable = False
            x = 0
            y = 0
            while not spawnable:
                x = random.randrange(self.x1,self.x2)
                y = random.randrange(self.y1,self.y2)
                floor_tiles = (Dungeon.FLOOR, Dungeon.FLOOR_1)
                if mapData[y-1][x] in floor_tiles and mapData[y+1][x] in floor_tiles and mapData[y][x-1] in floor_tiles and mapData[y][x+1] in floor_tiles:
                    spawnable = True

            return [x * settings.TILE_SIZE[0],y * settings.TILE_SIZE[1]]

        def getSurroundingTiles(self, x, y):
            mapData = self.world.mapArr
            return (mapData[y - 1][x], mapData[y + 1][x], mapData[y][x - 1], mapData[y][x + 1])

        def getCorner(self):
            return (self.x1 * settings.TILE_SIZE[0], self.y1 * settings.TILE_SIZE[1])

        def getCornerTile(self):
            return random.choice([(self.x1,self.y1), (self.x2, self.y1), (self.x1, self.y2), (self.x2, self.y2)])

        def getCornerTiles(self):
            return [(self.x1,self.y1), (self.x2, self.y1), (self.x1, self.y2), (self.x2, self.y2)]

    class Hallway():
        def __init__(self,world,x,y,w,h):
            self.world = world
            self.x1 = x
            self.y1 = y
            self.x2 = x + w
            self.y2 = y + h
            self.w = w
            self.h = h

        def center(self):
            return ((self.x1 + self.x2)//2,(self.y1 + self.y2)//2)


class Forest():

    TIME_PER_UPDATE = 60
    VOID = 0
    GRASS = 1
    FLOOR_1 = 2
    WALL = 3
    WATER = 4
    EXIT = 5

    def __init__(self, game):
        self.level = 0
        self.game = game
        self.tileset = tile.TileManager()
        self.mapArr = []
        self.time = 60

    def generateMap(self, size_x, size_y):

        self.level += 1

        self.size_x = size_x
        self.size_y = size_y

        self.roomList = []

        self.mapArr = [[self.randomizeTile() for x in range(size_x)] for y in range(size_y)]
        self.generation = 0

        # Create water streams using Cellular Automata
        while self.generation != 10:
            self.createGeneration(Forest.WATER)

        # Create checkpoints and connect them with Lloyd's Algorithm
        self.checkpoints = []

        for i in range(5):
            self.checkpoints.append((random.randrange(0, self.size_x), random.randrange(0, self.size_y)))

        self.spreadPoints(5)

        for i in range(len(self.checkpoints)):
            self.mapArr[self.checkpoints[i][1]][self.checkpoints[i][0]] = Forest.GRASS
            for tile in self.getMetaTiles(self.checkpoints[i]):
                self.mapArr[tile[1]][tile[0]] = Forest.GRASS

            maxIndex = min(i + 1, len(self.checkpoints) - 1)
            self.carvePath(self.checkpoints[i],self.checkpoints[maxIndex])

        for points in self.checkpoints:
            room_w = min(self.size_x - points[0], 3 + random.randrange(8))
            room_h = min(self.size_y - points[1], 3 + random.randrange(8))

            room = Forest.Room(self, points[0], points[1], room_w, room_h)
            self.roomList.append(room)

            for y in range(room.y1, room.y2):
                for x in range(room.x1, room.x2):
                    self.mapArr[y][x] = Forest.GRASS

        self.fillBorders([(x,y) for x in range(self.size_x) for y in range(self.size_y) if self.mapArr[y][x] == Forest.WATER], Forest.WATER, Forest.WALL)

        self.spawnx = self.roomList[0].center()[0] * settings.TILE_SIZE[0]
        self.spawny = self.roomList[0].center()[1] * settings.TILE_SIZE[1]

        rp = self.roomList[-1].center()
        self.mapArr[rp[1]][rp[0]] = Forest.EXIT

    def getSpawn(self):
        return (self.spawnx, self.spawny)

    def update(self, dt):
        self.time -= dt

        if self.time <= 0:
            self.time = Forest.TIME_PER_UPDATE

    def render(self,surface,camera):
        start = camera.rect.topleft
        end = camera.rect.bottomright

        # amount of tiles to render on x and y
        render_x = [start[0] // settings.TILE_SIZE[0], math.ceil(end[0] / settings.TILE_SIZE[0])]
        render_y = [start[1] // settings.TILE_SIZE[1], math.ceil(end[1] / settings.TILE_SIZE[1])]

        for y in range(max(0,render_y[0]), min(render_y[1], self.size_y)):
            for x in range(max(0,render_x[0]), min(render_x[1], self.size_x)):
                px = x * settings.TILE_SIZE[0] - start[0]
                py = y * settings.TILE_SIZE[1] - start[1]
                surface.blit(self.tileset[self.mapArr[y][x]], (px,py))

    def getCollidableTiles(self, rect):
        collidables = []
        start_pos = rect.topleft
        end_pos =  rect.bottomright
        render_x = [start_pos[0]//settings.TILE_SIZE[0], end_pos[0]//settings.TILE_SIZE[0]]
        render_y = [start_pos[1]//settings.TILE_SIZE[1], end_pos[1]//settings.TILE_SIZE[1]]

        for y in range(max(0,render_y[0] - 1), min(render_y[1] + 1,self.size_y)):
            for x in range(max(0,render_x[0] -  1), min(render_x[1] + 1,self.size_x)):
                if self.mapArr[y][x] in [Forest.WALL, Forest.WATER, Forest.EXIT]:
                    if self.mapArr[y][x] == Forest.EXIT:
                        obj = Forest.ExitObject(self.game, x, y)
                    else:
                        obj = Forest.WorldObject(x, y)

                    collidables.append(obj)

        return collidables

    def getWorldSize(self):
        return (self.size_x * settings.TILE_SIZE[0], self.size_y * settings.TILE_SIZE[1])

    def randomizeTile(self):
        if random.randrange(10) > 3:
            return Forest.WALL
        return Forest.WATER


    def carvePath(self, start, end):
        current = start
        while (current[0] != end[0]) or (current[1] != end[1]):
            angle = math.atan2((end[1] - current[1]),(end[0] - current[0]))
            new_x = current[0] + round(1 * math.cos(angle))
            new_y = current[1] + round(1 * math.sin(angle))
            self.mapArr[new_y][new_x] = Forest.GRASS
            self.mapArr[new_y][max(0, new_x-1)] = Forest.GRASS
            self.mapArr[new_y][min(new_x + 1, self.size_x)] = Forest.GRASS
            current = (new_x, new_y)


    def fillBorders(self, areas, targetState, newState):
        for wall in areas:


            for tile in self.getMetaTiles((wall[1],wall[0])):
                if self.mapArr[tile[1]][tile[0]] == targetState:
                    self.mapArr[tile[1]][tile[0]] = newState


    def getMetaTiles(self, position):
        return [(min(position[0] + 1, self.size_y - 1), max(0, position[1] - 1)),
                     (min(position[0] + 1, self.size_y - 1), position[1]),
                     (min(position[0] + 1, self.size_y - 1), min(position[1] + 1, self.size_x - 1)),
                     (position[0], max(0, position[1] - 1)),
                     (position[0], min(position[1] + 1, self.size_x - 1)),
                     (max(0, position[0] - 1), min(position[1] + 1, self.size_x - 1)),
                     (max(0, position[0] - 1), position[1]),
                     (max(0, position[0] - 1), max(0, position[1] - 1))
                     ]

    def spreadPoints(self, iterations):
        for iteration in range(5):

            regions = [[i] for i in self.checkpoints]

            for cell in [(x,y) for x in range(self.size_x) for y in range(self.size_y)]:

                nearestDistanceSquared = 100000

                for i in range(len(self.checkpoints)):
                    offset = (self.checkpoints[i][0] - cell[0]) ** 2 + (self.checkpoints[i][1] - cell[1]) ** 2
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

            self.checkpoints = new_checkpoint

    def createGeneration(self, live):
        self.generation += 1
        for y in range(self.size_y):
            for x in range(self.size_x):
                count = 0
                neighbours = [self.mapArr[max(0, y - 1)][x],self.mapArr[min(self.size_y - 1, y + 1)][x],
                 self.mapArr[y][max(0, x - 1)], self.mapArr[y][min(self.size_x - 1, x + 1)]]

                for cell in neighbours:
                    if cell == live:
                        count += 1

                self.mapArr[y][x] = self.cellRule(self.mapArr[y][x], count)

    def cellRule(self, current, count):
        live_cell = Forest.WATER
        dead_cell = Forest.WALL

        if current == live_cell and count < 1: return dead_cell
        elif current == live_cell and count in (2,3): return live_cell
        elif current == live_cell and count == 4: return live_cell
        elif current == dead_cell and count <= 1: return dead_cell
        elif current == dead_cell and count in (2,3): return random.choice([live_cell] + [dead_cell]*2)
        elif current == dead_cell and count == 4: return live_cell

        return dead_cell

    def getRooms(self):
        return self.roomList[1:]

    class WorldObject():

        type = 'wall'
        collidable = True

        def __init__(self, x, y):
            self.rect = pg.Rect((x * settings.TILE_SIZE[0], y * settings.TILE_SIZE[1]), settings.TILE_SIZE)

    class ExitObject(WorldObject):

        type = 'world'
        collidable = False

        def __init__(self, game, x, y):
            super().__init__(x, y)
            self.game = game

        def interact(self):
            self.game.generateLevel()

    class Room():
        def __init__(self,world,x,y,w,h):
            self.world = world
            self.x1 = x
            self.y1 = y
            self.x2 = x + w - 1
            self.y2 = y + h - 1
            self.w = w
            self.h = h

        def center(self):
            return ((self.x1 + self.x2)//2,(self.y1 + self.y2)//2)

        def getSpawnableSpace(self):
            mapData = self.world.mapArr
            spawnable = False
            x = 0
            y = 0
            while not spawnable:
                x = random.randrange(self.x1,self.x2)
                y = random.randrange(self.y1,self.y2)
                floor_tiles = (Dungeon.FLOOR, Dungeon.FLOOR_1)
                if mapData[y-1][x] in floor_tiles and mapData[y+1][x] in floor_tiles and mapData[y][x-1] in floor_tiles and mapData[y][x+1] in floor_tiles:
                    spawnable = True

            return [x * settings.TILE_SIZE[0],y * settings.TILE_SIZE[1]]

        def getSurroundingTiles(self, x, y):
            mapData = self.world.mapArr
            return (mapData[y - 1][x], mapData[y + 1][x], mapData[y][x - 1], mapData[y][x + 1])

        def getCorner(self):
            return (self.x1 * settings.TILE_SIZE[0], self.y1 * settings.TILE_SIZE[1])

        def getCornerTile(self):
            return random.choice([(self.x1,self.y1), (self.x2, self.y1), (self.x1, self.y2), (self.x2, self.y2)])

        def getCornerTiles(self):
            return [(self.x1,self.y1), (self.x2, self.y1), (self.x1, self.y2), (self.x2, self.y2)]
