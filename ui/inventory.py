import pygame as pg
from .ui import GUI, StringRenderer, OptionState
from .buttons import UseButton, DestroyButton
from sprite.sprite import AlphaSpritesheet, Spritesheet

class HoveringState(StringRenderer):
    def __init__(self,slot):
        super().__init__()
        self.slot = slot
        self.rect = pg.Rect(slot.rect.center,[200,110])
        self.selected = None

    def isHovering(self,pos):
        return self.rect.collidepoint(pos)

    def draw(self,surface):
        panel = pg.Surface([200, 110])
        panel.fill(pg.Color('black'))
        panel.set_alpha(200)
        self.drawString(panel, self.slot.item.name, [8, 8], color = InventoryGUI.colors[self.slot.item.rarity])
        # self.drawStrings(panel, self.slot.item.desc, (8, 32))
        for i,(k,v) in enumerate(self.slot.item.attributes.items()):
            posEffect = v > 0
            self.drawString(panel, "{} {} {}".format("+" if posEffect else "-", v, k), (8, 32 + i * 16), color = pg.Color('green') if posEffect else pg.Color('red'))


        surface.blit(panel,self.slot.rect.center)


class InventoryState(OptionState):

    def __init__(self, slot, ui):
        super().__init__(slot, ui)

        self.options = [
            UseButton(self.rect.topleft,[100,30],'Use',ui),
            DestroyButton([self.rect.left, self.rect.top + 30], [100, 30],'Destroy',ui)
        ]

class InventoryGUI(GUI):

    type = 'main_ui'

    colors = {
        'common': pg.Color('white'),
        'uncommon': pg.Color('green'),
        'rare': pg.Color('blue'),
        'super_rare': pg.Color('purple')
    }
    def __init__(self, surface, inventory, pos, ui_heading = 'Inventory'):
        super().__init__(surface,[256,384], pos)
        self.pressed = False
        self.inventory = inventory
        self.grid = []

        self.drawString(self.interface, ui_heading, (16,16), 2)

        start = [16,64]
        for y in range(4):
            for x in range(3):
                self.grid.append(InventoryGUI.Tile(self,[64,64],[start[0] + (64 * x) + (16*x), start[1] + (64 * y) + (16*y)]))

        self.selectedSlot = None
        self.state = None

        self.updateSlots()

    def update(self):
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
                if isinstance(self.state,InventoryState):
                    self.state.check(event.pos)
                elif isinstance(self.state,HoveringState) and not self.selectedSlot.isHovering(event.pos):
                    self.state = None
                # If no state check if mouse is over a slot with an item
                elif not self.state and self.isHoveringSlot(event.pos) and self.selectedSlot.item:
                        self.state = HoveringState(self.selectedSlot)


    def handleMouseDownEvent(self,pos):
        if not self.pressed:
            if self.state and isinstance(self.state,InventoryState) and self.state.isHovering(pos):
                # If state is InventoryState and mouse is hovering
                self.state.selected.use()
                self.state = None
            elif self.state and not self.selectedSlot.isHovering(pos):
                # If there is a state but mouse is not hovering over slot
                self.state = None
            elif self.selectedSlot and self.selectedSlot.item and self.selectedSlot.isHovering(pos):
                # If selected slot has an item and is being hovered over
                self.state = InventoryState(self.selectedSlot,self)


    class Tile(StringRenderer):
        def __init__(self,gui,size,pos,item = None):
            super().__init__()
            self.gui = gui
            self.rect = pg.Rect(pos,size)
            self.position = pos
            self.size = size
            self.item = item
            self.image = pg.transform.scale(Spritesheet('ui.png').getSprite([16,16],[2,1]),size)

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
                self.drawString(self.gui.interface,self.item.amount,(self.position[0] + 2,self.position[1] + 2))

