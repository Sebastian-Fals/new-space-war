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
        
        handled = False
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and self.hovered:
                    self.clicked = True
                    self.on_click()
                    handled = True
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.clicked = False
                    
        return handled
                    
    def on_click(self):
        pass
        
    def render_rect(self, renderer, x, y, w, h, color, border=False, border_color=(1,1,1), radius=10, gradient_bot=None):
        if border:
            # Draw border as a larger rect behind
            renderer.draw_chamfered_rect(x - 2, y - 2, w + 4, h + 4, border_color, radius)
            
        renderer.draw_chamfered_rect(x, y, w, h, color, radius)
