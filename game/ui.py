import pygame as pg
import sprite

class StringRenderer():
    def __init__(self,size = 16):
        self.font = pg.font.Font(pg.font.get_default_font(), size)
        self.size = size

    def drawString(self,surface, string, position, color = pg.Color('white')):
        text = self.font.render(str(string),1,color)
        surface.blit(text,position)

    def drawStrings(self, surface, strings, position, size = 16, color = pg.Color('white')):
        font = pg.font.Font(pg.font.get_default_font(), size)
        for i in range(len(strings)):
            text = font.render(str(strings[i]),1,color)
            surface.blit(text, (position[0], position[1] + (i * font.size(strings[i])[1])))

    def getStringsSize(self,strings):
        size = [self.font.size(strings[0])[0],0]
        for string in strings:
            size[1] += self.font.size(string)[1]
        return size

class GUI(StringRenderer):
    black = pg.Color(0,0,0,200)
    def __init__(self,surface,size,pos = [0,0], fontsize = 16):
        super().__init__(fontsize)
        self.surface = surface
        self.showing = False
        self.active = False
        self.spritesheet = sprite.AlphaSpritesheet('ui.png')
        self.interface = pg.transform.scale(self.spritesheet.getSprite([32,48],0,0),size)
        self.interface.set_alpha(200)
        self.rect = pg.Rect(pos,size)

    def update(self):
        pass

    def draw(self):
        if self.showing:
            self.surface.blit(self.interface,self.rect.topleft)
            self.drawFeatures()

    def drawFeatures(self):
        pass

    def toggle(self):
        pass

class InventoryGUI(GUI):
    def __init__(self,surface,inventory):
        super().__init__(surface,[256,384],fontsize=20)
        self.inventory = inventory
        self.grid = []
        start = [16,64]
        for y in range(4):
            for x in range(3):
                self.grid.append(InventoryGUI.tile(self,[64,64],[start[0] + (64 * x) + (16*x), start[1] + (64 * y) + (16*y)]))

        self.selectedSlot = None

    def update(self):
        self.updateSlots()
        for item in self.inventory.items:
                self.findEmptySlot().item = item

    def updateSlots(self):
        for slot in self.grid:
            slot.update()
            slot.item = None

    def findEmptySlot(self):
        found = self.grid[0]
        for slot in self.grid:
            if not slot.item:
                found = slot
                break

        return found

    def drawFeatures(self):
        for tile in self.grid:
            tile.draw()

        if self.selectedSlot and self.selectedSlot.item:
            panel = pg.Surface([200, 100])
            panel.fill(pg.Color('black'))
            panel.set_alpha(200)
            self.drawString(panel,self.selectedSlot.item.name,[8,8])
            self.drawStrings(panel, self.selectedSlot.item.desc, [8, 32])

            # Display panel on screen
            self.surface.blit(panel, self.selectedSlot.rect.center)

    def isHoveringSlot(self,pos):
        self.selectedSlot = None
        for slot in self.grid:
            if slot.rect.collidepoint(pos):
                self.selectedSlot = slot
                break

    def toggle(self):
        if not self.showing:
            self.selectedSlot = None
            self.active = False
        else:
            self.active = True



    class tile(StringRenderer):
        def __init__(self,gui,size,pos,item = None):
            super().__init__(20)
            self.gui = gui
            self.rect = pg.Rect(pos,size)
            self.position = pos
            self.size = size
            self.item = item
            self.image = pg.transform.scale(sprite.Spritesheet('ui.png').getSprite([16,16],2,0),size)

        def update(self):
            self.rect.topleft = [self.gui.rect.topleft[0] + self.position[0],self.gui.rect.topleft[1] + self.position[1]]

        def draw(self):
            self.gui.interface.blit(self.image,self.position)
            if self.item:
                self.gui.interface.blit(pg.transform.scale(self.item.image,self.size),self.position)
                self.drawString(self.gui.interface,self.item.amount,self.position)