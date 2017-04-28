#TODO: convert tmx file to world object

import pygame
import math
from pytmx.util_pygame import load_pygame

class World:
    size = [64,64]
    def __init__(self,surface,file):
        self.surface = surface
        self.mapData = load_pygame(file)
        self.scale = pygame.transform.scale

    def render(self,camera):
        # Gets the tiles based on camera location and blits to game.surface
        offset = camera.getView()
        for y in range(math.ceil((offset[1] + self.surface.get_height() + 64) / World.size[1])):
            for x in range(math.ceil((offset[0] + self.surface.get_width() + 64) / World.size[0])):
                try:
                    image = self.mapData.get_tile_image(x,y,0)
                    image = self.scale(image,World.size)
                except:
                    continue
                px = x * World.size[0]  - offset[0]
                py = y * World.size[1] - offset[1]
                self.surface.blit(image,(px,py))

    def getMap(self):
        return self.mapData

class Camera:

    def __init__(self):
        self.offset = [128,128]

    def isVisible(self,position):
        """
        checks if a pygame.Rect() object is in the self.view
        :param rect: pygame.Rect()
        :return: bool
        """
        return (abs(position[0] - self.offset[0]) >= 0 and abs(position[1] - self.offset[1]) >= 0)

    def getView(self):
        # returns the camera position
        return (int(self.offset[0]), int(self.offset[1]))

    def moveCamera(self,x=0,y=0):
        # moves the camera by x and y
        # -x,y are integers
        self.offset = [self.offset[0] + x, self.offset[1] + y]