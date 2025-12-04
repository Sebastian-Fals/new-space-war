from OpenGL.GL import *
import pygame

class PlayerRenderer:
    def __init__(self):
        pass

    def render(self, player):
        glPushMatrix()
        glTranslatef(player.x, player.y, 0)
        glRotatef(player.angle, 0, 0, 1)
        
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
        
        # Hitbox Visualization (The "Core")
        # Draw a small glowing diamond/circle at the center
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE)
        
        # Glow
        glColor4f(0.0, 1.0, 1.0, 0.5)
        glBegin(GL_TRIANGLE_FAN)
        glVertex2f(0, 0)
        for i in range(9): # 8 segments
            import math
            angle = i * math.pi * 2 / 8
            glVertex2f(math.cos(angle) * 8, math.sin(angle) * 8)
        glEnd()
        
        # Core
        glColor4f(1.0, 1.0, 1.0, 1.0)
        glBegin(GL_TRIANGLE_FAN)
        glVertex2f(0, 0)
        for i in range(9):
            angle = i * math.pi * 2 / 8
            glVertex2f(math.cos(angle) * 4, math.sin(angle) * 4)
        glEnd()
        
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        glPopMatrix()
