import pygame as pg
import mobs,items,sprite
from events import EventListener
from world import World




class Game:
    bg = pg.Color('black')
    fg = pg.Color('white')
    def __init__(self, surface):

        self.surface = surface
        self.windowSize = surface.get_size()
        self.running = True
        self.events = EventListener(self)
        self.hud = HUD(surface)
        self.map = World(self.surface,'res/test.tmx')
        self.entities = sprite.EntityGroup()
        self.player = mobs.Player(256,512)
        self.player.inventory.addItem(items.Potion())
        self.entities.add(items.Potion().drop(64,64),items.Potion().drop(128,64),items.Potion().drop(256,64),items.Sword().drop(64,256),items.Sword().drop(64,512))
        self.entities.add(mobs.Goblin(256,128),mobs.Skeleton(512,128),mobs.Skeleton(400,128),self.player)


        self.camera = Camera(surface.get_size(), self.map.getWorldSize(), self.player)
        self.gui = InventoryGUI(self.surface,self.player.inventory)

        pg.key.set_repeat(1,1)

    def run(self):
        clock = pg.time.Clock()
        while self.running:
            dt = clock.tick(60)

            pg.display.set_caption('%s %i fps' % ('pyLota Alpha Build:', clock.get_fps()//1))

            self.render()
            self.events.handleEvent()
            self.update(dt)

    def update(self,dt):
        self.entities.update(self.map,dt)
        self.gui.update()

    def render(self):
        # Clear Screen
        self.surface.fill(Game.bg)

        # Draw components here
        self.map.render(self.camera)
        self.entities.draw(self.surface,self.camera)

        self.gui.draw()

        pg.display.update()

    def getCurrentMap(self):
        return self.map

    def loadMap(self,file):
        self.map = World(self.surface,file)


class Camera:
    def __init__(self, screenSize, worldSize, target):
        '''
        :param screenSize: tuple
        :param worldSize: tuple
        :param target: Game object for camera to follow
        '''
        self.windowSize = screenSize
        self.world = worldSize
        self.target = target

        self.offset = []
        self.moveCamera()

    def isVisible(self,position):
        """
        checks if a pygame.Rect() object is in the self.view
        :param rect: pygame.Rect()
        :return: bool
        """
        return (position[0] - self.offset[0] >= 0) and (position[1] - self.offset[1] >= 0)

    def getOffsetPosition(self,rect):
        return (rect.center[0] - self.offset[0], rect.center[1] - self.offset[1])


    def getView(self):
        # returns the camera position
        return (int(self.offset[0]), int(self.offset[1]))

    def moveCamera(self):
        # moves the camera by x and y
        # -x,y are integers
        targetPos = self.target.getPosition()
        self.offset = [targetPos[0] - self.windowSize[0] // 2, targetPos[1] - self.windowSize[1] // 2]

        # Bounds of the World
        for coord in range(2):
            if self.offset[coord] < 0:
                self.offset[coord] = 0
            elif self.offset[coord] > self.world[coord] - self.windowSize[coord]:
                self.offset[coord] = self.world[coord] - self.windowSize[coord]

    def drawRectangle(self,surface,color,rect):
        orect = pg.Rect((rect.topleft[0] - self.offset[0], rect.topleft[1] - self.offset[1]),rect.size)
        pg.draw.rect(surface,color,orect,1)

class HUD():
    sprite_size = [16,16]
    def __init__(self,surface):
        self.surface = surface
        self.spritesheet = sprite.Spritesheet('hud.png')
        self.font = pg.font.Font(pg.font.get_default_font(),16)

    def drawString(self, position, string, color = pg.Color('white')):
        text = self.font.render(string,1,color)
        self.surface.blit(text,position)

    def drawImage(self,image,position,scale = [64,64]):
        # Prints a surface on screen
        if image:
            pg.draw.rect(self.surface,pg.Color('cyan'),self.surface.blit(pg.transform.scale(image,scale),position),1)
        else:
            pg.draw.rect(self.surface, pg.Color('cyan'), pg.Rect(position,scale),1)
    def drawHUDImage(self,imagePosition,position,scale = [64,64]):
        # Draws an image from the hud spritesheet
        image = pg.transform.scale(self.spritesheet.getSprite(HUD.sprite_size,imagePosition[0],imagePosition[1]),scale)
        pg.draw.rect(self.surface,pg.Color('black'),self.surface.blit(image,position),1)

class GUI:
    black = pg.Color(0,0,0,200)
    def __init__(self,surface,size,pos = [0,0]):
        self.surface = surface
        self.showing = False
        self.active = False
        self.spritesheet = sprite.AlphaSpritesheet('ui.png')
        self.window = pg.transform.scale(self.spritesheet.getSprite([32,48],0,0),size)
        self.window.set_alpha(200)
        self.rect = pg.Rect(pos,size)




    def update(self):
        pass

    def draw(self):
        if self.showing:
            self.surface.blit(self.window,self.rect.topleft)
            self.drawFeatures()

    def drawFeatures(self):
        pass

    def hide(self):
        self.showing = False

class StringRenderer():
    def __init__(self,size = 16):
        self.font = pg.font.Font(pg.font.get_default_font(), size)
        self.size = size

    def drawString(self,surface, string, position, color = pg.Color('white')):
        text = self.font.render(str(string),1,color)
        surface.blit(text,position)

    def drawStrings(self, surface, strings, position, color = pg.Color('white')):
        for i in range(len(strings)):
            text = self.font.render(str(strings[i]),1,color)
            surface.blit(strings[i], position + (i * self.font.size(strings[i])))

    def getStringsSize(self,strings):
        size = [self.font.size(strings[0])[0],0]
        for string in strings:
            size[1] += self.font.size(string)[1]
        return size


class InventoryGUI(GUI):
    def __init__(self,surface,inventory):
        super().__init__(surface,[256,384])
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

        if self.selectedSlot:
            panel = pg.Surface([200, 120])
            panel.fill(pg.Color('black'))
            panel.set_alpha(128)
            self.surface.blit(panel, self.selectedSlot.rect.center)

    def isHoveringSlot(self,pos):
        self.selectedSlot = None
        for slot in self.grid:
            if slot.rect.collidepoint(pos):
                self.selectedSlot = slot
                break

    def hide(self):
        if not self.showing:
            self.selectedSlot = None



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
            self.gui.window.blit(self.image,self.position)
            if self.item:
                self.gui.window.blit(pg.transform.scale(self.item.image,self.size),self.position)
                self.drawString(self.gui.window,self.item.amount,self.position)


