from src.ui.ui_element import UIElement
import pygame
from OpenGL.GL import *

class Dropdown(UIElement):
    def __init__(self, x, y, width, height, options, selected_index, callback, text_renderer):
        super().__init__(x, y, width, height)
        self.options = options
        self.selected_index = selected_index
        self.callback = callback
        self.text_renderer = text_renderer
        self.expanded = False
        
    def update(self, dt, events, mx, my):
        # Don't call super().update immediately because we need custom click handling for expanded
        # But we do need hover logic.
        
        self.hovered = self.x < mx < self.x + self.width and self.y < my < self.y + self.height
        
        # Bounce animation logic (copied from UIElement)
        target_scale = 1.1 if self.hovered else 1.0
        if self.clicked: target_scale = 0.95
        self.anim_scale += (target_scale - self.anim_scale) * 15 * dt
        
        self.hover_idx = -1
        handled = False
        
        # Calculate full bounds if expanded
        full_height = self.height
        if self.expanded:
            full_height += len(self.options) * (self.height + 2)
            
        is_mouse_over_expanded = self.x < mx < self.x + self.width and self.y < my < self.y + full_height
        
        if self.expanded:
            # Check clicks on options FIRST
            for event in events:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    # Calculate full height
                    # We added margins, so calculation changes
                    # y = self.y + self.height + (self.height + 2) * i
                    
                    clicked_option = False
                    for i in range(len(self.options)):
                         opt_y = self.y + self.height + (self.height + 2) * i
                         if self.x < mx < self.x + self.width and opt_y < my < opt_y + self.height:
                             self.selected_index = i
                             self.expanded = False
                             if self.callback: self.callback(self.selected_index)
                             clicked_option = True
                             handled = True
                             break
                    
                    if not clicked_option:
                        # If clicked outside main box AND outside options, close
                        # But if clicked on main box, let standard logic handle it (toggle)
                        
                        # Check if clicked on main box
                        if self.x < mx < self.x + self.width and self.y < my < self.y + self.height:
                            # Will be handled by standard logic below
                            pass
                        else:
                            # Clicked outside everything
                            self.expanded = False
                            handled = True
            
            # Calculate hover index for rendering
            if self.x < mx < self.x + self.width and self.y + self.height < my:
                 dy = my - (self.y + self.height)
                 idx = int(dy / (self.height + 2))
                 if 0 <= idx < len(self.options):
                     self.hover_idx = idx
                     
        # Standard click handling for main box
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and self.hovered:
                    self.clicked = True
                    self.on_click()
                    handled = True
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.clicked = False
                    
        # If expanded and mouse is over the expanded area, capture the event
        # This prevents underlying elements from receiving hover/clicks
        if self.expanded and is_mouse_over_expanded:
            handled = True
            
        return handled

    def on_click(self):
        self.expanded = not self.expanded
        
    def render(self, renderer):
        # Main box
        # Gradient effect
        # Normal: Dark Blue -> Darker Blue
        # Hover: Cyan -> Blue
        if self.hovered or self.expanded:
            c_top = (0.0, 0.5, 0.9, 0.9)
            c_bot = (0.0, 0.2, 0.7, 0.9)
            border_color = (0.4, 0.9, 1.0, 1.0)
        else:
            c_top = (0.1, 0.2, 0.4, 0.8)
            c_bot = (0.05, 0.1, 0.2, 0.9)
            border_color = (0.2, 0.4, 0.8, 0.8)
            
        # Draw main rect with gradient and chamfered corners
        renderer.draw_chamfered_rect(self.x, self.y, self.width, self.height, c_top, radius=10, gradient_bot=c_bot)
        
        # Border
        if not (self.hovered or self.expanded):
             renderer.draw_chamfered_rect(self.x - 1, self.y - 1, self.width + 2, self.height + 2, border_color, radius=10)
             renderer.draw_chamfered_rect(self.x, self.y, self.width, self.height, c_top, radius=10, gradient_bot=c_bot)
        else:
             # Glow border
             renderer.draw_chamfered_rect(self.x - 2, self.y - 2, self.width + 4, self.height + 4, (0.0, 0.8, 1.0, 0.5), radius=10)
             renderer.draw_chamfered_rect(self.x, self.y, self.width, self.height, c_top, radius=10, gradient_bot=c_bot)
        
        # Selected text
        text = str(self.options[self.selected_index])
        self.text_renderer.render_text(renderer, text, self.x + 10, self.y + 10, (255, 255, 255))
        
        # Arrow
        arrow = "^" if self.expanded else "v"
        self.text_renderer.render_text(renderer, arrow, self.x + self.width - 25, self.y + 10, (200, 200, 255))
        
        if self.expanded:
            for i, opt in enumerate(self.options):
                # Add margin between options
                margin = 2
                y = self.y + self.height + (self.height + margin) * i
                
                # Highlight hover
                is_hover = (i == self.hover_idx)
                
                # Option Background
                c_top = (0.2, 0.4, 0.8, 0.95) if is_hover else (0.1, 0.15, 0.3, 0.95)
                c_bot = (0.1, 0.3, 0.6, 0.95) if is_hover else (0.05, 0.1, 0.2, 0.95)
                
                # Use draw_chamfered_rect for options too
                renderer.draw_chamfered_rect(self.x, y, self.width, self.height, c_top, radius=5, gradient_bot=c_bot)
                
                self.text_renderer.render_text(renderer, str(opt), self.x + 10, y + 10, (255, 255, 255) if is_hover else (200, 200, 200))
