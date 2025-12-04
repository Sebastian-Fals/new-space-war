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
            
    def render(self, renderer):
        # Background
        color = (0.1, 0.2, 0.4, 0.8) if self.hovered else (0.05, 0.1, 0.2, 0.8)
        self.render_rect(renderer, self.x, self.y, self.width, self.height, color, border=True, border_color=(0.3, 0.6, 0.9, 0.8))
        
        if self.checked:
            # Draw checkmark (Cyan Glow)
            # Inner box
            self.render_rect(renderer, self.x + 6, self.y + 6, self.width - 12, self.height - 12, (0.0, 0.8, 1.0, 1.0))
            # Glow
            self.render_rect(renderer, self.x + 4, self.y + 4, self.width - 8, self.height - 8, (0.0, 0.8, 1.0, 0.4))
            
        if self.label:
            self.text_renderer.render_text(renderer, self.label, self.x + self.width + 15, self.y + 5, (255, 255, 255))
