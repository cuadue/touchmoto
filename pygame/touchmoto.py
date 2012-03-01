#!/usr/bin/python

import os, pygame, math
from bike import Bike

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

    # huge TODO is AI
    bikes = [player]
    
    # This is a bit of a hack
    player.rect.midleft = pygame.display.get_surface().get_rect().midleft
    player.x, player.y = player.rect.centerx, player.rect.centery

    # delegate rendering and updating to Pygame. Probably needs to 
    # be reworked eventually.
    allsprites = pygame.sprite.RenderPlain((player.target, player))

    while True:
        # don't go (much) faster than 60 fps
        dt = clock.tick(60) 
        for bike in bikes:
            bike.dt = dt

        # Handle Input Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return 
            elif event.type == pygame.MOUSEBUTTONDOWN:
                player.target.tracking = 1
                player.target.place()
            elif event.type == pygame.MOUSEBUTTONUP:
                player.target.tracking = 0
                
        # This is how we respond to mouse dragging events
        if player.target.tracking:
            player.target.place()

        allsprites.update()

        # Clear the screen
        background.fill((127, 127, 127))
        screen.blit(background, (0, 0))

        # Draw the sprite callbacks. These are for debugging so I'm not going
        # to even try to generalize it.
        for s in allsprites:
            if hasattr(s, 'draw_cb'):
                for callback in s.draw_cb:
                    callback(screen)

        # Draw your speed
        text = font.render("%s" % int(player.speed*10), 1, (10, 10, 10))
        textpos = text.get_rect(centerx=background.get_width()/2)
        screen.blit(text, textpos)

        # Let pygame draw all 2 sprites
        allsprites.draw(screen)

        # And show `screen`
        pygame.display.flip()

if __name__ == '__main__':
    main()

