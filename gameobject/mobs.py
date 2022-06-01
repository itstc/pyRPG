import pygame as pg
import random
import math
from util.util import lerp
from .particles import BouncyText, CritText

class Mob(pg.sprite.Sprite):
    sprite_size = [16,16]
    collidable = True
    type = 'gameobject'

    def __init__(self,group,images,size,position,health,ad):
        super().__init__()
        self.image = pg.Surface(size)

        self.size = size
        self.position = list(position)
        self.rect = pg.Rect(position[0],position[1],size[0],size[1])

        self.fov = []

        self.targetPos = (0,0)

        self.action = Mob.Actions(self,images)
        self.stats = Mob.Stats(self,health,ad)
        self.activeQueue = []

        self.group = group

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
            'right': pg.Rect(tlPos[0] + self.size[0] // 2, tlPos[1] - self.size[1] // 4,
                            self.size[0], self.size[1] + self.size[1] // 2),
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
        cd_bar = pg.Rect(self.rect.left, self.rect.top - 32, max(0,int(bar_width * (self.stats.cooldown / self.stats.maxcd))), 8)

        pg.draw.rect(surface, pg.Color('red'),camera.applyOnRect(red_bar))
        pg.draw.rect(surface, pg.Color('green'),camera.applyOnRect(green_bar))

        pg.draw.rect(surface, pg.Color('blue'),camera.applyOnRect(cd_bar))

    def getHealthRatio(self):
        return self.stats.hp/self.stats.maxHP

    def draw(self,surface,camera):
        self.action.draw(surface,camera)

        # Draw Health Bar
        self.drawHealthBar(surface,camera)

        # Draws collision box
        # camera.drawRectangle(surface, pg.Color('purple'), self.getLegBox())
        # camera.drawRectangle(surface,pg.Color('purple'),self.getAttackRange(self.action.direction))

        self.stats.draw(surface,camera)

    def update(self,dt):
        # Update collision box position
        self.rect.topleft = self.position

        self.stats.cooldown -= dt
        if self.stats.cooldown < 0:
            if self.activeQueue:
                cb, extra = self.activeQueue.pop()
                if cb:
                    cb(extra)
            self.stats.cooldown = self.stats.maxcd

        self.stats.update(dt)
        self.action.update(dt)


        if self.stats.hp <= 0:
            self.kill()

    def addActivity(self, activity, extra=None):
        if activity == 'ATTACK':
            self.action.attack()
            self.activeQueue.append((self.onAttackEnd, extra))
    
    def onAttackEnd(self, extra=None):
        for obj in self.fov:
            if self.getAttackRange(self.action.direction).colliderect(obj) and isinstance(obj, Mob):
                self.stats.damage(obj)
                obj.targetPos = obj.knockback(1, self)
        self.action['attack'] = False

    def isColliding(self, x, y):
        # Takes offset x,y and sees if sprite is colliding with any objects in fov
        offset = self.getLegBox()
        offset.topleft = (offset.topleft[0] + x,offset.topleft[1] + y)
        collide = False
        for obj in self.fov:
            collideBox = obj.rect
            if obj.type == 'gameobject':
                collideBox = obj.getLegBox()

            if offset.colliderect(collideBox) and obj.collidable:
                collide = True

        return collide

    def knockback(self, impact, obj):
        #self.action['knockback'] = True
        angle = math.atan2(self.position[1] - obj.position[1], self.position[0] - obj.position[0])
        fx = math.cos(angle) * impact
        fy = math.sin(angle) * impact
        return (fx, fy)


    class Actions:
        # Handles all the gameobject actions here
        def __init__(self,mob,images):
            self.mob = mob
            self.current = 'idle_right'
            self.actions = {
                'attack':False,
                'walk': False,
                'knockback': False,
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

            self.colliding = False
            self.actionQueue = []

        def __getitem__(self, item):
            return self.actions[item]

        def __setitem__(self, key, value):
            self.actions[key] = value

        def attack(self):
            self.actions['attack'] = True

        def move(self, x, y):
            if x != 0 and y != 0:
                self.move(x,0)
                self.move(0,y)
                return

            # Moves sprite if not colliding
            if not self.mob.isColliding(x, y):
                self.actions['walk'] = True
                self.colliding = False
                self.mob.position[0] += x
                self.mob.position[1] += y
            else:
                self.colliding = True

        def update(self,dt):
            if self.actions['walk']:
                self.current = 'walk_%s' % self.direction
            elif self.actions['attack']:
                self.current = 'attack_%s' % self.direction
            else:
                self.current = 'idle_%s' % self.direction
                self.mob.stats.current_speed = 0

            self.images[self.current].update(dt)
            self.currentFrame = self.images[self.current].frame

        def draw(self,surface,camera):
            self.mob.image = self.images[self.current].currentFrame()

        def getWeaponLocation(self,frame):
            offset = self.weaponLocation[self.direction][frame]
            rect = self.mob.rect.topleft
            if self.direction == 'right':
                rect = self.mob.rect.topright
            return (rect[0] + offset[0], rect[1] + offset[1])

        def clearActions(self):
            for k in self.actions.keys():
                self.actions[k] = False

    class Stats:
        # Handle all of gameobject stats here
        MAX_SPEED = 0.4
        def __init__(self,mob,health,ad):
            self.mob = mob
            self.maxHP = health
            self.hp = health
            self.ad = ad
            self.defence = 15
            self.maxcd = 60
            self.crit = 15
            self.cooldown = self.maxcd
            self.statQueue = []


        def damage(self,target):
            modifier = None
            dmg = self.ad
            critProc = random.randint(1,100)
            if critProc <= self.crit:
                modifier = "crit"
                dmg = self.ad*2

            target.stats.hurt(dmg, modifier)

        def hurt(self, value, modifier=None):
            defenceRating = math.log(10 + random.random() * (self.defence / (value + 1)))
            finalDamage = max(math.floor(value - defenceRating), 0)
            self.hp -= finalDamage
            if modifier == "crit":
                self.statQueue.append(CritText(self,finalDamage,[self.mob.rect.centerx, self.mob.rect.top - 20 * len(self.statQueue)]))
            else:
                self.statQueue.append(BouncyText(self,finalDamage,[self.mob.rect.centerx, self.mob.rect.top - 20 * len(self.statQueue)]))

        def update(self,dt):
            for (i,item) in enumerate(self.statQueue):
                item.update(dt)

        def draw(self,surface,camera,statFn=None):
            for i in self.statQueue:
                i.draw(surface,camera)
                if statFn:
                    statFn(surface, camera, i)
