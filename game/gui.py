import pygame as pg

class GUI:
    black = pg.Color(0,0,0,200)
    def __init__(self,size,pos = [0,0]):
        self.showing = False
        self.active = True
        self.surface = pg.Surface.convert_alpha(pg.Surface(size))
        self.rect = pg.Rect(pos,size)
        self.surface.fill(GUI.black,self.rect)


    def update(self):
        pass

    def draw(self,surface):
        if self.showing:
            surface.blit(self.surface,self.rect.topleft)