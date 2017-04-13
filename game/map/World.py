#TODO: convert tmx file to world object

import pygame
from pytmx.util_pygame import load_pygame

class World:
    size = [32,32]
    def __init__(self,surface,file):
        self.surface = surface
        self.mapData = load_pygame(file)

        self.screenSize = [self.surface.get_width() // World.size[0],self.surface.get_height() // World.size[1]]
        self.camera = [0,0]


    def render(self):
        # Gets the tiles based on camera location and blits to game.surface
        xRange = (self.camera[0],self.camera[0] + self.screenSize[0] + 1)
        yRange = (self.camera[1],self.camera[1] + self.screenSize[1] + 1)

        for y in range(yRange[0],yRange[1]):
            for x in range(xRange[0],xRange[1]):
                try:
                    image = self.mapData.get_tile_image(x,y,0)
                    image = pygame.transform.scale(image,World.size)
                except:
                    break
                drawX = (x - self.camera[0])
                drawY = (y - self.camera[1])
                self.surface.blit(image, (drawX * World.size[0],drawY * World.size[1]))


    def getCamera(self):
        # returns the camera position
        return self.camera

    def moveCamera(self,x=0,y=0):
        # moves the camera by x and y
        # -x,y are integers

        self.camera = [(self.camera[0] + x),(self.camera[1] + y)]

        if self.camera[0] >= self.mapData.width - self.screenSize[0] + 1:
            self.camera[0] = self.mapData.width - self.screenSize[0]
        elif self.camera[0] <= 0:
            self.camera[0] = 0

        if self.camera[1] >= self.mapData.height - self.screenSize[1]:
            self.camera[1] = self.mapData.height - self.screenSize[1]
        elif self.camera[1] <= 0:
            self.camera[1] = 0