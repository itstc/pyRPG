import pygame
from map.World import World,Camera
from mob.player import Player

class Game:

    bg_color = pygame.Color('black')

    def __init__(self, surface):
        self.surface = surface
        self.running = True
        self.camera = Camera()
        self.entities = pygame.sprite.Group()
        self.player = Player(self.surface,[64,128])
        self.map = World(self.surface,'res/test.tmx')
        pygame.key.set_repeat(1,1)

    def run(self):
        clock = pygame.time.Clock()
        while self.running:
            dt = clock.tick(60)

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
        pass

    def render(self):
        self.surface.fill(Game.bg_color)

        self.map.render(self.camera)
        self.player.render(self.camera)

        pygame.display.update()

    def getCurrentMap(self):
        return self.map

    def loadMap(self,file):
        self.map = World(self.surface,file)
