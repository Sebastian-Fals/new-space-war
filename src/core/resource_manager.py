import pygame
import os

class ResourceManager:
    def __init__(self):
        self.textures = {}
        self.sounds = {}
        self.fonts = {}
        self.base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        
    def load_texture(self, name):
        if name not in self.textures:
            path = os.path.join(self.base_path, 'assets', 'sprites', name)
            try:
                surface = pygame.image.load(path).convert_alpha()
                self.textures[name] = surface
            except Exception as e:
                print(f"Failed to load texture {name}: {e}")
                return None
        return self.textures[name]

    # TODO: Add sound and font loading
