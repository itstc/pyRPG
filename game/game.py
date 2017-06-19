import pygame as pg
import random
import settings, mobs, items, sprite, ui, world, controller, particles, ai, util
from events import EventListener




class Game:
    bg = pg.Color('black')
    fg = pg.Color('white')
    def __init__(self, surface):

        self.windowScreen = surface
        self.windowSize = surface.get_size()

        self.disable = False
        self.running = True
        self.events = EventListener(self)
        self.hud = HUD(surface)
        self.map = world.Forest(self)
        self.itemManager = items.ItemController('data/items.json')

        self.entityManager = controller.EntityController()

        self.player = mobs.Player(self.entityManager.entities, (self.map.spawnx,self.map.spawny))
        self.player.inventory.addItems([self.itemManager.getItem(0)]*10)

        self.entityManager.spawnMobs([ai.Goblin, ai.Skeleton],self.map)
        self.entityManager.spawnItems(self.itemManager.getItems(),self.map)
        self.entityManager.entities.add(self.player)

        self.camera = Camera(self.player.position,surface.get_size(), self.map)

        self.ui_manager = {
        'inventory': ui.InventoryGUI(self.windowScreen,self.player.inventory, (settings.WINDOW_SIZE[0] // 2,settings.WINDOW_SIZE[1] // 2))}

        self.gui = self.ui_manager['inventory']

        pg.key.set_repeat(5,5)

    def run(self):
        clock = pg.time.Clock()
        prev = 1
        while self.running:
            time = clock.tick(128)
            dt = (time / prev) * 12
            pg.display.set_caption('%s %i fps' % ('pyLota Alpha Build:', clock.get_fps()//1))

            if not self.disable:
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
        if self.gui.showing:
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

        self.disable = True
        self.entityManager.entities.empty()
        self.events.clear()

        self.map = world.Forest(self)
        self.entityManager.spawnMobs([ai.Goblin, ai.Skeleton],self.map)
        self.entityManager.spawnItems(self.itemManager.getItems(), self.map)
        self.entityManager.spawnChest(self, self.itemManager, self.map)


        pg.time.wait(500)
        self.hud.drawQueue.append(particles.FadingText('Dungeon Level %i' % self.map.level, (self.windowSize[0] // 2, self.windowSize[1] // 12), 4))
        self.disable = False

        self.player.setPosition(self.map.getSpawn())
        self.entityManager.entities.add(self.player)

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

        self.view_x = 0
        self.view_y = 0

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
        self.view_x =  util.lerp(self.view_x, player.rect.left - self.windowSize[0]//2, 0.1)
        self.view_y =  util.lerp(self.view_y, player.rect.top - self.windowSize[1]//2, 0.1)

        self.view_x = max(0,self.view_x)
        self.view_y = max(0,self.view_y)
        self.view_x = min(self.view_x,self.world.size_x * settings.TILE_SIZE[0] - self.windowSize[0])
        self.view_y = min(self.view_y,self.world.size_y * settings.TILE_SIZE[1] - self.windowSize[1])

        self.rect.topleft = [self.view_x,self.view_y]

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
        self.drawHUDImage((16, 16), (2, 2), (0, 6), 1)

        hp_hud = self.drawHUDImage([48, 16], [1, 0], [24, 0], 1)
        xp_hud = self.drawHUDImage([48, 16], [1, 1], [24, 16], 1)

        self.drawQueue = []

    def update(self,dt):
        for item in self.drawQueue:
            item.update(dt)

            if item.time <= 0:
                self.drawQueue.remove(item)

    def render(self, player):

        pg.draw.rect(self.surface, pg.Color(151, 0, 0), pg.Rect(64, 28, 96, 8))
        pg.draw.rect(self.surface, pg.Color(0, 255, 0), pg.Rect(64, 28, int(96 * player.getHealthRatio()), 8))
        pg.draw.rect(self.surface, pg.Color(0, 150, 200), pg.Rect(64, 60, 96, 8))

        self.surface.blit(pg.transform.scale(self.hud,(192, 128)),(16, 16))

        for item in self.drawQueue:
            item.render(self.surface)




    def drawStringToSurface(self,string, position, scale = 1, color = pg.Color('white')):
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




