import os 
import pygame
import math

main_dir = os.path.split(os.path.abspath(__file__))[0]
data_dir = os.path.join(main_dir, 'data')

def load_image(name, colorkey=None):
    fullname = os.path.join(data_dir, name)
    try:
        result = pygame.image.load(fullname)
    except pygame.error:
        print ('Cannot load image:', fullname)
        raise SystemExit(str(pygame.geterror()))
    result = result.convert()
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0,0))
        result.set_colorkey(colorkey, pygame.RLEACCEL)
    return result, result.get_rect()

def normangle(a):
    if a > math.pi: a -= 2 * math.pi
    if a < -math.pi: a += 2 * math.pi
    return a
