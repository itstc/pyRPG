import pygame as pg

from world import World
from entity import mobs
from sprites import sprite


class Game:
    bg_color = pg.Color('black')
    def __init__(self, surface):

        self.surface = surface
        self.running = True
        self.map = World(self.surface,'res/test.tmx')
        self.entities = sprite.MobGroup()
        self.player = mobs.Player(256,512)
        self.entities.add(mobs.Goblin(256,128),mobs.Skeleton(512,128),self.player)

        self.camera = Camera(surface.get_size(), self.map.getWorldSize(), self.player)

        pg.key.set_repeat(1,1)

    def run(self):
        clock = pg.time.Clock()
        while self.running:
            dt = clock.tick(60)

            pg.display.set_caption('%s %i fps' % ('pyLota Alpha Build:', clock.get_fps()//1))

            self.render()
            self.handleEvent()
            self.update()

    def handleEvent(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running = False
                pg.quit()
                exit()
            elif event.type == pg.KEYDOWN:
                self.handleKeyEvent(event.key)

    def handleKeyEvent(self,key):
        moveSpeed = 8
        if key == pg.K_w:
            self.player.move(0,-moveSpeed)
        elif key == pg.K_a:
            self.player.move(-moveSpeed,0)
        elif key == pg.K_s:
            self.player.move(0,moveSpeed)
        elif key == pg.K_d:
            self.player.move(moveSpeed,0)

        self.camera.moveCamera()

    def update(self):
        self.entities.update(self.map)

        # Testing Mob Movement
        self.entities.sprites()[0].move(-1,0)

    def render(self):
        # Clear Screen
        self.surface.fill(Game.bg_color)

        # Draw components here
        self.map.render(self.camera)
        self.entities.draw(self.surface,self.camera)

        ppos = self.player.getPosition()
        self.camera.drawRectangle(self.surface,pg.Color('green'),pg.Rect(ppos[0] - 64, ppos[1] - 64, 128, 128))

        pg.display.update()

    def getCurrentMap(self):
        return self.map

    def loadMap(self,file):
        self.map = World(self.surface,file)


class Camera:
    def __init__(self, screenSize, worldSize, target):
        '''
        :param screenSize: tuple
        :param worldSize: tuple
        :param target: Game object for camera to follow
        '''
        self.windowSize = screenSize
        self.world = worldSize
        self.target = target

        self.offset = []
        self.moveCamera()

    def isVisible(self,position):
        """
        checks if a pygame.Rect() object is in the self.view
        :param rect: pygame.Rect()
        :return: bool
        """
        return (position[0] - self.offset[0] >= 0) and (position[1] - self.offset[1] >= 0)

    def getView(self):
        # returns the camera position
        return (int(self.offset[0]), int(self.offset[1]))

    def moveCamera(self):
        # moves the camera by x and y
        # -x,y are integers
        targetPos = self.target.getPosition()
        self.offset = [targetPos[0] - self.windowSize[0] // 2, targetPos[1] - self.windowSize[1] // 2]

        # Bounds of the World
        for coord in range(2):
            if self.offset[coord] < 0:
                self.offset[coord] = 0
            elif self.offset[coord] > self.world[coord] - self.windowSize[coord]:
                self.offset[coord] = self.world[coord] - self.windowSize[coord]

    def drawRectangle(self,surface,color,rect):
        orect = pg.Rect((rect.topleft[0] - self.offset[0], rect.topleft[1] - self.offset[1]),rect.size)
        pg.draw.rect(surface,color,orect,1)
