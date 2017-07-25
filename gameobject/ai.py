import random

from game.settings import MOBSHEET
from sprite.sprite import AnimatedSprite, Spritesheet
from .mobs import Mob
from .player import Player


class AI(Mob):

    def __init__(self, group, images, size, position, health, ad):
        super().__init__(group, images, size, position, health, ad)

        self.ai_states = {
            'Wander': Wander().execute
        }
        self.current_ai_state = self.ai_states['Wander']

    def update(self, dt):
        super().update(dt)

        self.current_ai_state(dt, self.action)

        for obj in self.fov:
            if isinstance(obj, Player) and self.getAttackRange(self.action.direction).colliderect(obj):
                if not self.action['attack']:
                    self.action['walk'] = False
                    self.action.attack(obj)



class AI_State():
    def __init__(self):
        self.ai_direction = None
        self.ai_move_time = 60
        self.next_move = self.ai_move_time

class Wander(AI_State):
    def __init__(self):
        super().__init__()

        self.options = ['move','stay']
        self.current_option = 'stay'

    def execute(self, dt, action):
        self.next_move -= dt

        # every ai_move_time (ms) passes the ai will make a decision
        if self.next_move <= 0:

            if not self.ai_direction or action.colliding or random.randrange(100) >= 60:
                self.ai_direction = random.choice(['up','left','down','right'])

            self.current_option = random.choice(self.options)

            self.next_move = self.ai_move_time

        move_speed = 1 * dt**2

        # Check if ai wants to move
        if self.current_option == 'move':
            if self.ai_direction == 'up':
                action.move(0, -move_speed)
            elif self.ai_direction == 'left':
                action.direction = 'left'
                action.move(-move_speed, 0)
            elif self.ai_direction == 'down':
                action.move(0, move_speed)
            elif self.ai_direction == 'right':
                action.direction = 'right'
                action.move(move_speed, 0)




class Goblin(AI):
    name = 'Goblin'
    def __init__(self,group, pos):
        size = (64,64)
        sheet = Spritesheet(MOBSHEET)
        states = {
            'idle_left': AnimatedSprite(sheet, [(0, 0)], [16, 16], size, 30),
            'idle_right': AnimatedSprite(sheet, [(0, 1)], [16, 16], size, 30),
            'walk_left':AnimatedSprite(sheet, [(0, 0), (1, 0), (2, 0), (3, 0)], [16, 16],size,30),
            'walk_right':AnimatedSprite(sheet, [(0, 1), (1, 1), (2, 1), (3, 1)], [16, 16],size,30),
            'attack_left':AnimatedSprite(sheet, [(4, 0), (5, 0), (6, 0)], [16, 16],size,30),
            'attack_right':AnimatedSprite(sheet, [(4, 1), (5, 1), (6, 1)], [16, 16],size,30)
        }

        super().__init__(group, states, size, pos, 25, 8)
        self.maxcd = 90
        self.cooldown = 90

    def update(self,dt):
        super().update(dt)


class Skeleton(AI):
    name = 'Skeleton'
    def __init__(self, group, pos):
        size = (64,128)
        sheet = Spritesheet(MOBSHEET)
        states = {
            'idle_left': AnimatedSprite(sheet, [(0,1), (1,1)], [16, 32], size, 30),
            'idle_right': AnimatedSprite(sheet, [(2,1), (3,1)], [16, 32], size, 30),
            'walk_left': AnimatedSprite(sheet, [(0, 1), (1, 1)], [16, 32], size, 60),
            'walk_right': AnimatedSprite(sheet, [(2, 1), (3, 1)], [16, 32], size, 60),
            'attack_left': AnimatedSprite(sheet, [(0,1), (1,1)], [16, 32], size, 60),
            'attack_right': AnimatedSprite(sheet, [(2,1), (3,1)], [16, 32], size, 60)
        }

        super().__init__(group, states, size, pos, 30, 10)
        self.maxcd = 90
        self.cooldown = 90

    def update(self,dt):
        super().update(dt)

class Barbarian(AI):
    name = 'Barbarian'
    def __init__(self, group, pos):
        size = (64,64)
        sheet = Spritesheet(MOBSHEET)
        states = {
            'idle_left': AnimatedSprite(sheet, [(0, 4)], [16, 16], size, 30),
            'idle_right': AnimatedSprite(sheet, [(0, 5)], [16, 16], size, 30),
            'walk_left':AnimatedSprite(sheet, [(0, 4), (1, 4), (2, 4), (3, 4)], [16, 16],size,30),
            'walk_right':AnimatedSprite(sheet, [(0, 5), (1, 5), (2, 5), (3, 5)], [16, 16],size,30),
            'attack_left':AnimatedSprite(sheet, [(4, 4), (5, 4), (6, 4)], [16, 16],size,15),
            'attack_right':AnimatedSprite(sheet, [(4, 5), (5, 5), (6, 5)], [16, 16],size,15)
        }

        super().__init__(group, states, size, pos, 45, 8)
        self.maxcd = 45
        self.cooldown = 45

    def update(self,dt):
        super().update(dt)

class Bear(AI):
    name = 'Bear'
    def __init__(self, group, pos):
        size = (64,64)
        sheet = Spritesheet(MOBSHEET)
        states = {
            'idle_left': AnimatedSprite(sheet, [(0, 6)], [16, 16], size, 30),
            'idle_right': AnimatedSprite(sheet, [(0, 7)], [16, 16], size, 30),
            'walk_left':AnimatedSprite(sheet, [(0, 6), (1, 6), (2, 6), (3, 6)], [16, 16],size,30),
            'walk_right':AnimatedSprite(sheet, [(0, 7), (1, 7), (2, 7), (3, 7)], [16, 16],size,30),
            'attack_left':AnimatedSprite(sheet, [(4, 6), (5, 6), (6, 6)], [16, 16],size,40),
            'attack_right':AnimatedSprite(sheet, [(4, 7), (5, 7), (6, 7)], [16, 16],size,40)
        }

        super().__init__(group, states, size, pos, 100, 15)
        self.maxcd = 120
        self.cooldown = 120

    def update(self,dt):
        super().update(dt)


