import pygame
from Game import Game

def create_window():
    SIZE = (1280,720)
    pygame.init()
    screen = pygame.display.set_mode(SIZE)
    pygame.display.set_caption('LOTA ALPHA')

    return screen

def main():
    screen = create_window()
    game = Game(screen)

    game.run()


main()