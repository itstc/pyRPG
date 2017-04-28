import pygame

class Player(pygame.sprite.Sprite):
    #TODO: Create a player and place it on the map
    def __init__(self,surface,position):
        pygame.sprite.Sprite.__init__(self)

        self.surface = surface
        self.image = pygame.Surface([64,128])
        self.image.fill(pygame.Color('purple'))
        self.rect = self.image.get_rect()
        self.rect.center = position

        self.stats = Player.PlayerStats()

    def update(self):
        pass

    def getStats(self):
        return self.stats

    def getRect(self):
        return self.rect

    def getPosition(self):
        return self.rect.topleft

    def render(self,camera):
        offset = camera.getView()
        self.surface.blit(self.image,(self.getPosition()[0] - offset[0],self.getPosition()[1] - offset[1]))

    class PlayerStats:
        initHP = 100
        def __init__(self):
            self.maxHP = Player.PlayerStats.initHP
            self.hp = self.maxHP

        def damage(self,value):
            self.hp -= value
