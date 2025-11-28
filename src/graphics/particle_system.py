import random
from OpenGL.GL import *

class Particle:
    def __init__(self, x, y, color, vx=None, vy=None):
        self.x = x
        self.y = y
        # Explode outwards or use provided velocity
        if vx is not None:
            self.vx = vx + random.uniform(-50, 50) # Add some spread
        else:
            self.vx = random.uniform(-150, 150)
            
        if vy is not None:
            self.vy = vy + random.uniform(-50, 50)
        else:
            self.vy = random.uniform(-150, 150)
        self.life = 1.0
        
        # White color scale (droplets)
        shade = random.uniform(0.7, 1.0)
        self.color = (shade, shade, shade)
        
        self.size = random.uniform(2, 4)

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy += 200 * dt # Gravity for droplet feel
        self.life -= dt * 1.5
        self.size -= dt * 1.0

class ParticleSystem:
    def __init__(self):
        self.particles = []

    def emit(self, x, y, count=20, color=(1, 1, 1), vx=None, vy=None):
        for _ in range(count):
            self.particles.append(Particle(x, y, color, vx, vy))

    def update(self, dt):
        self.particles = [p for p in self.particles if p.life > 0]
        for p in self.particles:
            p.update(dt)

    def render(self):
        glDisable(GL_TEXTURE_2D)
        glBegin(GL_QUADS)
        for p in self.particles:
            alpha = max(0, p.life)
            glColor4f(p.color[0], p.color[1], p.color[2], alpha)
            
            s = max(0, p.size)
            glVertex2f(p.x - s, p.y - s)
            glVertex2f(p.x + s, p.y - s)
            glVertex2f(p.x + s, p.y + s)
            glVertex2f(p.x - s, p.y + s)
        glEnd()
