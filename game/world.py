#TODO: convert tmx file to world object

import pygame as pg
import math
from pytmx.util_pygame import load_pygame

class World:
    size = [64,64]
    def __init__(self,surface,file):
        self.surface = surface
        self.mapData = load_pygame(file)
        self.scale = pg.transform.scale

    def render(self,camera):
        # Gets the tiles based on camera location and blits to game.surface
        offset = camera.getView()
        renderDistance = [self.surface.get_width() + 32,self.surface.get_height() + 32]
        for y in range(offset[1]//World.size[1] ,math.ceil((offset[1] + renderDistance[1]) / World.size[1])):
            for x in range(offset[0]//World.size[0], math.ceil((offset[0] + renderDistance[0]) / World.size[0])):
                try:
                    image = self.mapData.get_tile_image(x,y,0)
                    image = self.scale(image,World.size)

                except:
                    continue
                px = x * World.size[0]  - offset[0]
                py = y * World.size[1] - offset[1]
                self.surface.blit(image,(px,py))


    def getCollidableTiles(self, rect):
        collidables = []
        start = rect.topleft
        end = rect.bottomright
        for y in range(start[1] // World.size[1], end[1] // World.size[1] + 1):
            for x in range(start[0] // World.size[0], end[0] // World.size[0] + 1):
                try:
                    tile = self.mapData.get_tile_properties(x,y,0)
                    if tile['Wall'] == 'true':
                        collidables.append(pg.Rect((x * World.size[0], y * World.size[1]),World.size))
                except:
                    continue
        return collidables

    def getData(self):
        return self.mapData

    def getWorldSize(self):
        return (self.mapData.width * World.size[0], self.mapData.height * World.size[1])

