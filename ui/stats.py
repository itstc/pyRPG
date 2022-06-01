import pygame as pg
from .ui import GUI, StringRenderer, OptionState
from .buttons import UnequipButton
from .inventory import HoveringState
from sprite.sprite import AlphaSpritesheet, Spritesheet

class EquipState(OptionState):

    def __init__(self, slot, ui):
        super().__init__(slot, ui)

        self.options = [
            UnequipButton(self.rect.topleft, [100, 30], 'Unequip', ui)
        ]

class StatsGUI(GUI):
    type = 'main_ui'

    colors = {
        'common': pg.Color(224, 228, 204),
        'uncommon': pg.Color(102, 255, 0),
        'rare': pg.Color(204, 0, 0),
        'super_rare': pg.Color(236, 208, 120)
    }

    equipment_order = ['head', 'body', 'leg', 'weapon']

    def __init__(self, surface, pos, player):
        super().__init__(surface, [384,384], pos)
        self.player = player


        self.interface = pg.Surface((384, 384), pg.SRCALPHA, 32)
        gui_image = pg.transform.scale(self.spritesheet.getSprite([32, 32],[0, 2]), (384, 384))
        gui_image.set_alpha(200)

        self.interface.blit(gui_image, (0, 0))
        self.textfield = self.interface.subsurface(pg.Rect(32, 80, 128, 96))

        self.drawString(self.interface, 'Stats', (32, 32), 2)
        self.equipments = [StatsGUI.Tile(self, (64,64), (384 - 96, 32 + 80 * i)) for i in range(4)]

        self.selectedSlot = None


    def update(self):
        for i in range(4):
            self.equipments[i].item = self.player.stats.equipment[StatsGUI.equipment_order[i]]
            self.equipments[i].update()

    def drawFeatures(self):
        self.textfield.fill(pg.Color(78, 77, 74, 200))

        self.drawString(self.textfield, 'Health: {} / {}'.format (self.player.stats.hp, self.player.stats.maxHP), (0, 0))
        self.drawString(self.textfield, 'Attack: {}'.format(self.player.stats.ad), (0, 16))
        self.drawString(self.textfield, 'Crit: {}%'.format(self.player.stats.crit), (0, 32))
        self.drawString(self.textfield, 'Defence: {}'.format(self.player.stats.defence), (0, 48))
        self.drawString(self.textfield, 'Haste: {}'.format(self.player.stats.maxcd), (0, 64))

        for tile in self.equipments:
            tile.draw()

        if self.state:
            self.state.draw(self.surface)

    def handleEvents(self,event):
        if event.type == pg.MOUSEBUTTONDOWN:
            self.handleMouseDownEvent(event.pos)
            self.pressed = True
        elif event.type == pg.MOUSEBUTTONUP:
            self.pressed = False
        elif event.type == pg.MOUSEMOTION:
            if self.active:
                # If hovering state is not hovered over
                if isinstance(self.state,EquipState):
                    self.state.check(event.pos)
                elif isinstance(self.state,HoveringState) and not self.selectedSlot.isHovering(event.pos):
                    self.state = None
                # If no state check if mouse is over a slot with an item
                elif not self.state and self.isHoveringSlot(event.pos) and self.selectedSlot.item:
                    self.state = HoveringState(self.selectedSlot)

    def handleMouseDownEvent(self,pos):
        if not self.pressed:
            if self.state and isinstance(self.state,EquipState) and self.state.isHovering(pos):
                # If state is EquipState and mouse is hovering
                self.state.selected.use()
                self.state = None
            elif self.state and not self.selectedSlot.isHovering(pos):
                # If there is a state but mouse is not hovering over slot
                self.state = None
            elif self.selectedSlot and self.selectedSlot.item and self.selectedSlot.isHovering(pos):
                # If selected slot has an item and is being hovered over
                self.state = EquipState(self.selectedSlot,self)

    def isHoveringSlot(self,pos):
        self.selectedSlot = None
        for slot in self.equipments:
            if slot.rect.collidepoint(pos):
                self.selectedSlot = slot
                return True
        return False

    def unequipSlot(self):
        self.player.stats.unequipItem(self.selectedSlot.item.equipment_type)

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
