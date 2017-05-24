import pygame as pg
import sprite,particles
from inventory import Inventory



class Mob(pg.sprite.Sprite):
    sprite_size = [16,16]
    collidable = True
    def __init__(self,images,size,position,health,ad):
        super().__init__()
        self.images = images
        self.image = pg.Surface(size)

        self.size = size
        self.position = position
        self.rect = pg.Rect(position,[size[0]//2,size[1]])
        self.rect.center = self.position

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
        legBox = pg.Rect(self.position[0]-self.size[0]//4, self.position[1],self.size[0]//2, self.size[1]//2)
        return legBox

    def draw(self,surface,camera, offset):
        self.action.draw()

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
        offset.center = [offset.center[0] + x, offset.center[1] + y]
        collide = False
        for i in self.fov:
            if offset.colliderect(i.rect) and i.collidable:
                collide = True
        return collide

    class Actions:
        def __init__(self,mob,states):
            self.mob = mob
            self.states = states
            self.current = 'idle_down'
            self.actions = {
                'attack':False,
                'walk': False,
            }
            self.direction = 'left'

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
                self.mob.position = [self.mob.position[0] + x, self.mob.position[1] + y]

        def update(self,dt):
            if self.actions['walk']:
                self.current = 'walk_%s' % self.direction
            elif self.actions['attack']:
                #self.current = 'attack_%s' % self.direction
                pass
            else:
                self.current = 'idle_%s' % self.direction

            self.states[self.current].update(dt)

        def draw(self):
            self.mob.image = self.states[self.current].currentFrame()

    class Stats:
        def __init__(self,health,ad):
            self.maxHP = health
            self.hp = health
            self.ad = ad
            self.defence = 12
            self.statQueue = []

        def damage(self,target):
            target.stats.hurt(self.ad)
            target.stats.statQueue.append(particles.BouncyText(target.stats,self.ad,[target.rect.centerx,target.rect.top - 8]))

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
        size = (64,64)
        states = {
            'idle_up': sprite.AnimatedSprite(sprite.Spritesheet('mobsheet.png'), [(0, 0), (1, 0)], [16, 16], size, 800),
            'idle_left': sprite.AnimatedSprite(sprite.Spritesheet('mobsheet.png'), [(0, 0), (1, 0)], [16, 16], size, 800),
            'idle_down': sprite.AnimatedSprite(sprite.Spritesheet('mobsheet.png'), [(0, 0), (1, 0)], [16, 16], size, 800),
            'idle_right': sprite.AnimatedSprite(sprite.Spritesheet('mobsheet.png'), [(0, 0), (1, 0)], [16, 16], size, 800)
        }
        super().__init__(states,size,(x,y),25,8)
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
    def __init__(self,x,y):
        size = (64,128)
        states = {
            'idle_up': sprite.AnimatedSprite(sprite.Spritesheet('mobsheet.png'), [(2, 0), (3, 0)], [16, 32], size, 800),
            'idle_left': sprite.AnimatedSprite(sprite.Spritesheet('mobsheet.png'), [(2, 0), (3, 0)], [16, 32], size, 800),
            'idle_down': sprite.AnimatedSprite(sprite.Spritesheet('mobsheet.png'), [(2, 0), (3, 0)], [16, 32], size, 800),
            'idle_right': sprite.AnimatedSprite(sprite.Spritesheet('mobsheet.png'), [(2, 0), (3, 0)], [16, 32], size, 800)

        }
        super().__init__(states,size,(x,y),30,10)


class Player(Mob):
    # TODO: Create a player and place it on the map
    def __init__(self,x,y):
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

        super().__init__(states, size, (x,y),100,9)
        self.stats.hp = 50
        self.isWalking = False
        self.inventory = Inventory(self,10)

    def update(self,dt):
        super().update(dt)

    def getPosition(self):
        return self.position

    def getSize(self):
        return self.size

    def move(self,x,y):
        if not self.isColliding(x,y):
            self.position = (self.position[0] + x, self.position[1] + y)

    def attack(self):
        self.action['attack'] = True
        for obj in self.fov:
            if self.getAttackRange(self.action.direction).colliderect(obj) and isinstance(obj,Mob):
                self.stats.damage(obj)
