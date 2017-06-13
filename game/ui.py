import pygame as pg
import sprite, settings
import random

class StringRenderer():

    def getStringAsSurface(self, string, scale = 1, color = pg.Color('white')):
        size = self.getStringSize(string, int(16 * scale))
        return pg.transform.scale(pg.font.Font('res/gamefont.ttf', 16).render(str(string),1,color), size)

    def drawString(self,surface, string, position, size = 16,color = pg.Color(224,228,204)):
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

    type = 'ui'

    black = pg.Color(0,0,0,200)
    def __init__(self,surface,size,pos = [0, 0]):
        super().__init__()
        self.surface = surface
        self.showing = False
        self.active = False
        self.spritesheet = sprite.AlphaSpritesheet('ui.png')
        self.interface = pg.transform.scale(self.spritesheet.getSprite([32,48],[0,0]),size)
        self.interface.set_alpha(200)

        adjusted_pos = (pos[0] - size[0] // 2, pos[1] - size[1] // 2)
        self.rect = pg.Rect(adjusted_pos,size)

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

    def show(self):
        self.showing = True
        self.active = True

class InventoryGUI(GUI):

    type = 'main_ui'

    colors = {
        'common': pg.Color(224,228,204),
        'uncommon': pg.Color(102,255,0),
        'rare': pg.Color(204,0,0),
        'super_rare': pg.Color(236,208,120)
    }
    def __init__(self, surface, inventory, pos, ui_heading = 'Inventory'):
        super().__init__(surface,[256,384], pos)
        self.pressed = False
        self.inventory = inventory
        self.grid = []

        self.drawString(self.interface, ui_heading, (16,16), 32)

        start = [16,64]
        for y in range(4):
            for x in range(3):
                self.grid.append(InventoryGUI.Tile(self,[64,64],[start[0] + (64 * x) + (16*x), start[1] + (64 * y) + (16*y)]))

        self.selectedSlot = None
        self.state = None

        self.updateSlots()

    def useSlot(self):
        self.inventory.useItem(self.selectedSlot.item)
        self.selectedSlot.item = None
        self.selectedSlot = None

        self.updateSlots()

    def destroyItem(self):
        self.inventory.removeItem(self.selectedSlot.item)
        self.selectedSlot.item = None
        self.selectedSlot = None

        self.updateSlots()

    def updateSlots(self):
        for slot in self.grid:
            slot.item = None
        for i,item in enumerate(self.inventory.items):
            self.grid[i].item = item
            self.grid[i].update()

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
            self.pressed = True
        elif event.type == pg.MOUSEBUTTONUP:
            self.pressed = False
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


    def handleMouseDownEvent(self,pos):
        if not self.pressed:
            if self.state and isinstance(self.state,OptionState) and self.state.isHovering(pos):
                # If state is OptionState and mouse is hovering
                self.state.selected.use()
                self.state = None
            elif self.state and not self.selectedSlot.isHovering(pos):
                # If there is a state but mouse is not hovering over slot
                self.state = None
            elif self.selectedSlot and self.selectedSlot.item and self.selectedSlot.isHovering(pos):
                # If selected slot has an item and is being hovered over
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
            DestroyButton([self.rect.left, self.rect.top + 30], [100, 30],'Destroy',ui)
        ]
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

class TransactionState(OptionState):

    def __init__(self, slot, ui):
        super().__init__(slot, ui)

        self.options = [
            UseButton(self.rect.topleft, [100, 30], 'Take', ui),
            DestroyButton([self.rect.left, self.rect.top + 30], [100, 30], 'Destroy', ui)
        ]


class Button(StringRenderer):
    def __init__(self,pos,size,string):
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

class UseButton(Button):
    def __init__(self,pos,size,string,ui):
        super().__init__(pos,size,string)
        self.ui = ui

    def use(self):
        self.ui.useSlot()

class DestroyButton(Button):
    def __init__(self,pos,size,string,ui):
        super().__init__(pos,size,string)
        self.ui = ui

    def use(self):
        self.ui.destroyItem()

class LootUI(InventoryGUI):

    type = 'ui'

    def __init__(self, surface, player_inventory, inventory, pos):
        super().__init__(surface, inventory, pos, 'Loot')

        self.player_inventory = player_inventory
        self.showing = True
        self.active = True


    def useSlot(self):
        self.player_inventory.addItem(self.selectedSlot.item)
        self.inventory.removeItem(self.selectedSlot.item)
        self.selectedSlot.item = None
        self.selectedSlot = None

        self.updateSlots()

    def handleEvents(self,event):
        if event.type == pg.MOUSEBUTTONDOWN:
            self.handleMouseDownEvent(event.pos)
            self.pressed = True
        elif event.type == pg.MOUSEBUTTONUP:
            self.pressed = False
        elif event.type == pg.MOUSEMOTION:
            if self.active:
                # If hovering state is not hovered over
                if isinstance(self.state,TransactionState):
                    self.state.check(event.pos)
                elif isinstance(self.state,HoveringState) and not self.selectedSlot.isHovering(event.pos):
                    self.state = None
                # If no state check if mouse is over a slot with an item
                elif not self.state and self.isHoveringSlot(event.pos) and self.selectedSlot.item:
                        self.state = HoveringState(self.selectedSlot)


    def handleMouseDownEvent(self,pos):
        if not self.pressed:
            if self.state and isinstance(self.state,TransactionState) and self.state.isHovering(pos):
                # If state is OptionState and mouse is hovering
                self.state.selected.use()
                self.state = None
            elif self.state and not self.selectedSlot.isHovering(pos):
                # If there is a state but mouse is not hovering over slot
                self.state = None
            elif self.selectedSlot and self.selectedSlot.item and self.selectedSlot.isHovering(pos):
                # If selected slot has an item and is being hovered over
                self.state = TransactionState(self.selectedSlot, self)