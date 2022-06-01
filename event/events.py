import pygame as pg

from util.util import Polygon

class EventListener:

    def __init__(self,game):
        self.game = game
        self.pressed = False
        self.lastMousePosition = [0,0]

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
            #'up': Polygon([(0, 0), playerPos, (self.game.windowSize[0], 0)]),
            'left': Polygon([(0, 0), (playerPos[0],0),
                             (playerPos[0], self.game.windowSize[1]),(0, self.game.windowSize[1])]),
            #'down': Polygon([(0, self.game.windowSize[1]), playerPos, self.game.windowSize]),
            'right': Polygon([(self.game.windowSize[0], 0), (playerPos[0],0),
                              (playerPos[0],self.game.windowSize[1]),self.game.windowSize])
        }

        for key in polygons.keys():
            if polygons[key].collide(pos):
                return key

        return self.game.player.action.direction

    def handleEvents(self,event):
        if event.type == pg.MOUSEBUTTONDOWN:
            if self.game.gui.showing and self.game.gui.rect.collidepoint(event.pos):
                self.game.gui.active = True
            else:
                self.game.gui.active = False
                if not self.game.player.action['attack']:
                    self.game.player.addActivity('ATTACK')

        elif event.type == pg.MOUSEMOTION:
            self.game.player.action.direction = self.getMouseDirection(event.pos)
            self.lastMousePosition = event.pos

        elif event.type == pg.KEYDOWN:
            self.handleKeyDown(event.key, self.lastMousePosition)
            self.pressed = True
        elif event.type == pg.KEYUP:
            self.handleKeyUp(event.key, self.lastMousePosition)
            self.pressed = False
            self.game.player.action['walk'] = False

    def handleKeyDown(self, key, pos):
        # Handle which key is pressed

        if self.game.gui.type != 'main_ui' and self.game.gui.showing and not self.pressed:
            self.game.gui.toggle()

        if key == pg.K_w:
            self.game.player.action.moveDirections['up'] = True
        if key == pg.K_a:
            self.game.player.action.moveDirections['left'] = True
        if key == pg.K_s:
            self.game.player.action.moveDirections['down'] = True
        if key == pg.K_d:
            self.game.player.action.moveDirections['right'] = True

        # Key Handling related to Game
        if not self.pressed:
            if key == pg.K_q:
                self.game.gui = self.game.ui_manager['stats']
                self.game.gui.toggle()
            if key == pg.K_i:
                self.game.gui = self.game.ui_manager['inventory']
                self.game.gui.toggle()
            if key == pg.K_e:
                if self.game.player.interactable:
                    self.game.player.interactable[0].interact()
            if key == pg.K_SPACE:
                self.game.generateLevel()
            if key == pg.K_TAB:
                self.game.gui = self.game.ui_manager['minimap']
                self.game.gui.toggle()
            if key == pg.K_ESCAPE:
                if self.game.gui.showing:
                    self.game.gui.toggle()
            if key == pg.K_1 and not self.game.player.action['attack']:
                self.game.player.addActivity('FIRE', pos)


    def handleKeyUp(self, key, pos):

        if key == pg.K_w:
            self.game.player.action.moveDirections['up'] = False
        if key == pg.K_a:
            self.game.player.action.moveDirections['left'] = False
        if key == pg.K_s:
            self.game.player.action.moveDirections['down'] = False
        if key == pg.K_d:
            self.game.player.action.moveDirections['right'] = False

    def clear(self):
        for direction in ['up','left','down','right']:
            self.game.player.action.moveDirections[direction] = False
