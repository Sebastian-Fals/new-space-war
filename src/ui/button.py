from src.ui.ui_element import UIElement
from src.graphics.text_renderer import TextRenderer

class Button(UIElement):
    def __init__(self, x, y, width, height, text, callback, text_renderer):
        super().__init__(x, y, width, height)
        self.text = text
        self.callback = callback
        self.text_renderer = text_renderer
        
    def on_click(self):
        # TODO: Spawn particles
        if self.callback:
            self.callback()
            
    def render(self):
        # Apply scale
        w = self.width * self.anim_scale
        h = self.height * self.anim_scale
        cx = self.x + self.width / 2
        cy = self.y + self.height / 2
        x = cx - w / 2
        y = cy - h / 2
        
        color = (0.2, 0.6, 1.0, 0.8) if self.hovered else (0.1, 0.3, 0.5, 0.6)
        
        # Border only when hovered
        border_color = (1.0, 1.0, 1.0, 1.0)
        show_border = self.hovered
        
        self.render_rect(x, y, w, h, color, border=show_border, border_color=border_color, radius=15)
        
        # Text
        text_w, text_h = self.text_renderer.measure_text(self.text)
        tx = cx - text_w / 2
        ty = cy - text_h / 2
        self.text_renderer.render_text(self.text, tx, ty, (255, 255, 255))
