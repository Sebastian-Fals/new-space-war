from src.ui.ui_element import UIElement
import pygame

class Dropdown(UIElement):
    def __init__(self, x, y, width, height, options, selected_index, callback, text_renderer):
        super().__init__(x, y, width, height)
        self.options = options
        self.selected_index = selected_index
        self.callback = callback
        self.text_renderer = text_renderer
        self.expanded = False
        
    def update(self, dt, events, mx, my):
        super().update(dt, events, mx, my)
        
        self.hover_idx = -1
        
        if self.expanded:
            # Check clicks outside to close
            for event in events:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    # Calculate full height
                    full_h = self.height * (len(self.options) + 1)
                    if not (self.x < mx < self.x + self.width and self.y < my < self.y + full_h):
                        self.expanded = False
                    elif self.y + self.height < my: # Clicked on option
                        idx = int((my - (self.y + self.height)) / self.height)
                        if 0 <= idx < len(self.options):
                            self.selected_index = idx
                            self.expanded = False
                            if self.callback:
                                self.callback(self.selected_index)
            
            # Calculate hover index for rendering
            if self.x < mx < self.x + self.width and self.y + self.height < my:
                 idx = int((my - (self.y + self.height)) / self.height)
                 if 0 <= idx < len(self.options):
                     self.hover_idx = idx

    def on_click(self):
        self.expanded = not self.expanded
        
    def render(self):
        # Main box
        color = (0.2, 0.6, 1.0, 0.8) if self.hovered else (0.1, 0.3, 0.5, 0.6)
        self.render_rect(self.x, self.y, self.width, self.height, color, border=True)
        
        # Selected text
        text = str(self.options[self.selected_index])
        self.text_renderer.render_text(text, self.x + 10, self.y + 5, (255, 255, 255))
        
        # Arrow
        self.text_renderer.render_text("v" if not self.expanded else "^", self.x + self.width - 20, self.y + 5, (200, 200, 200))
        
        if self.expanded:
            for i, opt in enumerate(self.options):
                y = self.y + self.height * (i + 1)
                
                # Highlight hover
                is_hover = (i == self.hover_idx)
                opt_color = (0.3, 0.7, 1.0, 0.9) if is_hover else (0.2, 0.4, 0.6, 0.9)
                
                self.render_rect(self.x, y, self.width, self.height, opt_color, border=True)
                self.text_renderer.render_text(str(opt), self.x + 10, y + 5, (255, 255, 255))
