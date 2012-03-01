import util
import pygame.sprite
from target import Target
from math import sin, cos, atan2, sqrt, degrees, hypot, fabs, pi

class Bike(pygame.sprite.Sprite):
    def __init__(self, *args, **kwargs):
        ''' Not perfect but the bike uses hardcoded constants
            Warning! Lots of opaque physics and math
        '''
        super(Bike, self).__init__(*args, **kwargs)

        # Not ideal to use white as the color key
        # Not ideal to hardcode the bike image asset
        self.original, self.rect = util.load_image('bike.png', (255,255,255))
        self.image = self.original

        self.speed = 0
        self.max_speed = 5

        # Is this bike moving?
        self.driving = 0

        # Each bike has its own target
        self.target = Target()

        # start at the origin
        self.x, self.y = self.rect.centerx, self.rect.centery
        self.angle = 0.0

        self.dt = 0.0

        # Some physics constants
        # F_c = mv*v/r --> v_max = sqrt(F_traction/m) * sqrt(r)
        self.ft = 5.0
        self.mass = 200.0
        self.brake = 0.1
        self.accel = 0.05
        self.draw_cb = []
        
    def turning_radius(self):
        if not self.target.visible: return 1e12
        "returns the radius of the circle needed to ride over the target"
        (a0, b0) = (self.target.x - self.x,  self.target.y - self.y)
        #mag: distance between Bike and it's target
        mag = hypot(a0, b0)
        #psi: angle of target relative to Bike's path of travel
        psi = util.normangle(atan2(b0, a0) - self.angle)
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
    
        a = mag * sin(psi)
        b = mag * cos(psi)
        if fabs(a) > 1e-12:
            return fabs((a*a + b*b) / (2.0*a))
        else: 
            return 1e12
    
    def update(self):
        r = self.turning_radius()
        
        r_min = self.mass * self.speed * self.speed / self.ft
        v_max = sqrt(r * self.ft/self.mass)
        dts = self.dt*60.0/1000.0

        # clear the drawing callbacks
        # TODO this is going to get slow!
        self.draw_cb = []
        
        if r < r_min and self.target.visible:
            #brake
            self.speed = max((1e-12, self.speed - self.brake * dts))
            slow_dist = 0.5 * ((self.speed - v_max) / self.brake) * (self.speed + v_max)
            r = 1e12

            # Add this to the callbacks
            @self.draw_cb.append
            def drawme(screen):
                start = self.x, self.y
                end = (self.x + cos(self.angle)*slow_dist,
                       self.y + sin(self.angle)*slow_dist)
                pygame.draw.line(screen, (127,0,0), start, end, 10)
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
            self.angle = util.normangle(self.angle + (phi * self.psi_sign))
            
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
                @self.draw_cb.append
                def drawme(s):
                    pygame.draw.circle(s, (0,0,0), (debugx, debugy), int(r), 1)
                    pygame.draw.circle(s, (0,0,0), (debugx, debugy), 2, 0)

            @self.draw_cb.append
            def drawme(s):
                pygame.draw.line(s, (0,0,0), self.rect.center, (self.x + cos(self.angle)*100,self.y + sin(self.angle)*100), 1)
        else:
            self.x += l * cos(self.angle)
            self.y += l * sin(self.angle)
            
        # the rect uses ints, so it's just for drawing
        self.rect.center = (self.x, self.y)
        # rotate and recenter. the centering is magic :(
        self.image = pygame.transform.rotate(self.original, -degrees(self.angle))
        self.rect = self.image.get_rect(center=self.rect.center)
        
        if self.target.rect.collidepoint(self.rect.center):
            self.target.unplace()
