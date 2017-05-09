import pygame as pg

from world import World
from entity import mobs,items
from sprites import sprite
from util import Polygon


class Game:
    bg = pg.Color('black')
    fg = pg.Color('white')
    def __init__(self, surface):

        self.surface = surface
        self.windowSize = surface.get_size()
        self.running = True
        self.hud = HUD(surface)
        self.map = World(self.surface,'res/test.tmx')
        self.entities = sprite.EntityGroup()
        self.player = mobs.Player(256,512)
        self.entities.add(items.Potion(64,64),items.Bow(128,128),items.Club(256,64),items.Axe(64,256),items.Sword(64,512),items.Spear(900,512))
        self.entities.add(mobs.Goblin(256,128),mobs.Skeleton(512,128),mobs.Skeleton(400,128),self.player)


        self.camera = Camera(surface.get_size(), self.map.getWorldSize(), self.player)

        pg.key.set_repeat(1,1)

    def run(self):
        clock = pg.time.Clock()
        while self.running:
            dt = clock.tick(60)

            pg.display.set_caption('%s %i fps' % ('pyLota Alpha Build:', clock.get_fps()//1))

            self.render()
            self.handleEvent()
            self.update(dt)

    def handleEvent(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running = False
                pg.quit()
                exit()
            elif event.type == pg.MOUSEBUTTONDOWN:
                self.handleMouseEvent(event.pos)
            elif event.type == pg.KEYDOWN:
                self.handleKeyEvent(event.key)
            elif event.type == pg.KEYUP:
                self.player.isWalking = False

    def handleMouseEvent(self,pos):
        self.player.direction = self.getMouseDirection(pos)
        if not self.player.attacking:
            self.player.attack()

    def getMouseDirection(self,pos):
        playerPos = self.camera.getOffsetPosition(self.player.rect)
        polygons = {
            # 0:top, 1:left, 2:down, 3:right
            0: Polygon([(0,0), playerPos,(self.windowSize[0],0)]),
            1: Polygon([(0,0), playerPos, (0, self.windowSize[1])]),
            2: Polygon([(0, self.windowSize[1]), playerPos, self.windowSize]),
            3: Polygon([(self.windowSize[0],0), playerPos, self.windowSize])
        }

        for key in polygons.keys():
            if polygons[key].collide(pos):
                return key

    def handleKeyEvent(self,key):
        self.player.isWalking = True
        moveSpeed = 4
        if key == pg.K_w:
            self.player.direction = 0
            self.player.move(0,-moveSpeed)
        elif key == pg.K_a:
            self.player.direction = 1
            self.player.move(-moveSpeed,0)
        elif key == pg.K_s:
            self.player.direction = 2
            self.player.move(0,moveSpeed)
        elif key == pg.K_d:
            self.player.direction = 3
            self.player.move(moveSpeed,0)

        self.camera.moveCamera()

    def update(self,dt):
        self.entities.update(self.map,dt)

    def render(self):
        # Clear Screen
        self.surface.fill(Game.bg)

        # Draw components here
        self.map.render(self.camera)
        self.entities.draw(self.surface,self.camera)

        # Draw HUD Here
        self.hud.drawHUDImage([0, 0], [self.windowSize[0] - 64,self.windowSize[1] - 192])
        self.hud.drawHUDImage([1, 0], [self.windowSize[0] - 64,self.windowSize[1] - 128])
        self.hud.drawHUDImage([2, 0], [self.windowSize[0] - 64,self.windowSize[1] - 64])

        self.hud.drawString([self.windowSize[0] - 64, self.windowSize[1] - 192], '12')
        self.hud.drawString([self.windowSize[0] - 64, self.windowSize[1] - 128], '10')
        self.hud.drawString([self.windowSize[0] - 64, self.windowSize[1] - 64], '10')

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

    def drawImage(self,image,position):
        # Prints a surface on screen
        self.surface.blit(image,position)

    def drawHUDImage(self,imagePosition,position,scale = [64,64]):
        # Draws an image from the hud spritesheet
        image = pg.transform.scale(self.spritesheet.getSprite(HUD.sprite_size,imagePosition[0],imagePosition[1]),scale)
        pg.draw.rect(self.surface,pg.Color('black'),self.surface.blit(image,position),1)

