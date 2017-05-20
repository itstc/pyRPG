import pygame as pg
import mobs,items,sprite,ui
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
        self.map = World(self.surface,'res/testmeta.tmx')
        self.entities = sprite.EntityGroup()
        self.player = mobs.Player(256,512)
        self.player.inventory.addItem(items.Potion())
        self.entities.add(items.Potion().drop(64,64),items.Potion().drop(128,64),items.Potion().drop(256,64),items.Sword().drop(64,256),items.Sword().drop(64,512))
        self.entities.add(mobs.Goblin(256,128),mobs.Skeleton(512,128),mobs.Skeleton(400,128),self.player)


        self.camera = Camera(surface.get_size(), self.map.getWorldSize(), self.player)
        self.gui = ui.InventoryGUI(self.surface,self.player.inventory)

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




