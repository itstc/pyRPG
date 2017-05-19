import pygame
from game import Game

if __name__ == '__main__':
    SIZE = (1280,720)
    pygame.init()
    screen = pygame.display.set_mode(SIZE)
    pygame.display.set_caption('LOTA ALPHA')
    g = Game(screen)
    g.run()
