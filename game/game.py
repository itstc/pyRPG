import pygame

from world import World
from entity import mobs
from sprites import sprite


class Game:
    bg_color = pygame.Color('black')
    def __init__(self, surface):

        self.surface = surface
        self.running = True
        self.player = mobs.Player(512,512)
        self.entities = sprite.MobGroup()
<<<<<<< HEAD
        self.player = mobs.Player(256,512)
        self.entities.add(self.player,mobs.Goblin(32,32),mobs.Skeleton(512,128))
        self.map = World(self.surface,'res/test.tmx')

        self.camera = Camera(surface.get_size(), self.map.getWorldSize(), self.player)
=======
        self.entities.add(self.player,mobs.Goblin(32,32),mobs.Skeleton(512,128))
        self.map = World(self.surface,'res/test.tmx')

        self.camera = Camera(self.map, self.player)
>>>>>>> d0a22a98c2fa60cbb45df88b208dc6e8f1fbd90b

        pygame.key.set_repeat(1,1)

    def run(self):
        clock = pygame.time.Clock()
        while self.running:
            dt = clock.tick(60)

            pygame.display.set_caption('%s %i fps' % ('pyLota Alpha Build:', clock.get_fps()//1))

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
<<<<<<< HEAD
            self.player.move(0,-moveSpeed)
        elif key == pygame.K_a:
            self.player.move(-moveSpeed,0)
        elif key == pygame.K_s:
            self.player.move(0,moveSpeed)
=======
            self.player.move(0, -moveSpeed)
        elif key == pygame.K_a:
            self.player.move(-moveSpeed,0)
        elif key == pygame.K_s:
            self.player.move(0, moveSpeed)
>>>>>>> d0a22a98c2fa60cbb45df88b208dc6e8f1fbd90b
        elif key == pygame.K_d:
            self.player.move(moveSpeed,0)

        self.camera.moveCamera()

    def update(self):
        pass

    def render(self):
        # Clear Screen
        self.surface.fill(Game.bg_color)

        # Draw components here
        self.map.render(self.camera)
        self.entities.draw(self.surface,self.camera.getView())

        pygame.display.update()

    def getCurrentMap(self):
        return self.map

<<<<<<< HEAD
    def loadNewMap(self,file):
=======
    def loadMap(self,file):
>>>>>>> d0a22a98c2fa60cbb45df88b208dc6e8f1fbd90b
        self.map = World(self.surface,file)


class Camera:

<<<<<<< HEAD
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
=======
    def __init__(self, world, player):
        self.player = player
        self.currentWorld = world
        self.worldSize = world.getMapSize()
        self.windowSize = [900,600]

        spawnPos = player.getPosition()
        self.offset = (spawnPos[0] - self.windowSize[0] // 2,spawnPos[1] - self.windowSize[1] // 2)
>>>>>>> d0a22a98c2fa60cbb45df88b208dc6e8f1fbd90b

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
<<<<<<< HEAD
        targetPos = self.target.getPosition()
        self.offset = [targetPos[0] - self.windowSize[0] // 2, targetPos[1] - self.windowSize[1] // 2]

        # Bounds of the World
        for coord in range(2):
            if self.offset[coord] < 0:
                self.offset[coord] = 0
            elif self.offset[coord] > self.world[coord] - self.windowSize[coord]:
                self.offset[coord] = self.world[coord] - self.windowSize[coord]
=======
        pPos = self.player.getPosition()
        self.offset = [pPos[0]  - self.windowSize[0] // 2, pPos[1]  - self.windowSize[1] // 2]

        # World Bounds
        for coord in range(2):
            if self.offset[coord] < 0:
                self.offset[coord] = 0
            elif self.offset[coord] > self.worldSize[coord] - self.windowSize[coord]:
                self.offset[coord] = self.worldSize[coord] - self.windowSize[coord]
>>>>>>> d0a22a98c2fa60cbb45df88b208dc6e8f1fbd90b
