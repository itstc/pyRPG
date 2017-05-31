import pygame,cProfile
import settings
from game import Game

if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode(settings.WINDOW_SIZE)
    pygame.display.set_caption('LOTA ALPHA')
    g = Game(screen)
    cProfile.run('g.run()')
