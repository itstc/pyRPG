from math import atan2

from game.settings import PLAYERSHEET
from .projectiles import Arrow
from .particles import CritText
from .mobs import Mob
from sprite.sprite import Spritesheet, AnimatedSprite
from item.inventory import Inventory

class Player(Mob):
    # TODO: Create a player and place it on the map
    def __init__(self, group, pos):
        # Initialize Images for player
        size = (64,64)
        sheet = Spritesheet(PLAYERSHEET)
        states = {
            # Animated Sprite will be called by syntax: action_direction
            'idle_left': AnimatedSprite(sheet, [(0, 0)], [16, 16], size, 12),
            'idle_right': AnimatedSprite(sheet, [(0, 1)], [16, 16], size, 12),
            'walk_left': AnimatedSprite(sheet, [(0, 0), (1, 0), (2, 0), (3, 0)], [16, 16], size, 12),
            'walk_right': AnimatedSprite(sheet, [(0, 1), (1, 1), (2, 1), (3, 1)], [16, 16], size, 12),
            'attack_left': AnimatedSprite(sheet, [(0, 0), (4, 0), (5, 0)], [16, 16], size, 15),
            'attack_right': AnimatedSprite(sheet, [(0, 1), (4, 1), (5, 1)], [16, 16], size, 15)
       }

        super().__init__(group, states, size, pos, 100, 2)
        self.inventory = Inventory(self,12)
        self.input = input
        self.stats = Player.PlayerStats(self, 100, 2)
        self.action = Player.PlayerActions(self,states)
        self.interactable = None

        self.camera_pos = (0,0)

    def addActivity(self, activity, extra=None):
        super().addActivity(activity, extra)
        if activity == 'FIRE' and not self.action['fire']:
            self.action['fire'] = True
            self.activeQueue.append((self.action.fire, extra))

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
            self.crit = 15

        def unequipItem(self, slot):
            if self.equipment[slot]:
                self.equipment[slot].unequip(self.mob)
                self.mob.inventory.addItem(self.equipment[slot])
                self.equipment[slot] = None

        def shakeOnCrit(self, surface, camera, i):
            if isinstance(i, CritText):
                camera.shake(1, self.mob.action.direction)

        def draw(self,surface,camera):
            super().draw(surface, camera, self.shakeOnCrit)

            # Draw Equipment on Player Here
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
            self.actions['fire'] = False

        def keyMove(self, dt):
            ax = 0
            ay = 0
            ac = 2

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
            self.actions['fire'] = False
            dx = pos[0] - self.mob.camera_pos[0]
            dy = pos[1] - self.mob.camera_pos[1]
            angle = atan2(dy, dx)
            self.mob.group.add(Arrow(self.mob, angle, self.mob.rect.center))
