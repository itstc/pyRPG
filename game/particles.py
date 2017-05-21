import pygame as pg
import ui

class BouncyText(ui.StringRenderer):
    critical = pg.Color(236,208,120)

    def __init__(self, host, value, position, size = 24, state = pg.Color(192,41,66), back = pg.Color(84,36,55)):
        super().__init__(size)
        self.host = host
        self.value = value
        self.position = list(position)
        self.position[0] -= self.getStringSize(value)[0] // 2

        self.fg = state
        self.bg = back

        self.alive = True
        self.lifeTime = 500

    def update(self,dt):
        if self.alive:
            self.lifeTime -= dt
            if self.lifeTime <= 0:
                self.alive = False

            self.position[1] -= 0.1*dt
        else:
            self.host.statQueue.remove(self)

    def draw(self,surface,camera):
        offset = camera.getView()
        ox = self.position[0] + 3
        if self.alive:
            self.drawString(surface, self.value, (ox - offset[0],self.position[1] - offset[1]), self.bg)
            self.drawString(surface,self.value,(self.position[0]- offset[0],self.position[1]- offset[1]),self.fg)







