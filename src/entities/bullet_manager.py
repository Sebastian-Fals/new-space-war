import numpy as np
from OpenGL.GL import *
import random

class BulletManager:
    def __init__(self, particle_system=None):
        self.bullets = [] # List of bullet objects for now, optimize later
        self.particle_system = particle_system
        
    def spawn_bullet(self, x, y, dx, dy, type="player"):
        self.bullets.append({
            "x": x, "y": y,
            "dx": dx, "dy": dy,
            "type": type,
            "active": True
        })

    def update(self, dt):
        for b in self.bullets:
            if not b["active"]: continue
            
            b["x"] += b["dx"] * dt
            b["y"] += b["dy"] * dt
            
            # Particle Trail
            if self.particle_system and random.random() < 0.3: # 30% chance per frame
                color = (0.5, 1.0, 1.0) if b["type"] == "player" else (1.0, 0.5, 0.5)
                # Spawn small trail particle opposite to movement
                vx = -b["dx"] * 0.1
                vy = -b["dy"] * 0.1
                self.particle_system.emit(b["x"], b["y"], count=1, color=color, vx=vx, vy=vy)
            
            # Boundary check (hardcoded for now, should use window size)
            if b["x"] < -50 or b["x"] > 1330 or b["y"] < -50 or b["y"] > 770:
                b["active"] = False
        
        # Remove inactive bullets
        self.bullets = [b for b in self.bullets if b["active"]]

    def render(self):
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE) # Additive Blending for Bloom
        
        glBegin(GL_QUADS)
        for b in self.bullets:
            if b["type"] == "player":
                color = (0.0, 1.0, 1.0) # Cyan
            else:
                color = (1.0, 0.0, 0.0) # Red
            
            x, y = b["x"], b["y"]
            size = 3 # Smaller bullets (was 8)
            
            # Glow (Outer quad) - Larger and softer
            glColor4f(*color, 0.4)
            glVertex2f(x, y - size * 4) # Larger glow relative to core
            glVertex2f(x + size * 4, y)
            glVertex2f(x, y + size * 4)
            glVertex2f(x - size * 4, y)
            
            # Core (Inner quad) - Bright center
            glColor4f(1.0, 1.0, 1.0, 0.8) # White-ish core
            glVertex2f(x, y - size)
            glVertex2f(x + size, y)
            glVertex2f(x, y + size)
            glVertex2f(x - size, y)
        glEnd()
        
        # Reset blend func to normal alpha blending
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
