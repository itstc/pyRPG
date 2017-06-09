import random, settings, sprite
import pygame as pg

class Tile():

    type = 'floor'
    collidable = False

    def __init__(self,id, image):
        self.id = id
        self.image = pg.transform.scale(image, (64,64))

    def __eq__(self, other):
        return self.id == other

    def setImage(self, x, y):
        self.image = pg.transform.scale(sprite.Spritesheet(settings.TILESHEET).getSprite((16, 16), (x, y)), (64,64))


class Void(Tile):
    type = 'void'

    def __init__(self):
        super().__init__(0, sprite.Spritesheet(settings.TILESHEET).getSprite((16, 16), (0, 2)))


class Grass(Tile):

    def __init__(self):

        if random.randrange(10) > 0:
            imgPos = (0, 0)
        else:
            imgPos = (0, 1)

        super().__init__(1, sprite.Spritesheet(settings.TILESHEET).getSprite((16, 16), imgPos))

class Wall(Tile):

    type = 'wall'
    collidable = True

    def __init__(self, x, y):
        super().__init__(2, sprite.Spritesheet(settings.TILESHEET).getSprite((16, 16), (0, 2)))
        self.rect = pg.Rect(x * 64, y * 64, 64, 64)

class ExitTile(Tile):

    type = 'world'

    def __init__(self, game, x, y):
        super().__init__(3, sprite.Spritesheet(settings.TILESHEET).getSprite((16, 16), (5, 0)))
        self.game = game
        self.rect = pg.Rect(x * 64, y * 64, 64, 64)

    def onCollide(self):
        pg.time.wait(500)
        self.game.generateLevel()