import pygame
from src.entities.entity import Entity

class Player(Entity):
    def __init__(self, x, y, bullet_manager):
        super().__init__(x, y)
        self.width = 32
        self.height = 32
        self.bullet_manager = bullet_manager
        self.shoot_timer = 0
        self.hp = 100
        self.max_hp = 100
        self.invulnerable_timer = 0
        self.max_hp = 100
        self.invulnerable_timer = 0
        self.angle = 0
        self.hitbox_radius = 4 # Exact size of visual core

    def update(self, dt, mx, my):
        # Calculate velocity for tilt
        dx = mx - self.x
        target_angle = dx * 0.5 # Fixed inverted tilt
        target_angle = max(-15, min(target_angle, 15)) # Clamp to +/- 15 degrees
        
        # Smooth rotation
        self.angle += (target_angle - self.angle) * 10 * dt
        
        # Follow mouse (passed from scene)
        self.x = mx
        self.y = my
        
        # Clamp to screen
        self.x = max(20, min(self.x, 1260))
        self.y = max(20, min(self.y, 700))
        
        if self.invulnerable_timer > 0:
            self.invulnerable_timer -= dt
        
        self.shoot_timer -= dt
        
        # Handle shooting
        if pygame.mouse.get_pressed()[2]: # Right click
            self.shoot()

    def shoot(self):
        if self.shoot_timer <= 0:
            self.bullet_manager.spawn_bullet(self.x, self.y - 20, 0, -800, "player")
            self.shoot_timer = 0.1 # Fire rate

    def render(self):
        # Rendering is now handled by PlayerRenderer, but we keep this for compatibility
        # or we can remove it and call renderer directly in GameScene.
        # For now, let's instantiate renderer here or pass it in?
        # Better: GameScene should have the renderer and call it.
        # But to keep GameScene simple, Player can hold its renderer?
        # Or better: Player shouldn't know about rendering.
        # Let's update GameScene to use PlayerRenderer.
        pass
