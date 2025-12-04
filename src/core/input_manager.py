import pygame

class InputManager:
    def __init__(self, game):
        self.game = game
        
    def get_mouse_pos(self):
        """
        Returns the mouse position in Virtual Space coordinates.
        """
        mx, my = pygame.mouse.get_pos()
        
        # Calculate scale and offset
        vw, vh = self.game.virtual_width, self.game.virtual_height
        ww, wh = self.game.window.width, self.game.window.height
        
        scale = min(ww / vw, wh / vh)
        tx = (ww - vw * scale) / 2
        ty = (wh - vh * scale) / 2
        
        # Transform mouse to virtual coords
        vmx = (mx - tx) / scale
        vmy = (my - ty) / scale
        
        return vmx, vmy

    def is_key_pressed(self, key):
        keys = pygame.key.get_pressed()
        return keys[key]

    def update(self):
        pass
