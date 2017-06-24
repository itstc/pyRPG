import pygame, os, random, math

class Spritesheet:
    def __init__(self,path):
        self.image = pygame.image.load(os.path.join(path)).convert_alpha()
        self.width = self.image.get_width()
        self.height = self.image.get_height()

    def getSprite(self,size,start):
        '''

        :param size: int (Size to cut out)
        :param startX: int (Starting X)
        :param startY: int (Starting Y)
        :return: pygame.Surface (The image on spritesheet)

        '''
        x = start[0] * size[0]
        y = start[1] * size[1]
        sheetArray = pygame.PixelArray(self.image)
        return sheetArray[x:x + size[0],y:y + size[1]].make_surface()

class StringRenderer():

    def drawString(self, surface, string, position, size = 16,color = pygame.Color(224,228,204)):
        text = pygame.font.Font('../game/res/gamefont.ttf', size).render(str(string),1,color)
        surface.blit(text,position)

    def getStringSize(self,string,size=16):
        return pygame.font.Font('../game/res/gamefont.ttf', size).size(str(string))

class Game(StringRenderer):

    TILE_SIZE = (16,16)

    def __init__(self, screen):
        self.pressed = False
        self.running = True
        self.screen = screen

        sheet = Spritesheet('../game/res/tilesheet.png')
        self.tileset = {
            0: pygame.transform.scale(sheet.getSprite((16, 16), (0, 0)), Game.TILE_SIZE),
            1: pygame.transform.scale(sheet.getSprite((16, 16), (1, 0)), Game.TILE_SIZE),
            2: pygame.transform.scale(sheet.getSprite((16, 16), (0, 3)), Game.TILE_SIZE),
            3: pygame.transform.scale(sheet.getSprite((16, 16), (5, 0)), Game.TILE_SIZE),
            4: pygame.transform.scale(sheet.getSprite((16, 16), (1, 1)), Game.TILE_SIZE)
        }

        self.map = Forest()

    def run(self):
        clock = pygame.time.Clock()
        prev = 1
        while self.running:
            time = clock.tick(128)
            dt = time // prev

            self.handleEvent()
            self.update(dt)
            self.render()

            prev = time

    def handleEvent(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                pygame.quit()
                exit()

            elif event.type == pygame.KEYDOWN and not self.pressed:
                self.pressed = True
                if event.key == pygame.K_SPACE:
                    self.map = Forest()

            elif event.type == pygame.KEYUP:
                self.pressed = False

    def update(self, dt):
        pass

    def render(self):
        for y in range(self.map.size_y):
            for x in range(self.map.size_x):
                self.screen.blit(self.tileset[self.map.mapArr[y][x]], (x * Game.TILE_SIZE[0], y * Game.TILE_SIZE[1]))

        for room in self.map.roomList:
            pygame.draw.rect(self.screen, pygame.Color('red'), pygame.Rect(room.x1 * Game.TILE_SIZE[0],
                                                                           room.y1 * Game.TILE_SIZE[1],
                                                                           room.w * Game.TILE_SIZE[0],
                                                                           room.h * Game.TILE_SIZE[1]), 1)

        pygame.display.update()

class World:

    GRASS = 0
    WATER = 1
    WALL = 2
    EXIT = 3
    FLOOD_WATER = 4

    def __init__(self, width, height):

        self.size_x = width
        self.size_y = height

        self.mapArr = []
        self.roomList = []


    def setTile(self, x, y, tile):
        self.mapArr[y][x] = tile

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


class Forest(World):

    def __init__(self):
        super().__init__(32, 32)

        self.mapArr = [[self.randomizeTiles(45, Forest.WALL, Forest.WATER) for x in range(self.size_x)] for y in range(self.size_y)]

        for i in range(10):
            self.cellGeneration(Forest.WALL, Forest.WATER)

        checkpoints = [(random.randrange(self.size_x), random.randrange(self.size_y)) for i in range(5)]

        for i in range(3):
            checkpoints = self.spreadPoints(checkpoints)

        for i in range(len(checkpoints)):
            self.drawCircle(checkpoints[i][0], checkpoints[i][1], 2, Forest.GRASS)
            self.carvePath(checkpoints[i], checkpoints[min(i + 1, len(checkpoints) - 1)], Forest.GRASS)

        wall = [(x, y) for x in range(self.size_x) for y in range(self.size_y) if self.mapArr[y][x] == Forest.WATER]

        for point in wall:
            self.borderFill(point, Forest.GRASS, Forest.WALL)

        for i in range(5):
            self.cellGeneration(Forest.WALL, Forest.WATER)







if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode((512, 512))
    pygame.display.set_caption('Map Generator')

    g = Game(screen)
    g.run()