import pygame
import util

class Target(pygame.sprite.Sprite):
    """ Places a little target on the map which the bike will pass through,
        as long as the target doesn't move.
    """
    def __init__(self, *args, **kwargs):
        super(Target, self).__init__(*args, **kwargs)
        # TODO change hardcoded asset path
        self.image, self.rect = util.load_image('target.png', (255,255,255))
        self.visible = self.tracking = 0
        self.r = self.x = self.y = 0

    def place(self):
        "place the target on the screen"
        (self.x, self.y) = pygame.mouse.get_pos()
        self.visible = self.tracking = 1

    def unplace(self):
        "returns true if the fist collides with the target"
        self.tracking = self.visible = 0
        
    def update(self):
        self.rect.center = (self.x, self.y)
        
