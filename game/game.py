import pygame

from world import World
from entity import mobs
from sprites import sprite


class Game:
    bg_color = pygame.Color('black')
    def __init__(self, surface):

        self.surface = surface
        self.running = True
        self.entities = sprite.MobGroup()
        self.entities.add(mobs.Player(128,256),mobs.Goblin(32,32),mobs.Skeleton(512,128))
        self.map = World(self.surface,'res/test.tmx')

        self.camera = Camera()

        pygame.key.set_repeat(1,1)

    def run(self):
        clock = pygame.time.Clock()
        while self.running:
            dt = clock.tick(60)

            pygame.display.set_caption('Game state: ' + str(clock.get_fps()//1))

            self.render()
            self.handleEvent()
            self.update()

    def handleEvent(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                self.handleKeyEvent(event.key)

    def handleKeyEvent(self,key):
        moveSpeed = 8
        if key == pygame.K_w:
            self.camera.moveCamera(0,-moveSpeed)
        elif key == pygame.K_a:
            self.camera.moveCamera(-moveSpeed,0)
        elif key == pygame.K_s:
            self.camera.moveCamera(0,moveSpeed)
        elif key == pygame.K_d:
            self.camera.moveCamera(moveSpeed,0)

    def update(self):
        self.entities.update(self.camera)

    def render(self):
        self.surface.fill(Game.bg_color)

        self.map.render(self.camera)
        self.entities.draw(self.surface)

        pygame.display.update()

    def getCurrentMap(self):
        return self.map

    def loadMap(self,file):
        self.map = world.World(self.surface,file)


class Camera:

    def __init__(self, position = (0,0)):
        self.offset = position

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

    def moveCamera(self,x=0,y=0):
        # moves the camera by x and y
        # -x,y are integers
        self.offset = [self.offset[0] + x, self.offset[1] + y]