from pygame.sprite import Sprite as PygameSprite

class Sprite(PygameSprite):
    def __init__(self, *args, **kwargs):
        super(Sprite, self).__init__(*args, **kwargs)
