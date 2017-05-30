import pygame as pg
from util import Polygon

class EventListener:

    def __init__(self,game):
        self.game = game
        self.pressed = False

    def handleEvent(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.game.running = False
                pg.quit()
                exit()
            elif self.game.gui.active:
                self.game.gui.handleEvents(event)

            self.handleEvents(event)



    def getMouseDirection(self, pos):
        playerPos = self.game.camera.applyOnPosition(self.game.player.rect.center)
        polygons = {
            # 0:top, 1:left, 2:down, 3:right
            'up': Polygon([(0, 0), playerPos, (self.game.windowSize[0], 0)]),
            'left': Polygon([(0, 0), playerPos, (0, self.game.windowSize[1])]),
            'down': Polygon([(0, self.game.windowSize[1]), playerPos, self.game.windowSize]),
            'right': Polygon([(self.game.windowSize[0], 0), playerPos, self.game.windowSize])
        }

        for key in polygons.keys():
            if polygons[key].collide(pos):
                return key

    def handleEvents(self,event):
        if event.type == pg.MOUSEBUTTONDOWN:
            if self.game.gui.showing and self.game.gui.rect.collidepoint(event.pos):
                self.game.gui.active = True
            else:
                self.game.gui.active = False
                self.game.player.action.direction = self.getMouseDirection(event.pos)
                if not self.game.player.action['attack']:
                    self.game.player.attack()
        elif event.type == pg.KEYDOWN:
            self.handleKeyEvent(event.key)
            self.pressed = True
        elif event.type == pg.KEYUP:
            self.pressed = False
            self.game.player.action['walk'] = False

    def handleKeyEvent(self, key):
        # Handle which key is pressed
        if key in [pg.K_w, pg.K_a, pg.K_s, pg.K_d]:
            self.game.player.action['walk'] = True
        if key == pg.K_w:
            self.game.player.action.direction = 'up'
            self.game.player.action.move(0, -self.game.player.stats.movement_speed)
        elif key == pg.K_a:
            self.game.player.action.direction = 'left'
            self.game.player.action.move(-self.game.player.stats.movement_speed, 0)
        elif key == pg.K_s:
            self.game.player.action.direction = 'down'
            self.game.player.action.move(0, self.game.player.stats.movement_speed)
        elif key == pg.K_d:
            self.game.player.action.direction = 'right'
            self.game.player.action.move(self.game.player.stats.movement_speed, 0)
        # Key Handling related to Game
        elif key == pg.K_i and not self.pressed:
            self.game.gui.toggle()
        elif key == pg.K_ESCAPE and not self.pressed:
            self.game.running = False