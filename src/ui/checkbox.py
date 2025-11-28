from src.ui.ui_element import UIElement

class Checkbox(UIElement):
    def __init__(self, x, y, size, checked, callback, text_renderer, label=""):
        super().__init__(x, y, size, size)
        self.checked = checked
        self.callback = callback
        self.text_renderer = text_renderer
        self.label = label
        
    def on_click(self):
        self.checked = not self.checked
        if self.callback:
            self.callback(self.checked)
            
    def render(self):
        color = (0.2, 0.6, 1.0, 0.8) if self.hovered else (0.1, 0.3, 0.5, 0.6)
        self.render_rect(self.x, self.y, self.width, self.height, color, border=True)
        
        if self.checked:
            # Draw checkmark (green box for now)
            self.render_rect(self.x + 5, self.y + 5, self.width - 10, self.height - 10, (0.0, 1.0, 0.0, 1.0))
            
        if self.label:
            self.text_renderer.render_text(self.label, self.x + self.width + 10, self.y, (255, 255, 255))
