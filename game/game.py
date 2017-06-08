import pygame as pg
import random
import settings, mobs, items, sprite, ui, world, controller, particles
from events import EventListener




class Game:
    bg = pg.Color('black')
    fg = pg.Color('white')
    def __init__(self, surface):

        self.windowScreen = surface
        self.windowSize = surface.get_size()

        self.end = False
        self.running = True
        self.events = EventListener(self)
        self.hud = HUD(surface)
        self.map = world.Dungeon(self)
        self.map.makeMap(32,32,50,20,30)
        self.itemManager = items.ItemController('data/items.json')

        self.player = mobs.Player((self.map.spawnx,self.map.spawny))
        self.player.inventory.addItems([self.itemManager.getItem(0)]*10)

        self.entityManager = controller.EntityController(self.player)
        self.entityManager.spawnMobs([mobs.Goblin,mobs.Skeleton],self.map)
        self.entityManager.spawnItems(self.itemManager.getItems(),self.map)

        self.camera = Camera(self.player.position,surface.get_size(), self.map)
        self.gui = ui.InventoryGUI(self.windowScreen,self.player.inventory)

        pg.key.set_repeat(5,5)

    def run(self):
        clock = pg.time.Clock()
        prev = 1
        while self.running:
            time = clock.tick(128)
            dt = (time / prev) * 12
            pg.display.set_caption('%s %i fps' % ('pyLota Alpha Build:', clock.get_fps()//1))

            self.render()
            self.events.handleEvent()
            self.update(dt)
            prev = time

    def update(self,dt):
        self.entityManager.update(self.map,dt)
        self.camera.update(self.player)

        if self.gui.showing:
            self.gui.updateSlots()

        self.hud.update(dt)


    def render(self):
        # Clear Screen
        self.windowScreen.fill(Game.bg)

        # Draw components here
        self.map.render(self.windowScreen,self.camera)
        self.entityManager.draw(self.windowScreen,self.camera)

        # Draw HUD
        self.hud.render(self.player)

        # Draw GUI
        self.gui.draw()

        # End Game
        if not self.entityManager.entities.has(self.player):
            self.end = True
            panel = pg.Surface([400,100])
            panel.fill(pg.Color(135,27,51))
            panel.set_alpha(200)
            string_size = ui.StringRenderer.getStringSize(self,'You are Dead!',48)
            ui.StringRenderer.drawString(self,panel, 'You are Dead!', ((400 - string_size[0])//2,(100 - string_size[1])//2),48)

            self.windowScreen.blit(panel,((self.windowSize[0] - 400)//2,(self.windowSize[1] - 100)//2))

        pg.display.update()

    def getCurrentMap(self):
        return self.map

    def generateLevel(self):
        self.events.clear()
        complete = False
        while not complete:
            self.map.makeMap(32, 32, 50, 20, 30)
            self.player.setPosition(self.map.getSpawn())
            self.entityManager = controller.EntityController(self.player)
            self.entityManager.spawnMobs([mobs.Goblin,mobs.Skeleton],self.map)
            self.entityManager.spawnItems(self.itemManager.getItems(), self.map)
            complete = True

        self.hud.drawQueue.append(particles.FadingText('Dungeon Level %i' % self.map.level, (self.windowSize[0]//2, self.windowSize[1]//12), 4))

class Camera:
    def __init__(self,pos,screenSize,world):
        '''
        :param screenSize: tuple
        :param worldSize: tuple
        :param target: Game object for camera to follow
        '''
        self.rect = pg.Rect(pos,screenSize)
        self.windowSize = screenSize
        self.world = world

    def apply(self, entity):
        offset = (-self.rect.left,-self.rect.top)
        return entity.rect.move(offset)

    def applyOnRect(self, rect):
        offset = (-self.rect.left,-self.rect.top)
        return rect.move(offset)

    def applyOnPosition(self,pos):
        x = pos[0] - self.rect.left
        y = pos[1] - self.rect.top
        return (x,y)

    def update(self, player):
        x =  player.rect.left - self.windowSize[0]//2
        y =  player.rect.top - self.windowSize[1]//2

        x = max(0,x)
        y = max(0,y)
        x = min(x,self.world.size_x * self.world.tile_size[1])
        y = min(y,self.world.size_y * self.world.tile_size[1])

        self.rect.topleft = [x,y]

    def isVisible(self,position):
        return self.rect.collidepoint(position)

    def drawRectangle(self,surface,color,rect):
        pg.draw.rect(surface,color,self.applyOnRect(rect),1)

class HUD(ui.StringRenderer):
    sprite_size = [16,16]
    def __init__(self,surface):
        self.surface = surface
        self.hud = pg.Surface((96,64),pg.SRCALPHA,32)
        pg.Surface.convert_alpha(self.hud)
        self.spritesheet = sprite.Spritesheet(settings.UISHEET)

        self.drawQueue = []

    def update(self,dt):
        for item in self.drawQueue:
            item.update(dt)

            if item.time <= 0:
                self.drawQueue.remove(item)

    def render(self, player):

        self.drawHUDImage((16,16),(2,2), (4,8), 1)

        pg.draw.rect(self.hud, pg.Color(151, 0, 0), pg.Rect(24, 6, 48, 4))
        pg.draw.rect(self.hud, pg.Color(0, 255, 0), pg.Rect(24, 6, int(48 * player.getHealthRatio()), 4))
        pg.draw.rect(self.hud, pg.Color(0, 150, 200), pg.Rect(24, 22, 48, 4))

        hp_hud = self.drawHUDImage([48, 16], [1, 0], [24, 0], 1)
        xp_hud = self.drawHUDImage([48, 16], [1, 1], [24, 16], 1)

        self.surface.blit(pg.transform.scale(self.hud,(288,192)),(8,8))

        for item in self.drawQueue:
            item.render(self.surface)




    def drawString(self, position, string, scale = 1, color = pg.Color('white')):
        size = self.getStringSize(string,int(16*scale))
        text = pg.font.Font('res/gamefont.ttf', 16).render(string,1,color)
        self.surface.blit(pg.transform.scale(text,(size[0],size[1])),(position[0] - size[0]//2, position[1]))

    def drawImage(self,image,position,scale = [64,64]):
        # Prints a surface on screen
        if image:
            pg.draw.rect(self.surface,pg.Color('cyan'),self.surface.blit(pg.transform.scale(image,scale),position),1)
        else:
            pg.draw.rect(self.surface, pg.Color('cyan'), pg.Rect(position,scale),1)

    def drawHUDImage(self,imageSize,imagePosition,position,scale = 1):
        # Draws an image from the hud spritesheet
        size = [imageSize[0] * scale, imageSize[1] * scale]
        image = pg.transform.scale(self.spritesheet.getSprite(imageSize,imagePosition),size)
        return self.hud.blit(image,position)




