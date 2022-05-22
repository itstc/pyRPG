import pygame as pg
from .inventory import InventoryGUI, OptionState
from .inventory import HoveringState
from .buttons import UseButton, DestroyButton
from sprite.sprite import AlphaSpritesheet, Spritesheet

class TransactionState(OptionState):

    def __init__(self, slot, ui):
        super().__init__(slot, ui)

        self.options = [
            UseButton(self.rect.topleft, [100, 30], 'Take', ui),
            DestroyButton([self.rect.left, self.rect.top + 30], [100, 30], 'Destroy', ui)
        ]

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
