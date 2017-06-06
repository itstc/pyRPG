import pygame as pg
import sprite,particles,settings
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
        self.stats = Mob.Stats(self,health,ad)

    def setPosition(self,pos):
        self.position = list(pos)

    def getAttackRange(self,direction):
        tlPos = self.rect.topleft
        range = {
            'up': pg.Rect(tlPos[0] - self.size[0] // 2, tlPos[1] , self.size[0] // 2 * 3,
                           self.size[1] // 4),
            'left': pg.Rect(tlPos[0] - self.size[0] // 2, tlPos[1] - self.size[1] // 4,
                            self.size[0], self.size[1] + self.size[1] // 2),
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
        green_bar = pg.Rect(self.rect.left, self.rect.top - 16, max(0,int(bar_width * (self.stats.hp / self.stats.maxHP))), 8)

        pg.draw.rect(surface, pg.Color('red'),camera.applyOnRect(red_bar))
        pg.draw.rect(surface, pg.Color('green'),camera.applyOnRect(green_bar))

    def draw(self,surface,camera):
        self.action.draw(surface,camera)

        # Draw Health Bar
        self.drawHealthBar(surface,camera)

        # Draws collision box
        #camera.drawRectangle(surface, pg.Color('purple'), self.getLegBox())
        #camera.drawRectangle(surface,pg.Color('purple'),self.getAttackRange('left'))

        self.stats.draw(surface,camera)

    def update(self,dt):
        # Update collision box position
        self.rect.topleft = self.position
        if self.action['attack']:
            self.cooldown -= dt
            if self.cooldown < 0:
                for obj in self.fov:
                    if self.getAttackRange(self.action.direction).colliderect(obj) and isinstance(obj, Mob):
                        self.stats.damage(obj)
                self.action['attack'] = False
                self.cooldown = self.maxcd
        else: self.cooldown = self.maxcd

        if self.stats.hp <= 0:
            self.kill()

        self.stats.update(dt)
        self.action.update(dt)

    def isColliding(self, x, y):
        # Takes offset x,y and sees if sprite is colliding with any objects in fov
        offset = self.getLegBox()
        offset.topleft = (offset.topleft[0] + x,offset.topleft[1] + y)
        collide = False
        for obj in self.fov:
            collideBox = obj.rect
            if obj.type == 'mob':
                collideBox = obj.getLegBox()
            if offset.colliderect(collideBox) and obj.collidable:
                if isinstance(self,Player) and obj.type == 'world':
                    self.position = [0,0]
                    obj.onCollide()
                collide = True
        return collide

    class Actions:
        # Handles all the mob actions here
        def __init__(self,mob,images):
            self.mob = mob
            self.current = 'idle_right'
            self.actions = {
                'attack':False,
                'walk': False,
            }
            self.direction = 'left'
            self.moveDirections = {
                'up': False,
                'left': False,
                'down': False,
                'right': False
            }
            self.images = images
            self.weaponLocation = {
                'left':[(-44, 0),
                        (-44, 0),
                        (-12, 0)],
                'right':[(-20, 0),
                         (-20, 0),
                         (-48, 0)]
            }

        def __getitem__(self, item):
            return self.actions[item]

        def __setitem__(self, key, value):
            self.actions[key] = value

        def attack(self,target):
            self.actions['attack'] = True

        def move(self, x, y):
            if x != 0 and y != 0:
                self.move(x,0)
                self.move(0,y)
                return

            # Moves sprite if not colliding
            if not self.mob.isColliding(x, y):
                self.mob.position[0] += x
                self.mob.position[1] += y

        def update(self,dt):
            if self.actions['walk']:
                self.current = 'walk_%s' % self.direction
            elif self.actions['attack']:
                self.current = 'attack_%s' % self.direction
                if isinstance(self.mob,Player):
                    self.images['slash_%s' % self.direction].update(dt)
            else:
                self.current = 'idle_%s' % self.direction
                self.mob.stats.current_speed = 0

            self.images[self.current].update(dt)

        def draw(self,surface,camera):
            self.mob.image = self.images[self.current].currentFrame()
            if isinstance(self.mob,Player) and self.actions['attack']:
                weapon = self.images['slash_%s' % self.direction]
                surface.blit(weapon.currentFrame(),
                             camera.applyOnPosition(self.getWeaponLocation(weapon.frame)))

        def getWeaponLocation(self,frame):
            offset = self.weaponLocation[self.direction][frame]
            rect = self.mob.rect.topleft
            if self.direction == 'right':
                rect = self.mob.rect.topright
            return (rect[0] + offset[0], rect[1] + offset[1])

    class Stats:
        # Handle all of mob stats here
        MAX_SPEED = 0.4
        def __init__(self,mob,health,ad):
            self.movement_speed = 0
            self.velocity = 0
            self.mob = mob
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
            for item in self.statQueue:
                item.update(dt)

        def draw(self,surface,camera):
            for i in self.statQueue:
                i.draw(surface,camera)
class Goblin(Mob):
    name = 'Goblin'
    def __init__(self,pos):
        size = (64,64)
        sheet = sprite.Spritesheet(settings.MOBSHEET)
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
        sheet = sprite.Spritesheet(settings.MOBSHEET)
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
        # Initialize Images for player
        size = (64,96)
        sheet = sprite.Spritesheet(settings.PLAYERSHEET)
        attack = sprite.Spritesheet(settings.ATTACKSHEET)
        states = {
            # Animated Sprite will be called by syntax: action_direction
            'idle_left': sprite.AnimatedSprite(sheet, [(0, 0)], [16,24], size, 200),
            'idle_right': sprite.AnimatedSprite(sheet, [(1, 0)], [16,24], size, 200),
            'walk_left':sprite.AnimatedSprite(sheet, [(0, 0), (4, 0), (5, 0)], [16,24],size,200),
            'walk_right':sprite.AnimatedSprite(sheet, [(1, 0), (6, 0), (7, 0)], [16,24],size,200),
            'attack_left':sprite.AnimatedSprite(sheet, [(0,0)], [16,24],size,200),
            'attack_right':sprite.AnimatedSprite(sheet, [(1,0)], [16,24],size,200),
            'slash_left':sprite.AnimatedSprite(attack, [(3,0), (4,0), (5,0)], [16,16],[64,64],200),
            'slash_right': sprite.AnimatedSprite(attack, [(0,0), (1,0), (2,0)], [16,16],[64,64],200)
                       }

        super().__init__(states, size, pos, 100, 9)
        self.inventory = Inventory(self,12)
        self.input = input
        self.action = Player.PlayerActions(self,states)

    def update(self,dt):
        super().update(dt)

    def draw(self,surface,camera):
        super().draw(surface,camera)

    def getPosition(self):
        return self.position

    def getSize(self):
        return self.size

    def attack(self):
        self.action['attack'] = True
        self.action.images['slash_%s' % self.action.direction].reset()


    class PlayerActions(Mob.Actions):
        def __init__(self,mob,images):
            super().__init__(mob,images)

        def keyMove(self, dt):
            ax = 0
            ay = 0
            ac = 0.02

            if self.moveDirections['up']:
                ay -= ac
            if self.moveDirections['left']:
                ax -= ac
            if self.moveDirections['down']:
                ay += ac
            if self.moveDirections['right']:
                ax += ac

            moveX = int(ax * dt**2)
            moveY = int(ay * dt**2)
            if moveX != 0 or moveY != 0:
                self.move(moveX,moveY)

        def update(self,dt):
            super().update(dt)
            self.keyMove(dt)


