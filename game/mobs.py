import pygame as pg
import sprite,particles
from inventory import Inventory



class Mob(pg.sprite.Sprite):
    sprite_size = [16,16]
    collidable = True
    type = 'mob'
    def __init__(self,images,size,position,health,ad):
        super().__init__()
        self.image = pg.Surface(size)

        self.size = size
        self.position = list(position)
        self.rect = pg.Rect(position[0],position[1],size[0],size[1])

        self.fov = []
        self.maxcd = 500
        self.cooldown = self.maxcd

        self.action = Mob.Actions(self,images)
        self.stats = Mob.Stats(health,ad)

    def getAttackRange(self,direction):
        tlPos = self.rect.topleft
        range = {
            'up': pg.Rect(tlPos[0] - self.size[0] // 2, tlPos[1] - self.size[1] // 4, self.size[0] // 2 * 3,
                           self.size[1] // 4),
            'left': pg.Rect(tlPos[0] - self.size[0] // 2, tlPos[1], self.size[0] // 2, self.size[1]),
            'down': pg.Rect(tlPos[0] - self.size[0] // 2, tlPos[1] + self.size[1], self.size[0] // 2 * 3,
                            self.size[1] // 4),
            'right': pg.Rect(tlPos[0] + self.size[0] // 2, tlPos[1], self.size[0] // 2, self.size[1])
        }
        return range[direction]

    def getLegBox(self):
        # Returns a pygame.Rect object of the legs of sprite
        legBox = pg.Rect(self.rect.centerx-self.size[0]//4, self.rect.centery,self.size[0]//2, self.size[1]//2)
        return legBox

    def drawHealthBar(self,surface,camera):
        bar_width = self.size[0]
        red_bar = pg.Rect(self.rect.left, self.rect.top - 16, bar_width, 8)
        green_bar = pg.Rect(self.rect.left, self.rect.top - 16, int(bar_width * (self.stats.hp / self.stats.maxHP)), 8)

        pg.draw.rect(surface, pg.Color('red'),camera.applyOnRect(red_bar))
        pg.draw.rect(surface, pg.Color('green'),camera.applyOnRect(green_bar))

    def draw(self,surface,camera):
        self.action.draw()

        # Draw Health Bar
        self.drawHealthBar(surface,camera)

        # Draws collision box
        camera.drawRectangle(surface, pg.Color('purple'), self.getLegBox())

        self.stats.draw(surface,camera)

    def update(self,dt):
        # Update collision box position
        self.rect.topleft = self.position
        if self.action['attack']:
            self.cooldown -= dt
            if self.cooldown < 0:
                self.action['attack'] = False
                self.cooldown = self.maxcd
        else: self.cooldown = self.maxcd

        if self.stats.hp <= 0:
            self.kill()

        self.action.update(dt)
        self.stats.update(dt)

    def isColliding(self, x, y):
        # Takes offset x,y and sees if sprite is colliding with any objects in fov
        offset = self.getLegBox()
        offset.topleft = (offset.topleft[0] + x,offset.topleft[1] + y)
        collide = False
        for obj in self.fov:
            if offset.colliderect(obj.rect) and obj.collidable:
                collide = True
        return collide

    class Actions:
        # Handles all the mob actions here
        def __init__(self,mob,images):
            self.mob = mob
            self.current = 'idle_down'
            self.actions = {
                'attack':False,
                'walk': False,
            }
            self.direction = 'left'
            self.images = images

        def __getitem__(self, item):
            return self.actions[item]

        def __setitem__(self, key, value):
            self.actions[key] = value

        def attack(self,target):
            self.actions['attack'] = True
            self.mob.stats.damage(target)

        def move(self, x, y):
            # Moves sprite if not colliding
            if not self.mob.isColliding(x, y):
                self.mob.position[0] += x
                self.mob.position[1] += y

        def update(self,dt):
            if self.actions['walk']:
                self.current = 'walk_%s' % self.direction
            elif self.actions['attack']:
                self.current = 'attack_%s' % self.direction
            else:
                self.current = 'idle_%s' % self.direction

            self.images[self.current].update(dt)

        def draw(self):
            self.mob.image = self.images[self.current].currentFrame()

    class Stats:
        # Handle all of mob stats here
        def __init__(self,health,ad):
            self.movement_speed = 0
            self.maxHP = health
            self.hp = health
            self.ad = ad
            self.defence = 12
            self.statQueue = []

        def damage(self,target):
            target.stats.hurt(self.ad)
            self.statQueue.append(particles.BouncyText(self,self.ad,[target.rect.centerx,target.rect.top - 16]))

        def hurt(self,value):
            self.hp -= value

        def update(self,dt):
            self.movement_speed = 0.3 * dt
            for item in self.statQueue:
                item.update(dt)

        def draw(self,surface,camera):
            for i in self.statQueue:
                i.draw(surface,camera)
class Goblin(Mob):
    name = 'Goblin'
    def __init__(self,pos):
        size = (64,64)
        sheet = sprite.Spritesheet('mobsheet.png')
        states = {
            'idle_up': sprite.AnimatedSprite(sheet, [(1, 1)], [16, 16], size, 800),
            'idle_left': sprite.AnimatedSprite(sheet, [(0,0),(1,0)], [16, 16], size, 800),
            'idle_down': sprite.AnimatedSprite(sheet, [(0, 1)], [16, 16], size, 800),
            'idle_right': sprite.AnimatedSprite(sheet, [(2, 0),(3,0)], [16, 16], size, 800),
            'walk_up':sprite.AnimatedSprite(sheet, [(1, 1)], [16, 16],size,200),
            'walk_left':sprite.AnimatedSprite(sheet, [(0, 0)], [16, 16],size,200),
            'walk_down':sprite.AnimatedSprite(sheet, [(0, 1)], [16, 16],size,200),
            'walk_right':sprite.AnimatedSprite(sheet, [(1, 0)], [16, 16],size,200),
            'attack_up':sprite.AnimatedSprite(sheet, [(6, 1), (7, 1)], [16, 16],size,500),
            'attack_left':sprite.AnimatedSprite(sheet, [(4, 0), (5, 0)], [16, 16],size,500),
            'attack_down':sprite.AnimatedSprite(sheet, [(4, 1), (5, 1)], [16, 16],size,500),
            'attack_right':sprite.AnimatedSprite(sheet, [(6, 0), (7, 0)], [16, 16],size,500)
        }
        super().__init__(states,size,pos,25,8)
        self.maxcd = 1000
        self.cooldown = 1000

    def update(self,dt):
        super().update(dt)
        for obj in self.fov:
            if isinstance(obj,Player) and self.getAttackRange(self.action.direction).colliderect(obj):
                if not self.action['attack']:
                    self.action.attack(obj)


class Skeleton(Mob):
    name = 'Skeleton'
    def __init__(self,pos):
        size = (64,128)
        sheet = sprite.Spritesheet('mobsheet.png')
        states = {
            'idle_up': sprite.AnimatedSprite(sheet, [(0,1), (1,1)], [16, 32], size, 800),
            'idle_left': sprite.AnimatedSprite(sheet, [(0,1), (1,1)], [16, 32], size, 800),
            'idle_down': sprite.AnimatedSprite(sheet, [(0,1), (1,1)], [16, 32], size, 800),
            'idle_right': sprite.AnimatedSprite(sheet, [(2,1), (3,1)], [16, 32], size, 800),
            'attack_up': sprite.AnimatedSprite(sheet, [(0,1), (1,1)], [16, 32], size, 1000),
            'attack_left': sprite.AnimatedSprite(sheet, [(0,1), (1,1)], [16, 32], size, 1000),
            'attack_down': sprite.AnimatedSprite(sheet, [(0,1), (1,1)], [16, 32], size, 1000),
            'attack_right': sprite.AnimatedSprite(sheet, [(2,1), (3,1)], [16, 32], size, 1000)

        }
        super().__init__(states,size,pos,30,10)
        self.maxcd = 1000
        self.cooldown = 1000

    def update(self,dt):
        super().update(dt)
        for obj in self.fov:
            if isinstance(obj,Player) and self.getAttackRange(self.action.direction).colliderect(obj):
                if not self.action['attack']:
                    self.action.attack(obj)


class Player(Mob):
    # TODO: Create a player and place it on the map
    def __init__(self,pos):
        size = (64,96)
        sheet = sprite.Spritesheet('playersheet.png')
        states = {
            'idle_up': sprite.AnimatedSprite(sheet, [(1, 0)], [16, 24], size, 200),
            'idle_left': sprite.AnimatedSprite(sheet, [(0, 1)], [16, 24], size, 200),
            'idle_down': sprite.AnimatedSprite(sheet, [(0, 0)], [16, 24], size, 200),
            'idle_right': sprite.AnimatedSprite(sheet, [(1, 1)], [16, 24], size, 200),
            'walk_up':sprite.AnimatedSprite(sheet, [(1, 0), (6, 0), (7, 0)], [16, 24],size,200),
            'walk_left':sprite.AnimatedSprite(sheet, [(0, 1), (4, 1), (5, 1)], [16, 24],size,200),
            'walk_down':sprite.AnimatedSprite(sheet, [(0, 0), (4, 0), (5, 0)], [16, 24],size,200),
            'walk_right':sprite.AnimatedSprite(sheet, [(1, 1), (6, 1), (7, 1)], [16, 24],size,200),
            'attack_up':sprite.AnimatedSprite(sheet, [(10, 0), (11, 0)], [16, 24],size,200),
            'attack_left':sprite.AnimatedSprite(sheet, [(8, 1), (9, 1)], [16, 24],size,200),
            'attack_down':sprite.AnimatedSprite(sheet, [(8, 0), (9, 0)], [16, 24],size,200),
            'attack_right':sprite.AnimatedSprite(sheet, [(10, 1), (11, 1)], [16, 24],size,200)
                       }

        super().__init__(states, size, pos, 100, 9)
        self.inventory = Inventory(self,10)

    def update(self,dt):
        super().update(dt)

    def draw(self,surface,camera):
        super().draw(surface,camera)
        for obj in self.fov:
            camera.drawRectangle(surface,pg.Color('green'),obj.rect)

    def getPosition(self):
        return self.position

    def getSize(self):
        return self.size

    def attack(self):
        self.action['attack'] = True
        for obj in self.fov:
            if self.getAttackRange(self.action.direction).colliderect(obj) and isinstance(obj,Mob):
                self.stats.damage(obj)



