import pygame as pg
from ui.ui import StringRenderer

class BouncyText(StringRenderer):
    def __init__(self, host, value, position, scale = 2, state = pg.Color(192,41,66), back = pg.Color(84,36,55)):
        super().__init__()
        self.scale = scale
        self.host = host
        self.value = value
        self.position = list(position)
        self.position[0] -= self.getStringSize(value, scale)[0] // 2

        self.fg = state
        self.bg = back

        self.alive = True
        self.lifeTime = 30

    def update(self,dt):
        if self.alive:
            self.lifeTime -= dt
            if self.lifeTime <= 0:
                self.alive = False

            self.position[1] -= 1.5 * dt**2
        else:
            self.host.statQueue.remove(self)

    def draw(self,surface,camera):
        ox = self.position[0] + 3
        if self.alive:
            self.drawString(surface,self.value,camera.applyOnPosition([ox,self.position[1]]),1 * self.scale,self.bg)
            self.drawString(surface,self.value,camera.applyOnPosition([self.position[0],self.position[1]]),1 * self.scale,self.fg)


class FadingText(StringRenderer):
    def __init__(self, string, position, scale = 1, time = 1500, fg = pg.Color(250,250,250), bg = pg.Color(32,32,32)):
        super().__init__()
        self.time = time
        self.string_size = self.getStringSize(string, scale)
        self.bg_display = self.getStringAsSurface(string, scale, bg)
        self.fg_display = self.getStringAsSurface(string, scale, fg)
        self.size = self.bg_display.get_size()
        self.pos = (position[0] - self.size[0] // 2, position[1] - self.size[1] // 2)

    def update(self,dt):
        self.time -= dt

    def render(self, surface):
        surface.blit(self.bg_display,self.pos)
        surface.blit(self.fg_display, (self.pos[0], self.pos[1] - 2))

class CritText(BouncyText):
    def __init__(self, host, value, position, scale = 3, state = pg.Color('yellow'), back = pg.Color(84,36,55)):
        super().__init__(host, value, position, scale, state, back)
        self.scale = scale
        self.host = host
        self.value = value
        self.position = list(position)
        self.position[0] -= self.getStringSize(value, scale)[0] // 2

        self.fg = state
        self.bg = back

        self.alive = True
        self.lifeTime = 30

    def update(self,dt):
        if self.alive:
            self.lifeTime -= dt
            if self.lifeTime <= 0:
                self.alive = False

            self.position[1] -= 1.5 * dt**2
        else:
            self.host.statQueue.remove(self)

    def draw(self,surface,camera):
        ox = self.position[0] + 3
        if self.alive:
            self.drawString(surface,self.value,camera.applyOnPosition([ox,self.position[1]]),1 * self.scale,self.bg)
            self.drawString(surface,self.value,camera.applyOnPosition([self.position[0],self.position[1]]),1 * self.scale,self.fg)
