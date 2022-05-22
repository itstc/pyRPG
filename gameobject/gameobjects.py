import pygame as pg
from game.settings import MOBSHEET
from sprite.sprite import Spritesheet
from item.inventory import Inventory
from ui.loot import LootUI

class GameObject(pg.sprite.Sprite):

    type = 'world'
    collidable = False

    def __init__(self, sprite_group, image, pos, size):
        super().__init__()

        self.image = pg.transform.scale(image, size)
        self.rect = self.image.get_bounding_rect()
        self.rect.topleft = pos

        self.sprite_group = sprite_group

    def update(self, dt):
        pass

    def draw(self, surface, camera):
        pass

    def interact(self):
        pass


class Chest(GameObject):
    #TODO: Use Inventory to store items
    collidable = True

    def __init__(self, game, item_controller, sprite_group, pos):
        self.states = [Spritesheet(MOBSHEET).getSprite((16, 16), (0, 8)),
                       Spritesheet(MOBSHEET).getSprite((16, 16), (1, 8))]

        super().__init__(sprite_group, self.states[0], pos, (64,64))

        self.game = game
        self.items = item_controller
        self.opened = False

        self.inventory = Inventory(self, 3)
        for i in range(3):
            self.inventory.addItem(self.items.getRandomItem())

    def interact(self):
        if not self.opened:
            self.opened = True
            self.image = pg.transform.scale(self.states[1], (64,64))

        self.game.gui = LootUI(self.game.windowScreen, self.game.player.inventory, self.inventory,
                                  (self.game.windowSize[0] // 2, self.game.windowSize[1] // 2))
