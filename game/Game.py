import pygame
from map import World

class Game:

    bg_color = pygame.Color('black')

    def __init__(self, surface):
        self.surface = surface
        self.running = True
        self.spriteList = pygame.sprite.Group()
        self.map = World.World(self.surface,'res/test.tmx')
        pygame.key.set_repeat(20,20)

    def run(self):
        clock = pygame.time.Clock()

        while self.running:

            self.render()
            clock.tick(60)
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
        if key == pygame.K_w:
            self.map.moveCamera(0,-1)
        elif key == pygame.K_a:
            self.map.moveCamera(-1,0)
        elif key == pygame.K_s:
            self.map.moveCamera(0,1)
        elif key == pygame.K_d:
            self.map.moveCamera(1,0)

    def update(self):
        pass

    def render(self):
        self.surface.fill(Game.bg_color)
        self.map.render()
        pygame.display.update()
