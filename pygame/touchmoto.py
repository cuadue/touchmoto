#!/usr/bin/env python
"""
This is based on the Chimp example game which shipped with Python
It is a prototype for the touchmoto turning algorithm!
"""

import os, pygame, math
from bike import Bike
class Obstacle(pygame.sprite.Sprite):
    ''' Not used presently '''
    def __init__(self, target, *args, **kwargs):
        super(Obstacle, self).__init__(*args, **kwargs)
        self.original, self.rect = load_image('cone.png', (255,255,255))

background = None
track = None

def load_map(fpath):
    img, rect = load_image(fpath)
    
def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("TouchMoto")

    background = pygame.Surface(screen.get_size()).convert()

    font = pygame.font.Font(None, 16)
        
    screen.blit(background, (0, 0))
    pygame.display.flip()

    clock = pygame.time.Clock()
    player = Bike()
    player.rect.midleft = pygame.display.get_surface().get_rect().midleft
    player.x, player.y = player.rect.centerx, player.rect.centery
    bikes = [player]
    allsprites = pygame.sprite.RenderPlain((player.target, player))

    while True:
        #import pdb; pdb.set_trace()
        dt = clock.tick(60) #don't go (much) faster than 60 fps
        for bike in bikes:
            bike.dt = dt
        #Handle Input Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return 
            elif event.type == pygame.MOUSEBUTTONDOWN:
                player.target.tracking = 1
                player.target.place()
            elif event.type == pygame.MOUSEBUTTONUP:
                player.target.tracking = 0
                
        if player.target.tracking:
            player.target.place()

        allsprites.update()

        # Clear the screen
        background.fill((127, 127, 127))
        screen.blit(background, (0, 0))

        # Draw callbacks
        # Not sure if drawing directly to the screen is best
        for s in allsprites:
            if hasattr(s, 'draw_cb'):
                for callback in s.draw_cb:
                    callback(screen)

        #Draw Everything
        text = font.render("%s" % int(player.speed*10), 1, (10, 10, 10))
        textpos = text.get_rect(centerx=background.get_width()/2)
        screen.blit(text, textpos)

        allsprites.draw(screen)
        pygame.display.flip()

if __name__ == '__main__':
    main()
