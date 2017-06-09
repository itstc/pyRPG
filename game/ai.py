import mobs, sprite, settings, random

class AI(mobs.Mob):

    def __init__(self, images, size, position, health, ad):
        super().__init__(images, size, position, health, ad)

        self.ai_states = {
            'Wander': Wander().execute
        }
        self.current_ai_state = self.ai_states['Wander']

    def update(self, dt):
        super().update(dt)

        self.current_ai_state(dt, self.action)



class AI_State():
    def __init__(self):
        self.ai_direction = None
        self.ai_move_time = 500
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

        move_speed = 0.01 * dt**2

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
    def __init__(self,pos):
        size = (64,64)
        sheet = sprite.Spritesheet(settings.MOBSHEET)
        states = {
            'idle_left': sprite.AnimatedSprite(sheet, [(0, 0)], [16, 16], size, 800),
            'idle_right': sprite.AnimatedSprite(sheet, [(0, 1)], [16, 16], size, 800),
            'walk_left':sprite.AnimatedSprite(sheet, [(0, 0), (1, 0), (2, 0), (3, 0)], [16, 16],size,250),
            'walk_right':sprite.AnimatedSprite(sheet, [(0, 1), (1, 1), (2, 1), (3, 1)], [16, 16],size,250),
            'attack_left':sprite.AnimatedSprite(sheet, [(4, 0), (5, 0), (6, 0)], [16, 16],size,500),
            'attack_right':sprite.AnimatedSprite(sheet, [(4, 1), (5, 1), (6, 1)], [16, 16],size,500)
        }
        super().__init__(states,size,pos,25,8)
        self.maxcd = 1500
        self.cooldown = 1500

    def update(self,dt):
        super().update(dt)
        for obj in self.fov:
            if isinstance(obj,mobs.Player) and self.getAttackRange(self.action.direction).colliderect(obj):
                if not self.action['attack']:
                    self.action.attack(obj)


class Skeleton(AI):
    name = 'Skeleton'
    def __init__(self,pos):
        size = (64,128)
        sheet = sprite.Spritesheet(settings.MOBSHEET)
        states = {
            'idle_left': sprite.AnimatedSprite(sheet, [(0,1), (1,1)], [16, 32], size, 800),
            'idle_right': sprite.AnimatedSprite(sheet, [(2,1), (3,1)], [16, 32], size, 800),
            'walk_left': sprite.AnimatedSprite(sheet, [(0, 1), (1, 1)], [16, 32], size, 800),
            'walk_right': sprite.AnimatedSprite(sheet, [(2, 1), (3, 1)], [16, 32], size, 800),
            'attack_left': sprite.AnimatedSprite(sheet, [(0,1), (1,1)], [16, 32], size, 1000),
            'attack_right': sprite.AnimatedSprite(sheet, [(2,1), (3,1)], [16, 32], size, 1000)

        }
        super().__init__(states,size,pos,30,10)
        self.maxcd = 1500
        self.cooldown = 1500

    def update(self,dt):
        super().update(dt)
        for obj in self.fov:
            if isinstance(obj,mobs.Player) and self.getAttackRange(self.action.direction).colliderect(obj):
                if not self.action['attack']:
                    self.action.attack(obj)


