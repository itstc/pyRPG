import pygame as pg
import sprite
import random

class StringRenderer():

    def drawString(self,surface, string, position,size = 16,color = pg.Color(224,228,204)):
        text = pg.font.Font('res/gamefont.ttf', size).render(str(string),1,color)
        surface.blit(text,position)

    def drawStrings(self, surface, strings, position, size = 16, color = pg.Color(224,228,204)):
        font = pg.font.Font('res/gamefont.ttf', size)
        for i in range(len(strings)):
            text = font.render(str(strings[i]),1,color)
            surface.blit(text, (position[0], position[1] + (i * font.size(strings[i])[1])))

    def getStringSize(self,string,size=16):
        return pg.font.Font('res/gamefont.ttf', size).size(str(string))

    def getStringsSize(self,strings):
        size = [self.font.size(strings[0])[0],0]
        for string in strings:
            size[1] += self.font.size(string)[1]
        return size

class GUI(StringRenderer):
    black = pg.Color(0,0,0,200)
    def __init__(self,surface,size,pos = [0,0]):
        super().__init__()
        self.surface = surface
        self.showing = False
        self.active = False
        self.spritesheet = sprite.AlphaSpritesheet('ui.png')
        self.interface = pg.transform.scale(self.spritesheet.getSprite([32,48],[0,0]),size)
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
    colors = {
        'common': pg.Color(224,228,204),
        'uncommon': pg.Color(102,255,0),
        'rare': pg.Color(204,0,0),
        'super_rare': pg.Color(236,208,120)
    }
    def __init__(self,surface,inventory):
        super().__init__(surface,[256,384])
        self.inventory = inventory
        self.grid = []
        start = [16,64]
        for y in range(4):
            for x in range(3):
                self.grid.append(InventoryGUI.Tile(self,[64,64],[start[0] + (64 * x) + (16*x), start[1] + (64 * y) + (16*y)]))

        self.selectedSlot = None
        self.state = None

    def useItem(self):
        self.inventory.useItem(self.selectedSlot.item)

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

        if self.state:
            self.state.draw(self.surface)

    def moveInterface(self,pos):
        self.rect.centerx = pos[0]
        self.rect.top = pos[1]

    def isHoveringSlot(self,pos):
        self.selectedSlot = None
        for slot in self.grid:
            if slot.rect.collidepoint(pos):
                self.selectedSlot = slot
                return True
        return False

    def toggle(self):
        self.showing = not self.showing
        self.active = not self.active

        if not self.showing:
            self.selectedSlot = None
            self.state = None
            self.active = False
        else:
            self.active = True

    def handleEvents(self,event):
        if event.type == pg.MOUSEBUTTONDOWN:
            self.handleMouseDownEvent(event.pos)
        elif event.type == pg.MOUSEMOTION:
            if self.active:
                # If hovering state is not hovered over
                if isinstance(self.state,OptionState):
                    self.state.check(event.pos)
                elif isinstance(self.state,HoveringState) and not self.selectedSlot.isHovering(event.pos):
                    self.state = None
                # If no state check if mouse is over a slot with an item
                elif not self.state and self.isHoveringSlot(event.pos) and self.selectedSlot.item:
                        self.state = HoveringState(self.selectedSlot)
                elif 1 in event.buttons:
                    self.moveInterface(event.pos)


    def handleMouseDownEvent(self,pos):
        if isinstance(self.state,OptionState) and self.state.isHovering(pos):
            self.state.selected.use()
            self.state = None
        elif self.state and not self.selectedSlot.isHovering(pos):
            self.state = None
        elif self.selectedSlot and self.selectedSlot.item and self.selectedSlot.isHovering(pos):
            self.state = OptionState(self.selectedSlot,self)


    class Tile(StringRenderer):
        def __init__(self,gui,size,pos,item = None):
            super().__init__()
            self.gui = gui
            self.rect = pg.Rect(pos,size)
            self.position = pos
            self.size = size
            self.item = item
            self.image = pg.transform.scale(sprite.Spritesheet('ui.png').getSprite([16,16],[2,0]),size)

        def isHovering(self,pos):
            return self.rect.collidepoint(pos)

        def update(self):
            # update tile position based on gui position
            self.rect.topleft = [self.gui.rect.topleft[0] + self.position[0],self.gui.rect.topleft[1] + self.position[1]]

        def draw(self):
            # Draw slot image onto gui
            self.gui.interface.blit(self.image,self.position)
            # If there is an item occupying slot draw the item and the amount
            if self.item:
                self.gui.interface.blit(pg.transform.scale(self.item.image,self.size),self.position)
                self.drawString(self.gui.interface,self.item.amount,(self.position[0]+2,self.position[1]+2))

class HoveringState(StringRenderer):
    def __init__(self,slot):
        self.slot = slot
        self.rect = pg.Rect(slot.rect.center,[200,110])
        self.selected = None

    def isHovering(self,pos):
        return self.rect.collidepoint(pos)

    def draw(self,surface):
        panel = pg.Surface([200, 110])
        panel.fill(pg.Color('black'))
        panel.set_alpha(200)
        self.drawString(panel, self.slot.item.name, [8, 8], 24,
                        InventoryGUI.colors[self.slot.item.rarity])
        self.drawStrings(panel, self.slot.item.desc, [8, 32], 18)

        surface.blit(panel,self.slot.rect.center)

class OptionState(StringRenderer):
    def __init__(self,slot,ui):
        self.rect = pg.Rect(slot.rect.center,[100,60])
        self.options = [
            UseButton(self.rect.topleft,[100,30],'Use',ui),
            Button([self.rect.left, self.rect.top + 30], [100, 30],'Destroy')
        ]
        self.selected = self.options[0]

    def check(self,pos):
        for option in self.options:
            option.check(pos)

    def isHovering(self,pos):
        return self.rect.collidepoint(pos)

    def draw(self,surface):
        panel = pg.Surface([200, 110])
        panel.fill(pg.Color('black'))
        panel.set_alpha(200)
        for option in self.options:
            option.draw(surface)


class Button(StringRenderer):
    def __init__(self,pos,size,string):
        self.color = pg.Color('black')
        self.rect = pg.Rect(pos,size)
        self.ui = pg.Surface(size)
        self.ui.set_alpha(200)
        self.string = string

        self.hover = False
        self.pressed = False

    def check(self,pos):
        if self.rect.collidepoint(pos):
            self.color = pg.Color('gray')
        else:
            self.color = pg.Color('black')

    def getCenterPosition(self):
        return (self.rect.width//2,self.rect.height//2)

    def draw(self,surface):
        self.ui.fill(self.color)
        # Draw String on Button
        button_center = self.getCenterPosition()
        string_size = self.getStringSize(self.string)
        string_center = [button_center[0] - string_size[0]//2,
                         button_center[1] - string_size[1]//2]
        self.drawString(self.ui,self.string,string_center)

        # Draw Button on gui location
        surface.blit(self.ui,self.rect.topleft)

class UseButton(Button):
    def __init__(self,pos,size,string,inventory):
        super().__init__(pos,size,string)
        self.inventory = inventory

    def use(self):
        self.inventory.useItem()