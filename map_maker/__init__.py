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
            3: pygame.transform.scale(sheet.getSprite((16, 16), (5, 0)), Game.TILE_SIZE)
        }

        self.map = Map()
        self.map.generateMap(32,32)

    def run(self):
        clock = pygame.time.Clock()
        prev = 1
        while self.running:
            time = clock.tick(128)
            dt = (time / prev)

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
                    self.map.generateMap(32,32)

            elif event.type == pygame.KEYUP:
                self.pressed = False

    def update(self, dt):
        self.map.update(dt)

    def render(self):
        for y in range(self.map.size_y):
            for x in range(self.map.size_x):
                self.screen.blit(self.tileset[self.map.mapArr[y][x]], (x * Game.TILE_SIZE[0], y * Game.TILE_SIZE[1]))

        self.drawString(self.screen, 'Generation: %i' % self.map.generation, (0,0), 32)

        for points in self.map.checkpoints:
            pygame.draw.rect(self.screen, pygame.Color('green'), pygame.Rect(tuple(map(lambda i: i * Game.TILE_SIZE[0], points)),Game.TILE_SIZE))

        pygame.display.update()


class Map():

    TIME_PER_UPDATE = 60
    GRASS = 0
    WATER = 1
    WALL = 2
    EXIT = 3

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
            self.createGeneration()

        # Create checkpoints and connect them with Lloyd's Algorithm
        self.checkpoints = []

        for i in range(3):
            self.checkpoints.append((random.randrange(0, self.size_x), random.randrange(0, self.size_y)))

        self.spreadPoints(3)

        for i in range(len(self.checkpoints)):
            self.mapArr[self.checkpoints[i][1]][self.checkpoints[i][0]] = Map.GRASS
            for tile in self.getMetaTiles(self.checkpoints[i]):
                self.mapArr[tile[1]][tile[0]] = Map.GRASS

            maxIndex = min(i + 1, len(self.checkpoints) - 1)
            self.carvePath(self.checkpoints[i],self.checkpoints[maxIndex])

        for points in self.checkpoints:
            room = Map.Room(points[0], points[1], 3 + random.randrange(2), 3 + random.randrange(2))
            self.roomList.append(room)

            for y in range(room.y1, room.y2):
                for x in range(room.x1, room.x2):
                    self.mapArr[y][x] = Map.GRASS

        rp = self.roomList[-1].center()
        self.mapArr[rp[1]][rp[0]] = Map.EXIT

    def update(self, dt):
        self.time -= dt

        if self.time <= 0:
            self.time = Map.TIME_PER_UPDATE

    def randomizeTile(self):
        if random.randrange(10) > 3:
            return Map.WALL
        return Map.WATER


    def carvePath(self, start, end):
        current = start
        while (current[0] != end[0]) or (current[1] != end[1]):
            angle = math.atan2((end[1] - current[1]),(end[0] - current[0]))
            new_x = current[0] + round(1 * math.cos(angle))
            new_y = current[1] + round(1 * math.sin(angle))
            self.mapArr[new_y][new_x] = Map.GRASS
            self.mapArr[new_y][max(0, new_x-1)] = Map.GRASS
            self.mapArr[new_y][min(new_x + 1, self.size_x)] = Map.GRASS
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

    def createGeneration(self):
        self.generation += 1
        for y in range(self.size_y):
            for x in range(self.size_x):
                n = self.countRule(self.mapArr[max(0, y - 1)][x])
                s = self.countRule(self.mapArr[min(self.size_y - 1, y + 1)][x])
                w = self.countRule(self.mapArr[y][max(0, x - 1)])
                e = self.countRule(self.mapArr[y][min(self.size_x - 1, x + 1)])

                count = n + s + w + e

                self.mapArr[y][x] = self.cellRule(self.mapArr[y][x], count)

    def countRule(self, id):
        if id == 1:
            return 1
        return 0

    def cellRule(self, current, count):
        live_cell = 1
        dead_cell = 2

        if current == live_cell and count < 1: return dead_cell
        elif current == live_cell and count in (2,3): return live_cell
        elif current == live_cell and count == 4: return live_cell
        elif current == dead_cell and count <= 1: return dead_cell
        elif current == dead_cell and count in (2,3): return random.choice([live_cell] + [dead_cell]*2)
        elif current == dead_cell and count == 4: return live_cell

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

if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode((1024, 1024))
    pygame.display.set_caption('Map Generator')

    g = Game(screen)
    g.run()