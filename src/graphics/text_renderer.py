import pygame
from OpenGL.GL import *

class TextRenderer:
    def __init__(self, font_name=None, size=24, antialias=False):
        # Use default system font (None) or specific if available
        # antialias=False gives a more pixelated look
        self.font = pygame.font.SysFont("consolas", size) if font_name == "pixel" else pygame.font.SysFont(font_name, size)
        self.antialias = antialias
        self.textures = {}
        self.max_cache_size = 100

    def clear_cache(self):
        if not self.textures: return
        ids = [t[0] for t in self.textures.values()]
        glDeleteTextures(len(ids), ids)
        self.textures.clear()

    def render_text(self, renderer, text, x, y, color=(255, 255, 255), outline_color=None, outline_width=2):
        if outline_color:
            # Render outline by rendering text at offsets
            for dx in [-outline_width, outline_width]:
                for dy in [-outline_width, outline_width]:
                    self._render_single(renderer, text, x + dx, y + dy, outline_color)
            # Render center
            self._render_single(renderer, text, x, y, color)
        else:
            self._render_single(renderer, text, x, y, color)

    def _render_single(self, renderer, text, x, y, color):
        # Cache based on text only (since we tint with glColor)
        key = text
        if key not in self.textures:
            if len(self.textures) >= self.max_cache_size:
                self.clear_cache()
                
            # Render white text to texture
            surface = self.font.render(text, self.antialias, (255, 255, 255))
            texture_data = pygame.image.tostring(surface, "RGBA", 1)
            width = surface.get_width()
            height = surface.get_height()
            
            texture_id = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, texture_id)
            # Nearest neighbor filtering for pixel look
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, texture_data)
            
            self.textures[key] = (texture_id, width, height)
            
        texture_id, width, height = self.textures[key]
        
        # Handle color input (can be tuple of 3 or 4, ints 0-255 or floats 0-1)
        r, g, b, a = 1.0, 1.0, 1.0, 1.0
        
        if len(color) >= 3:
            # Check if floats or ints
            is_float = any(isinstance(c, float) for c in color)
            if is_float:
                r = color[0]
                g = color[1]
                b = color[2]
                if len(color) > 3: a = color[3]
            else:
                r = color[0] / 255.0
                g = color[1] / 255.0
                b = color[2] / 255.0
                if len(color) > 3: a = color[3] / 255.0
        
        renderer.draw_texture(texture_id, x, y, width, height, (r, g, b, a))

    def measure_text(self, text):
        return self.font.size(text)
