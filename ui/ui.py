import pygame as pg
from sprite.sprite import AlphaSpritesheet, Spritesheet

class StringRenderer:

    def __init__(self):
        self.font = pg.font.Font('res/gamefont.ttf', 16)

    def getStringAsSurface(self, string, scale = 1, color = pg.Color('white')):
        size = self.font.size(str(string))
        return pg.transform.scale(self.font.render(str(string), 1, color), tuple(map(lambda t: t * scale, size)))

    def drawString(self,surface, string, position, size=1 ,color=pg.Color(224, 228, 204)):
        text_size = self.font.size(str(string))
        text = pg.transform.scale(self.font.render(str(string), 1, color), list(map(lambda t: t * size, text_size)))
        surface.blit(text, position)

    def drawStringIndependent(self,surface, string, position, size = 1 ,color = pg.Color(224,228,204)):
        font = pg.font.Font('res/gamefont.ttf', 16)
        text_size = font.size(str(string))
        text = pg.transform.scale(font.render(str(string), 1, color), list(map(lambda t: t * size, text_size)))
        surface.blit(text, position)

    def drawStrings(self, surface, strings, position, size = 1, color = pg.Color(224,228,204)):
        for i in range(len(strings)):
            text = self.font.render(str(strings[i]), 1, color)
            surface.blit(text, (position[0], position[1] + (i * self.font.size(strings[i])[1])))

    def getStringSize(self, string, size = 1):
        return pg.font.Font('res/gamefont.ttf', 16 * size).size(str(string))

    def getStringsSize(self,strings):
        size = [self.font.size(strings[0])[0],0]
        for string in strings:
            size[1] += self.font.size(string)[1]
        return size

class GUI(StringRenderer):

    type = 'ui'

    black = pg.Color(0,0,0,200)
    def __init__(self,surface,size,pos = [0, 0]):
        super().__init__()
        self.surface = surface
        self.showing = False
        self.active = False
        self.spritesheet = AlphaSpritesheet('ui.png')
        self.pressed = False
        self.interface = pg.transform.scale(self.spritesheet.getSprite([32,48],[0,0]),size)
        self.interface.set_alpha(200)

        adjusted_pos = (pos[0] - size[0] // 2, pos[1] - size[1] // 2)
        self.rect = pg.Rect(adjusted_pos,size)
        self.state = None

    def update(self):
        pass

    def draw(self):
        if self.showing:
            self.surface.blit(self.interface,self.rect.topleft)
            self.drawFeatures()

    def drawFeatures(self):
        pass

    def toggle(self):
        self.showing = not self.showing
        self.active = not self.active

        if not self.showing:
            self.selectedSlot = None
            self.state = None
            self.active = False
        else:
            self.active = True

    def show(self):
        self.showing = True
        self.active = True

    def handleEvents(self,event):
        pass

    def handleMouseDownEvent(self,pos):
        pass

class OptionState(StringRenderer):
    def __init__(self,slot,ui):
        super().__init__()
        self.rect = pg.Rect(slot.rect.center,[100,60])
        self.options = []
        self.selected = None

    def check(self,pos):
        # Checks if button is hovered over
        for option in self.options:
            if option.check(pos):
                self.selected = option

    def isHovering(self,pos):
        return self.rect.collidepoint(pos)

    def draw(self,surface):
        # draw buttons and the option panel
        panel = pg.Surface([200, 110])
        panel.fill(pg.Color('black'))
        panel.set_alpha(200)
        for option in self.options:
            option.draw(surface)

class Button(StringRenderer):
    def __init__(self,pos,size,string):
        super().__init__()
        self.color = pg.Color('black')
        self.rect = pg.Rect(pos,size)
        self.panel = pg.Surface(size)
        self.panel.set_alpha(200)
        self.string = string

        self.hover = False
        self.pressed = False

    def check(self,pos):
        if self.rect.collidepoint(pos):
            self.color = pg.Color('gray')
            return True
        else:
            self.color = pg.Color('black')
            return False

    def getCenterPosition(self):
        return (self.rect.width//2,self.rect.height//2)

    def draw(self,surface):
        self.panel.fill(self.color)
        # Draw String on Button
        button_center = self.getCenterPosition()
        string_size = self.getStringSize(self.string)
        string_center = [button_center[0] - string_size[0]//2,
                         button_center[1] - string_size[1]//2]
        self.drawString(self.panel,self.string,string_center)

        # Draw Button on gui location
        surface.blit(self.panel,self.rect.topleft)
