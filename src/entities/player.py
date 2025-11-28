import pygame
from src.entities.entity import Entity

class Player(Entity):
    def __init__(self, x, y, bullet_manager):
        super().__init__(x, y)
        self.width = 32
        self.height = 32
        self.bullet_manager = bullet_manager
        self.shoot_timer = 0
        self.hp = 100
        self.max_hp = 100
        self.invulnerable_timer = 0

    def update(self, dt, mx, my):
        # Follow mouse (passed from scene)
        self.x = mx
        self.y = my
        
        # Clamp to screen
        self.x = max(20, min(self.x, 1260))
        self.y = max(20, min(self.y, 700))
        
        if self.invulnerable_timer > 0:
            self.invulnerable_timer -= dt
        
        self.shoot_timer -= dt
        
        # Handle shooting
        if pygame.mouse.get_pressed()[2]: # Right click
            self.shoot()

    def shoot(self):
        if self.shoot_timer <= 0:
            self.bullet_manager.spawn_bullet(self.x, self.y - 20, 0, -800, "player")
            self.shoot_timer = 0.1 # Fire rate

    def render(self):
        from OpenGL.GL import glBegin, glEnd, glVertex2f, glColor3f, GL_TRIANGLES, glPushMatrix, glPopMatrix, glTranslatef
        
        glPushMatrix()
        glTranslatef(self.x, self.y, 0)
        
        # Draw Ship (Triangle)
        glColor3f(0.0, 1.0, 1.0) # Cyan
        glBegin(GL_TRIANGLES)
        glVertex2f(0, -20)  # Nose
        glVertex2f(-15, 20) # Left Wing
        glVertex2f(15, 20)  # Right Wing
        glEnd()
        
        # Engine flame
        glColor3f(1.0, 0.5, 0.0)
        glBegin(GL_TRIANGLES)
        glVertex2f(-5, 20)
        glVertex2f(5, 20)
        glVertex2f(0, 30 + (pygame.time.get_ticks() % 100) / 10.0) # Flicker
        glEnd()
        
        glPopMatrix()
