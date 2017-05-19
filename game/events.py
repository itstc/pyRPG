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
            elif event.type == pg.MOUSEBUTTONDOWN:
                self.handleMouseEvent(event.pos)
            elif event.type == pg.MOUSEMOTION:
                self.handleMouseMovement(event.pos,event.buttons)
            elif event.type == pg.KEYDOWN:
                self.handleKeyEvent(event.key)
                self.pressed = True
            elif event.type == pg.KEYUP:
                self.pressed = False
                self.game.player.isWalking = False

    def handleMouseMovement(self, pos, buttons):
        if self.game.gui.active:
            if 1 in buttons:
                self.game.gui.rect.centerx = pos[0]
                self.game.gui.rect.top = pos[1]
            else:
                self.game.gui.isHoveringSlot(pos)



    def handleMouseEvent(self, pos):
        # GUI handling
        if self.game.gui.showing and self.game.gui.rect.collidepoint(pos):
            self.game.gui.active = True

        self.game.player.direction = self.getMouseDirection(pos)
        if not self.game.player.attacking:
            self.game.player.attack()

    def getMouseDirection(self, pos):
        playerPos = self.game.camera.getOffsetPosition(self.game.player.rect)
        polygons = {
            # 0:top, 1:left, 2:down, 3:right
            0: Polygon([(0, 0), playerPos, (self.game.windowSize[0], 0)]),
            1: Polygon([(0, 0), playerPos, (0, self.game.windowSize[1])]),
            2: Polygon([(0, self.game.windowSize[1]), playerPos, self.game.windowSize]),
            3: Polygon([(self.game.windowSize[0], 0), playerPos, self.game.windowSize])
        }

        for key in polygons.keys():
            if polygons[key].collide(pos):
                return key

    def handleKeyEvent(self, key):
        if key in [pg.K_w,pg.K_a,pg.K_s,pg.K_d]:
            self.game.player.isWalking = True
        moveSpeed = 4
        if key == pg.K_w:
            self.game.player.direction = 0
            self.game.player.move(0, -moveSpeed)
        elif key == pg.K_a:
            self.game.player.direction = 1
            self.game.player.move(-moveSpeed, 0)
        elif key == pg.K_s:
            self.game.player.direction = 2
            self.game.player.move(0, moveSpeed)
        elif key == pg.K_d:
            self.game.player.direction = 3
            self.game.player.move(moveSpeed, 0)
        # The button below are toggles hence using boolean pressed
        elif key == pg.K_e and not self.pressed:
            self.game.player.inventory.useItem(0)
        elif key == pg.K_i and not self.pressed:
            self.game.gui.showing = not self.game.gui.showing
            self.game.gui.hide()

        self.game.camera.moveCamera()