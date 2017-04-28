import pygame
from Game import Game

def create_window():
    SIZE = (900,600)
    pygame.init()
    screen = pygame.display.set_mode(SIZE)
    pygame.display.set_caption('LOTA ALPHA')

    return screen

def main():
    screen = create_window()
    game = Game(screen)

    game.run()


main()