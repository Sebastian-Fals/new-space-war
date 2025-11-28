import math
from src.entities.entity import Entity
from OpenGL.GL import *

class Boss(Entity):
    def __init__(self, x, y, bullet_manager):
        super().__init__(x, y)
        self.bullet_manager = bullet_manager
        self.hp = 1000
        self.max_hp = 1000
        self.phase = 0
        self.time = 0
        self.width = 100
        self.height = 100
        
    def update(self, dt):
        self.time += dt
        
        # Movement: Figure 8
        self.x = 640 + math.sin(self.time * 0.5) * 300
        self.y = 150 + math.sin(self.time) * 50
        
        # Shooting patterns based on phase
        if self.time % 0.2 < dt:
            self.shoot_pattern()
            
    def shoot_pattern(self):
        # Geometric pattern: Circle
        num_bullets = 20
        for i in range(num_bullets):
            angle = (i / num_bullets) * 2 * math.pi + self.time
            dx = math.cos(angle) * 300
            dy = math.sin(angle) * 300
            self.bullet_manager.spawn_bullet(self.x, self.y, dx, dy, "enemy")

    def render(self):
        glPushMatrix()
        glTranslatef(self.x, self.y, 0)
        glColor3f(1.0, 0.0, 1.0) # Magenta
        
        glBegin(GL_QUADS)
        glVertex2f(-50, -50)
        glVertex2f(50, -50)
        glVertex2f(50, 50)
        glVertex2f(-50, 50)
        glEnd()
        
        glPopMatrix()
