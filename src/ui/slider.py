import pygame
from OpenGL.GL import *
from src.ui.ui_element import UIElement

class Slider(UIElement):
    def __init__(self, x, y, width, height, min_val, max_val, initial_val, callback, text_renderer, label=""):
        super().__init__(x, y, width, height)
        self.min_val = min_val
        self.max_val = max_val
        self.value = initial_val
        self.callback = callback
        self.text_renderer = text_renderer
        self.label = label
        self.dragging = False
        
    def update(self, dt, events, mx, my):
        # Check for mouse interaction
        hover = self.x < mx < self.x + self.width and self.y < my < self.y + self.height
        
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and hover:
                    self.dragging = True
                    self.update_value(mx)
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.dragging = False
                    
        if self.dragging:
            self.update_value(mx)
            
    def update_value(self, mx):
        # Calculate value based on mouse X relative to slider
        # Clamp mx to slider bounds
        rel_x = max(0, min(mx - self.x, self.width))
        pct = rel_x / self.width
        self.value = self.min_val + pct * (self.max_val - self.min_val)
        
        if self.callback:
            self.callback(self.value)
            
    def render(self, renderer):
        # Draw Label (Handled by OptionsScene now, but keep for standalone usage)
        if self.label:
            tw, th = self.text_renderer.measure_text(self.label)
            self.text_renderer.render_text(renderer, self.label, self.x, self.y - th - 5, (200, 220, 255))
            
        # Draw Track (Background)
        # glDisable(GL_TEXTURE_2D) # Not needed with Renderer2D
        
        track_h = 8
        track_y = self.y + (self.height - track_h) // 2
        
        # Track Background (Dark)
        # Use small radius for rounded ends
        self.render_rect(renderer, self.x, track_y, self.width, track_h, (0.1, 0.1, 0.2, 1.0), border=True, border_color=(0.3, 0.3, 0.4, 1.0), radius=4)
        
        # Draw Fill (Active part)
        pct = (self.value - self.min_val) / (self.max_val - self.min_val)
        fill_w = self.width * pct
        
        # Fill (Cyan Gradient)
        if fill_w > 0:
            # Clamp fill_w to at least radius*2 if we want perfect rounds, but clamping in render_rect handles it.
            # We want the fill to look connected to the handle.
            self.render_rect(renderer, self.x, track_y, fill_w, track_h, (0.0, 0.6, 0.9, 1.0), radius=4)
        
        # Draw Handle (Knob)
        # Handle is a diamond (20x20 with 10 radius)
        handle_size = 20
        handle_x = self.x + fill_w - handle_size / 2
        handle_y = self.y + (self.height - handle_size) // 2
        
        # Handle Glow
        if self.dragging:
             self.render_rect(renderer, handle_x - 2, handle_y - 2, handle_size+4, handle_size+4, (0.5, 0.9, 1.0, 0.5), radius=12)
        
        # Handle Body
        self.render_rect(renderer, handle_x, handle_y, handle_size, handle_size, (1.0, 1.0, 1.0, 1.0), border=True, border_color=(0.0, 0.0, 0.0, 1.0), radius=10)
        
        # Draw Value Text
        val_text = f"{int(self.value * 100)}%"
        # Vertically center text
        th = 24 # Approximate height or measure
        text_y = self.y + (self.height - th) // 2 + 5 # +5 nudge
        self.text_renderer.render_text(renderer, val_text, self.x + self.width + 15, text_y, (255, 255, 255))
