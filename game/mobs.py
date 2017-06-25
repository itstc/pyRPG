import pygame as pg
import sprite,particles,settings,projectiles,math
from inventory import Inventory



class Mob(pg.sprite.Sprite):
    sprite_size = [16,16]
    collidable = True
    type = 'mob'

    def __init__(self,group,images,size,position,health,ad):
        super().__init__()
        self.image = pg.Surface(size)

        self.size = size
        self.position = list(position)
        self.rect = pg.Rect(position[0],position[1],size[0],size[1])

        self.fov = []
        self.maxcd = 45
        self.cooldown = self.maxcd

        self.action = Mob.Actions(self,images)
        self.stats = Mob.Stats(self,health,ad)

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

    def getHealthRatio(self):
        return self.stats.hp/self.stats.maxHP

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
        else:
            self.cooldown = self.maxcd

        self.stats.update(dt)
        self.action.update(dt)

        if self.stats.hp <= 0:
            self.kill()

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

            self.colliding = False

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

    class Stats:
        # Handle all of mob stats here
        MAX_SPEED = 0.4
        def __init__(self,mob,health,ad):
            self.mob = mob
            self.maxHP = health
            self.hp = health
            self.ad = ad
            self.defence = 12
            self.statQueue = []


        def damage(self,target):
            target.stats.hurt(self.ad)
            self.statQueue.append(particles.BouncyText(self,self.ad,[target.rect.centerx,target.rect.top - 18 * len(target.stats.statQueue)]))

        def hurt(self,value):
            self.hp -= value

        def update(self,dt):
            for (i,item) in enumerate(self.statQueue):
                item.update(dt)

        def draw(self,surface,camera):
            for i in self.statQueue:
                i.draw(surface,camera)

class Player(Mob):
    # TODO: Create a player and place it on the map
    def __init__(self, group, pos):
        # Initialize Images for player
        size = (64,64)
        sheet = sprite.Spritesheet(settings.PLAYERSHEET)
        states = {
            # Animated Sprite will be called by syntax: action_direction
            'idle_left': sprite.AnimatedSprite(sheet, [(0, 0)], [16,16], size, 12),
            'idle_right': sprite.AnimatedSprite(sheet, [(0, 1)], [16,16], size, 12),
            'walk_left':sprite.AnimatedSprite(sheet, [(0, 0), (1, 0), (2, 0), (3, 0)], [16,16],size,12),
            'walk_right':sprite.AnimatedSprite(sheet, [(0, 1), (1, 1), (2, 1), (3, 1)], [16,16],size,12),
            'attack_left':sprite.AnimatedSprite(sheet, [(0, 0), (4, 0), (5, 0)], [16,16],size, 15),
            'attack_right':sprite.AnimatedSprite(sheet, [(1, 1), (4, 1), (5, 1)], [16,16],size, 15)
                       }

        super().__init__(group, states, size, pos, 100, 10)
        self.inventory = Inventory(self,12)
        self.input = input
        self.stats = Player.PlayerStats(self, 100, 10)
        self.action = Player.PlayerActions(self,states)
        self.interactable = None

        self.camera_pos = (0,0)

    def update(self,dt):
        super().update(dt)

        self.interactable = [obj for obj in self.fov if obj.type == 'world' and self.rect.colliderect(obj.rect)]

    def draw(self,surface,camera):
        super().draw(surface,camera)

        self.camera_pos = camera.applyOnPosition(self.rect.center)



    def getPosition(self):
        return self.position

    def getSize(self):
        return self.size

    class PlayerStats(Mob.Stats):
        def __init__(self, player, health, ad):
            super().__init__(player, health, ad)

            self.equipment = {
                'head': None,
                'body': None,
                'leg': None,
                'weapon': None
            }

        def unequipItem(self, slot):
            if self.equipment[slot]:
                self.equipment[slot].unequip(self.mob)
                self.mob.inventory.addItem(self.equipment[slot])
                self.equipment[slot] = None

        def draw(self,surface,camera):
            super().draw(surface, camera)

            if self.equipment['head']:
                head_sprite = self.equipment['head'].sprite[self.mob.action.current].getFrame(self.mob.action.currentFrame)
                surface.blit(head_sprite, camera.applyOnRect(self.mob.rect))

            if self.equipment['body']:
                body_sprite = self.equipment['body'].sprite[self.mob.action.current].getFrame(self.mob.action.currentFrame)
                surface.blit(body_sprite, camera.applyOnRect(self.mob.rect))

            if self.equipment['leg']:
                leg_sprite = self.equipment['leg'].sprite[self.mob.action.current].getFrame(self.mob.action.currentFrame)
                surface.blit(leg_sprite, camera.applyOnRect(self.mob.rect))

            if self.equipment['weapon']:
                weapon_sprite = self.equipment['weapon'].sprite[self.mob.action.current].getFrame(self.mob.action.currentFrame)
                surface.blit(weapon_sprite, camera.applyOnRect(self.mob.rect))

    class PlayerActions(Mob.Actions):
        def __init__(self,mob,images):
            super().__init__(mob,images)

        def keyMove(self, dt):
            ax = 0
            ay = 0
            ac = 3

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

        def attack(self):
            self.actions['attack'] = True
            self.images['attack_%s' % self.direction].reset()

        def fire(self, pos):
            dx = pos[0] - self.mob.camera_pos[0]
            dy = pos[1] - self.mob.camera_pos[1]
            angle = math.atan2(dy, dx)
            self.mob.group.add(projectiles.Arrow(self.mob, angle, self.mob.rect.center))