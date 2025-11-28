import pygame
from OpenGL.GL import *

class UIElement:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.hovered = False
        self.clicked = False
        self.anim_scale = 1.0
        
    def update(self, dt, events, mx, my):
        self.hovered = self.x < mx < self.x + self.width and self.y < my < self.y + self.height
        
        # Bounce animation logic
        target_scale = 1.1 if self.hovered else 1.0
        if self.clicked:
            target_scale = 0.95 # Shrink slightly when clicked
            
        self.anim_scale += (target_scale - self.anim_scale) * 15 * dt
        
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and self.hovered:
                    self.clicked = True
                    self.on_click()
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.clicked = False
                    
    def on_click(self):
        pass
        
    def render_rect(self, x, y, w, h, color, border=False, border_color=(1,1,1), radius=0):
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        # Pixel Art Style: Chamfered corners (diagonal cut)
        cut = 10 # Size of the corner cut
        
        def draw_chamfered(cx, cy, cw, ch, c):
            if len(c) == 4:
                glColor4f(*c)
            else:
                glColor3f(*c)
                
            glBegin(GL_POLYGON)
            # Top-Left
            glVertex2f(cx + cut, cy)
            # Top-Right
            glVertex2f(cx + cw - cut, cy)
            glVertex2f(cx + cw, cy + cut)
            # Bottom-Right
            glVertex2f(cx + cw, cy + ch - cut)
            glVertex2f(cx + cw - cut, cy + ch)
            # Bottom-Left
            glVertex2f(cx + cut, cy + ch)
            glVertex2f(cx, cy + ch - cut)
            glVertex2f(cx, cy + cut)
            glEnd()

        if border:
            # Draw slightly larger rect for border
            draw_chamfered(x - 4, y - 4, w + 8, h + 8, border_color)
            
        draw_chamfered(x, y, w, h, color)
