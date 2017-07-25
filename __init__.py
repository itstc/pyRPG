import pygame,cProfile
from game.settings import WINDOW_SIZE
from game.game import Game

if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode(WINDOW_SIZE, pygame.DOUBLEBUF)
    pygame.display.set_caption('LOTA ALPHA')
    g = Game(screen)
    cProfile.run('g.run()')
