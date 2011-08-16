#!/usr/bin/env python
"""
This is based on the Chimp example game which shipped with Python
It is a prototype for the touchmoto turning algorithm!
"""

#Import Modules
import os, pygame, math
from pygame.locals import *
from math import sin, cos, pi, fabs, hypot, atan2

main_dir = os.path.split(os.path.abspath(__file__))[0]
data_dir = os.path.join(main_dir, 'data')

def load_image(name, colorkey=None):
    fullname = os.path.join(data_dir, name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error:
        print ('Cannot load image:', fullname)
        raise SystemExit(str(geterror()))
    image = image.convert()
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0,0))
        image.set_colorkey(colorkey, RLEACCEL)
    return image, image.get_rect()

#The Target class is where the Bike rider is looking, and through where he wants to ride
class Target(pygame.sprite.Sprite):
    """Places a little target on the map which the bike will pass through,
        as long as the target doesn't move."""
    def __init__(self):
        pygame.sprite.Sprite.__init__(self) #call Sprite initializer
        self.image, self.rect = load_image('target.png', (255,255,255))
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

def normangle(a):
    if a > pi: a -= 2 * pi
    if a < -pi: a += 2 * pi
    return a
        
class Bike(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self) #call Sprite intializer
        self.original, self.rect = load_image('bike.png', (255,255,255))
        self.image = self.original
        self.speed = 0
        self.max_speed = 5
        self.driving = 0
        self.target = Target()
        self.angle = 0.0
        (self.x, self.y) = (0.0 + self.rect.centerx, 0.0 + self.rect.centery) 
        self.dt = 0.0
        self.ft = 5.0 # F_c = mv*v/r --> v_max = sqrt(F_traction/m) * sqrt(r)
        self.mass = 200.0
        self.brake = 0.1
        self.accel = 0.05
        
    def turning_radius(self):
        if not self.target.visible: return 1e12
        "returns the radius of the circle needed to ride over the target"
        (a0, b0) = (self.target.x - self.x,  self.target.y - self.y)
        #mag: distance between Bike and it's target
        mag = hypot(a0, b0)
        #psi: angle of target relative to Bike's path of travel
        psi = normangle(atan2(b0, a0) - self.angle)
        if psi > 0: self.psi_sign = 1
        else:       self.psi_sign = -1
        
        if fabs(psi) > pi/2.0:
            #i don't know why but sometimes this distance comes out negative... probably something to do with sin < 0 being negative
            #take note, future scholars. The above is "dry humor"
            tmp = fabs(mag * sin(psi - self.psi_sign * pi/2.0))
            self.target.x += tmp * cos(self.angle)
            self.target.y += tmp * sin(self.angle)
            
            psi = self.psi_sign * pi/2.0
            #calculate as though the target is parallel with path of travel at 90deg angle to the path of travel
            a0 = self.target.x - self.x
            b0 = self.target.y - self.y
            mag = hypot(a0, b0)
    
        #print psi
        a = mag * sin(psi)
        b = mag * cos(psi)
        if fabs(a) > 1e-12:
            return fabs((a*a + b*b) / (2.0*a))
        else: 
            return 1e12
    
    def update(self):
        r = self.turning_radius()
        
        
        r_min = self.mass * self.speed * self.speed / self.ft
        v_max = math.sqrt(r * self.ft/self.mass)
        dts = self.dt*60.0/1000.0
        
        if r < r_min and self.target.visible:
            #brake
            self.speed = max((1e-12, self.speed - self.brake * dts))
            slow_dist = 0.5 * ((self.speed - v_max) / self.brake) * (self.speed + v_max)
            pygame.draw.line(background, (127,0,0), (self.x, self.y), (self.x + cos(self.angle)*slow_dist,self.y + sin(self.angle)*slow_dist), 10)
            r = 1e12
        else:
            #accelerate
            if not self.target.visible:
                v_max = 1e12
            # Important to keep v_max * 0.98 because otherwise, the bike is really close to over accelerating with random fluctuations
            # This is a little messy, but i think i understand the behavior if not the best solution.
            self.speed = min((self.speed + self.accel * dts, self.max_speed, v_max * 0.98))
        
        l = self.speed * dts
        if self.target.visible and fabs(r) < 1e9:
            #phi: angle of rotation to travel distance l over circle with radius r
            phi = l / r
            self.angle = normangle(self.angle + (phi * self.psi_sign))
            
            #c: the chord with angle phi through circle with radius r. extremely close to l for small values of l
            c = 2.0 * r * sin(phi/2.0)
            # fabs(c-l) is typically less than 1e-5 pixels
            self.x += c * cos(phi+self.angle)
            self.y += c * sin(phi+self.angle)
            
            # the remainder of this block is debug
            # find the center of the turning circle
            tmp = self.angle + (self.psi_sign * pi/2.0)
            debugx = int(self.x + r * cos(tmp))
            debugy = int(self.y + r * sin(tmp))
            
            #the path-of-travel circle
            if(r < 1000 and r > 0):
                pygame.draw.circle(background, (0,0,0), (debugx, debugy), int(r), 1)
                pygame.draw.circle(background, (0,0,0), (debugx, debugy), 2, 0)
            pygame.draw.line(background, (0,0,0), self.rect.center, (self.x + cos(self.angle)*100,self.y + sin(self.angle)*100), 1)
        else:
            self.x += l * cos(self.angle)
            self.y += l * sin(self.angle)
            
        # the rect uses ints, so it's just for drawing
        self.rect.center = (self.x, self.y)
        # rotate and recenter. the centering is magic :(
        self.image = pygame.transform.rotate(self.original, -math.degrees(self.angle))
        self.rect = self.image.get_rect(center=self.rect.center)
        
        if self.target.rect.collidepoint(self.rect.center):
            self.target.unplace()
            
class obstacle(pygame.sprite.Sprite):
    def __init__(self, target):
        pygame.sprite.Sprite.__init__(self) #call Sprite intializer
        self.original, self.rect = load_image('cone.png', (255,255,255))

background = None
track = None

def load_map(fpath):
    img, rect = load_image(fpath)
    
def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("TouchMoto")

    global background
    background = pygame.Surface(screen.get_size()).convert()
    background.fill((127, 127, 127))

    font = pygame.font.Font(None, 16)
        
    screen.blit(background, (0, 0))
    pygame.display.flip()

    clock = pygame.time.Clock()
    player = Bike()
    player.rect.midleft = pygame.display.get_surface().get_rect().midleft
    player.x, player.y = player.rect.centerx, player.rect.centery
    bikes = (player, )
    allsprites = pygame.sprite.RenderPlain((player.target, player))

    going = True
    while going:
        #import pdb; pdb.set_trace()
        dt = clock.tick(60) #don't go (much) faster than 60 fps
        for bike in bikes:
            bike.dt = dt
        #Handle Input Events
        for event in pygame.event.get():
            if event.type == QUIT:
                going = False
            elif event.type == MOUSEBUTTONDOWN:
                player.target.tracking = 1
                player.target.place()
            elif event.type == MOUSEBUTTONUP:
                player.target.tracking = 0
                
        if player.target.tracking:
            player.target.place()

        background.fill((127, 127, 127))
        allsprites.update()
        #Draw Everything
        text = font.render("%s" % int(player.speed*10), 1, (10, 10, 10))
        textpos = text.get_rect(centerx=background.get_width()/2)
        background.blit(text, textpos)
        screen.blit(background, (0, 0))
        allsprites.draw(screen)
        pygame.display.flip()

    pygame.quit()

if __name__ == '__main__':
    main()
