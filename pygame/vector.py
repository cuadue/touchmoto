#!/usr/bin/env python

import math

class Vector():
    def __init__(self):
        self.mag, self.angle = 0, 0
        
    def __init__(self, mag, angle):
        self.mag, self.angle = mag, angle
        
    def __init__(self, other):
        self.mag, self.angle = other.mag, other.angle
        
    def x(self):
        return self.mag * math.cos(self.angle)
    
    def y(self):
        return self.mag * math.sin(self.angle)
        
    def add(self, other):
        sx, sy = self.x(), self.y()
        ox, oy = other.x(), other.y()
        self.mag = math.hypot(sx + ox, sy + oy)
        self.angle = math.atan2(sy + oy, sx + ox)
        return self
        
    def mag(self):
        return math.hypot(self.x, self.y)
    
    def mag(self, m):
        self.mag = m
        return self
        
    def scale(self, r):
        self.mag *= r
        return self
        
    def angle(self):
        return math.atan2(self.y, self.x)
    
    def angle(self, a):
        self.angle = a
        return self
    
    def rotate(self, a):
        self.angle += a
        return self
    
    def copy(self):
        return Vector(self)
        