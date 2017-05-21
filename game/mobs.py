import pygame as pg
import sprite,particles
from inventory import Inventory



class Mob(pg.sprite.Sprite):
    sprite_size = [16,32]
    collidable = True
    def __init__(self,image,size,position,health,ad):
        super().__init__()
        self.stats = Mob.Stats(health,ad)
        self.size = size
        self.position = position
        self.image = pg.transform.scale(image,size)
        self.rect = pg.Rect(position,[size[0]//2,size[1]])
        self.rect.center = self.position
        self.fov = []
        self.attacking = False
        self.cooldown = 0
        self.direction = 0 # 0:top, 1:left, 2:down, 3:right

    def getAttackRange(self,direction):
        tlPos = self.rect.topleft
        range = {
            0: pg.Rect(tlPos[0] - self.size[0] // 2, tlPos[1] - self.size[1] // 4, self.size[0] // 2 * 3,
                           self.size[1] // 4),
            1: pg.Rect(tlPos[0] - self.size[0] // 2, tlPos[1], self.size[0] // 2, self.size[1]),
            2: pg.Rect(tlPos[0] - self.size[0] // 2, tlPos[1] + self.size[1], self.size[0] // 2 * 3,
                            self.size[1] // 4),
            3: pg.Rect(tlPos[0] + self.size[0] // 2, tlPos[1], self.size[0] // 2, self.size[1])
        }
        return range[direction]

    def getLegBox(self):
        # Returns a pygame.Rect object of the legs of sprite
        legBox = pg.Rect(self.position[0]-self.size[0]//4, self.position[1],self.size[0]//2, self.size[1]//2)
        return legBox

    def move(self,x,y):
        # Moves sprite if not colliding
        if not self.isColliding(x,y):
            self.position = [self.position[0] + x, self.position[1] + y]

    def draw(self,surface,camera, offset):

        # Draw Health Bar
        pg.draw.rect(surface, pg.Color('red'), pg.Rect(offset[0], offset[1] - 16, self.size[0], 8))
        pg.draw.rect(surface, pg.Color('green'),pg.Rect(offset[0], offset[1] - 16, int(self.size[0] * (self.stats.hp / self.stats.maxHP)), 8))

        # Draws collision box
        # camera.drawRectangle(surface, pg.Color('cyan'), self.rect)
        # camera.drawRectangle(surface, pg.Color('purple'), self.getLegBox())

        self.stats.draw(surface,camera)

    def update(self,dt):
        # Update collision box position
        self.rect.center = self.position

        if self.attacking:
            self.cooldown += dt
            if self.cooldown // 500 > 0:
                self.attacking = False
                self.cooldown = 0

        if self.stats.hp <= 0:
            self.kill()

        self.stats.update(dt)

    def isColliding(self, x, y):
        # Takes offset x,y and sees if sprite is colliding with any objects in fov
        offset = self.getLegBox()
        offset.center = [offset.center[0] + x, offset.center[1] + y]
        collide = False
        for i in self.fov:
            if offset.colliderect(i.rect) and i.collidable:
                collide = True
        return collide

    class Stats:
        def __init__(self,health,ad):
            self.maxHP = health
            self.hp = health
            self.ad = ad
            self.statQueue = []

        def damage(self,target):
            target.stats.hurt(self.ad)
            self.statQueue.append(particles.BouncyText(self,self.ad,[target.rect.centerx,target.rect.top]))

        def hurt(self,value):
            self.hp -= value

        def update(self,dt):
            for item in self.statQueue:
                item.update(dt)

        def draw(self,surface,camera):
            for item in self.statQueue:
                item.draw(surface,camera)
class Goblin(Mob):
    name = 'Goblin'
    def __init__(self,x,y):
        super().__init__(sprite.Spritesheet('mobsheet.png').getSprite(Mob.sprite_size,[0,0]),(64,96),(x,y),25,8)

class Skeleton(Mob):
    name = 'Skeleton'
    def __init__(self,x,y):
        super().__init__(sprite.Spritesheet('mobsheet.png').getSprite(Mob.sprite_size,[1,0]),(64,128),(x,y),30,10)

class Player(Mob):
    # TODO: Create a player and place it on the map
    def __init__(self,x,y):
        sheet = sprite.Spritesheet('playersheet.png')
        super().__init__(sheet.getSprite([16,24],[3,1]), (64,96), (x,y),100,9)
        self.stats.hp = 50
        self.isWalking = False

        self.states = {
            0:sprite.AnimatedSprite(sheet, [(3, 0), (4, 0), (5, 0)], [16, 24], self.size,200),
            1:sprite.AnimatedSprite(sheet, [(0, 1), (1, 1), (2, 1)], [16, 24], self.size,200),
            2:sprite.AnimatedSprite(sheet, [(0, 0), (1, 0), (2, 0)], [16, 24], self.size,200),
            3:sprite.AnimatedSprite(sheet, [(3, 1), (4, 1), (5, 1)], [16, 24], self.size,200),
            4:sprite.AnimatedSprite(sheet, [(8, 0), (9, 0)], [16, 24], self.size,200),
            5:sprite.AnimatedSprite(sheet, [(6, 1), (7, 1)], [16, 24], self.size,200),
            6:sprite.AnimatedSprite(sheet, [(6, 0), (7, 0)], [16, 24], self.size,200),
            7:sprite.AnimatedSprite(sheet, [(8, 1), (9, 1)], [16, 24], self.size,200)
                       }

        self.inventory = Inventory(self,10)

    def update(self,dt):
        super().update(dt)
        if self.attacking:
            self.image = self.states[self.direction + 4].update(dt)
        elif self.isWalking:
            self.image = self.states[self.direction].update(dt)
        else:
            self.image = self.states[self.direction].currentFrame()

    def getPosition(self):
        return self.position

    def getSize(self):
        return self.size

    def move(self,x,y):
        if not self.isColliding(x,y):
            self.position = (self.position[0] + x, self.position[1] + y)

    def attack(self):
        self.attacking = True
        for obj in self.fov:
            if self.getAttackRange(self.direction).colliderect(obj) and isinstance(obj,Mob):
                self.stats.damage(obj)