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
            
    def render(self, renderer):
        # Apply scale
        w = self.width * self.anim_scale
        h = self.height * self.anim_scale
        cx = self.x + self.width / 2
        cy = self.y + self.height / 2
        x = cx - w / 2
        y = cy - h / 2
        
        # Glassmorphism Style
        # Glow effect when hovered
        if self.hovered:
            renderer.draw_chamfered_rect(x - 4, y - 4, w + 8, h + 8, (0.0, 0.8, 1.0, 0.4), radius=15)
            
        # Gradient Background
        # Normal: Dark Blue -> Darker Blue
        # Hover: Cyan -> Blue
        if self.hovered:
            c_top = (0.0, 0.6, 1.0, 0.9)
            c_bot = (0.0, 0.2, 0.8, 0.9)
            border_color = (0.5, 1.0, 1.0, 1.0)
        else:
            # Check if base_color is set (for tabs)
            if hasattr(self, 'base_color'):
                c_top = self.base_color
                # Darken for bottom
                c_bot = (c_top[0]*0.5, c_top[1]*0.5, c_top[2]*0.5, c_top[3])
                border_color = (c_top[0]*1.5, c_top[1]*1.5, c_top[2]*1.5, 1.0)
            else:
                c_top = (0.1, 0.2, 0.4, 0.8)
                c_bot = (0.05, 0.1, 0.2, 0.9)
                border_color = (0.2, 0.4, 0.8, 0.8)
        
        # Draw Button Body
        renderer.draw_chamfered_rect(x, y, w, h, c_top, radius=15, gradient_bot=c_bot)
        
        # Draw Border (Thin)
        # renderer.draw_rect_outline not implemented yet, simulate with slightly larger rect behind?
        # Or just skip border for now as the glow handles it.
        # Let's add a subtle border by drawing a slightly larger rect behind if not hovered?
        # Actually, draw_chamfered_rect doesn't support outline.
        # We can draw a slightly larger one behind.
        if not self.hovered:
             renderer.draw_chamfered_rect(x - 1, y - 1, w + 2, h + 2, border_color, radius=15)
             renderer.draw_chamfered_rect(x, y, w, h, c_top, radius=15, gradient_bot=c_bot)
        
        # Text
        text_w, text_h = self.text_renderer.measure_text(self.text)
        tx = cx - text_w / 2
        ty = cy - text_h / 2
        
        # Text Glow/Shadow
        if self.hovered:
             self.text_renderer.render_text(renderer, self.text, tx, ty, (255, 255, 255), outline_color=(0, 100, 255), outline_width=1)
        else:
             self.text_renderer.render_text(renderer, self.text, tx, ty, (220, 220, 220))
