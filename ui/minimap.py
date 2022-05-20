import pygame as pg
from ui.ui import GUI
from level.world import World
from game.tile import TILE_COLOR_MAP
from game.settings import TILE_SIZE

class MinimapGUI(GUI):

    TILE_SIZE = 6

    type = 'main_ui'

    def __init__(self, surface, worldMap, player, pos):
        super().__init__(surface, [256,256], pos)

        self.interface = pg.Surface([256,256])
        self.interface.set_alpha(200)

        self.worldMap = worldMap
        self.player = player
        self.showing = True
        self.active = True

    def drawFeatures(self):
        mapArr = self.worldMap.getMap()
        playerPos = [self.player.position[i] // TILE_SIZE[i] for i in range(2)]
        for row in range(len(mapArr)):
            for col in range(len(mapArr[row])):
                tile = pg.Surface([MinimapGUI.TILE_SIZE, MinimapGUI.TILE_SIZE])
                tile.fill(TILE_COLOR_MAP[mapArr[row][col]])
                self.interface.blit(tile, [col * MinimapGUI.TILE_SIZE, row * MinimapGUI.TILE_SIZE])
        player = pg.Surface([MinimapGUI.TILE_SIZE, MinimapGUI.TILE_SIZE])
        player.fill(pg.Color('red'))
        self.interface.blit(player, [playerPos[0] * MinimapGUI.TILE_SIZE, playerPos[1] * MinimapGUI.TILE_SIZE])
        
