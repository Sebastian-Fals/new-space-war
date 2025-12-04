import math
from src.entities.entity import Entity
from OpenGL.GL import *

class Enemy(Entity):
    def __init__(self, x, y, type_id, bullet_manager, difficulty='medium'):
        super().__init__(x, y)
        self.type_id = type_id
        self.bullet_manager = bullet_manager
        self.difficulty = difficulty
        self.time = 0
        
        # HP Scaling
        base_hp = 10
        if difficulty == 'easy': self.hp = base_hp
        elif difficulty == 'medium': self.hp = base_hp * 1.5
        elif difficulty == 'hard': self.hp = base_hp * 2.0
        elif difficulty == 'extreme': self.hp = base_hp * 3.0
        else: self.hp = base_hp
        
        self.shoot_timer = 0
        
        # Physics & Rotation
        self.vx = 0
        self.vy = 0
        self.angle = 180 # Facing down
        self.target_angle = 180
        
        self.state = 'ENTERING'
        # Start above screen if not already
        if self.y > -50: self.y = -50
        
    def update(self, dt, player=None):
        self.time += dt
        
        # State Machine
        if self.state == 'ENTERING':
            # Move down to target Y (e.g., 25px from top or just enter screen)
            target_y = 25
            self.angle = 0 # Force Face DOWN while entering
            if self.y < target_y:
                self.y += 200 * dt # Enter speed
            else:
                self.state = 'ACTIVE'
                self.time = 0 # Reset time for patterns
            return # Don't do other logic while entering
            
        # ACTIVE State Logic
        
        # Calculate Velocity based on type
        if self.type_id == 0: # Red - Group behavior (Standard Sine for now, but spawned in groups)
            self.vy = 100
            self.vx = math.cos(self.time * 2) * 150
            
        elif self.type_id == 1: # Zigzag
            self.vy = 80
            self.vx = 100 if (int(self.time) % 2 == 0) else -100
            
        elif self.type_id == 2: # Blue - Kamikaze with Tracking
            self.vy = 300 # Fast down
            
            # Tracking logic
            if player:
                dx = player.x - self.x
                # Steer towards player X with smoothing
                # Wide angle (170 deg) means we can go very fast horizontally
                max_vx = 300 
                target_vx = 0
                
                if dx > 10: target_vx = max_vx
                elif dx < -10: target_vx = -max_vx
                
                # Smooth acceleration (Sine-like or just lerp)
                # Lerp: current + (target - current) * speed * dt
                self.vx += (target_vx - self.vx) * 5 * dt
                
            else:
                # Decelerate if no player
                self.vx += (0 - self.vx) * 5 * dt
                
        elif self.type_id == 3: # Yellow - Stop and shoot
            if self.time < 1.0:
                self.vy = 150
                self.vx = 0
            else:
                self.vy = 0
                self.vx = 0
                
        elif self.type_id == 4: # Orbit (simplified)
            self.vy = 50
            self.vx = math.cos(self.time) * 100
            
        # Apply Velocity
        self.x += self.vx * dt
        self.y += self.vy * dt
        
        # Boundary Checks (Sides only)
        if self.x < 20: 
            self.x = 20
            self.vx *= -1 
        elif self.x > 1260:
            self.x = 1260
            
        # Off-screen Culling (Bottom)
        # Assuming virtual height is 720. Add margin of 100.
        if self.y > 820:
            self.active = False
            return
            
        # Calculate Target Angle
        if self.type_id == 3: # Stop and shoot - Aim at player
            if player:
                dx = player.x - self.x
                dy = player.y - self.y
                rads = math.atan2(dy, dx)
                degs = math.degrees(rads)
                self.target_angle = degs - 90
            else:
                self.target_angle = 0 
                
        elif abs(self.vx) > 10 or abs(self.vy) > 10:
            # Rotate towards movement vector
            rads = math.atan2(self.vy, self.vx)
            degs = math.degrees(rads)
            self.target_angle = degs - 90 
            
        # Smooth Rotation
        diff = (self.target_angle - self.angle + 180) % 360 - 180
        self.angle += diff * 5 * dt 
        
        # Shooting logic
        self.shoot_timer += dt
        
        # Difficulty Multipliers
        fire_rate_mult = 1.0
        if self.difficulty == 'easy': fire_rate_mult = 1.0
        elif self.difficulty == 'medium': fire_rate_mult = 0.7
        elif self.difficulty == 'hard': fire_rate_mult = 0.5
        elif self.difficulty == 'extreme': fire_rate_mult = 0.3
        
        # Fire rate and pattern based on type
        if self.type_id == 0: # Red - Shoot straight down
            if self.shoot_timer > 1.5 * fire_rate_mult:
                self.shoot_timer = 0
                self.bullet_manager.spawn_bullet(self.x, self.y + 20, 0, 300, "enemy")
                
        elif self.type_id == 1: # Zigzag
            if self.shoot_timer > 2.0 * fire_rate_mult:
                self.shoot_timer = 0
                self.bullet_manager.spawn_bullet(self.x, self.y + 20, 0, 300, "enemy")
                self.bullet_manager.spawn_bullet(self.x, self.y + 20, -100, 250, "enemy")
                self.bullet_manager.spawn_bullet(self.x, self.y + 20, 100, 250, "enemy")
                
                if self.difficulty in ['hard', 'extreme']:
                    self.bullet_manager.spawn_bullet(self.x, self.y + 20, -200, 200, "enemy")
                    self.bullet_manager.spawn_bullet(self.x, self.y + 20, 200, 200, "enemy")
                
                if self.difficulty == 'extreme':
                    self.bullet_manager.spawn_bullet(self.x, self.y + 20, -300, 150, "enemy")
                    self.bullet_manager.spawn_bullet(self.x, self.y + 20, 300, 150, "enemy")
                
        elif self.type_id == 2: # Kamikaze - No shoot
            pass
            
        elif self.type_id == 3: # Yellow - Aimed at player
            if self.shoot_timer > 1.0 * fire_rate_mult: 
                self.shoot_timer = 0
                
                vx, vy = 0, 400
                if player:
                    dx = player.x - self.x
                    dy = player.y - self.y
                    dist = math.sqrt(dx*dx + dy*dy)
                    if dist > 0:
                        vx = (dx / dist) * 400
                        vy = (dy / dist) * 400
                
                import random
                spread_angle = random.uniform(-0.1, 0.1)
                cs = math.cos(spread_angle); sn = math.sin(spread_angle)
                final_vx = vx * cs - vy * sn
                final_vy = vx * sn + vy * cs
                
                self.bullet_manager.spawn_bullet(self.x, self.y + 20, final_vx, final_vy, "enemy")
                
                if self.difficulty in ['hard', 'extreme']:
                     spread_angle = -0.2
                     cs = math.cos(spread_angle); sn = math.sin(spread_angle)
                     vx1 = vx * cs - vy * sn; vy1 = vx * sn + vy * cs
                     self.bullet_manager.spawn_bullet(self.x, self.y + 20, vx1, vy1, "enemy")
                     
                     spread_angle = 0.2
                     cs = math.cos(spread_angle); sn = math.sin(spread_angle)
                     vx2 = vx * cs - vy * sn; vy2 = vx * sn + vy * cs
                     self.bullet_manager.spawn_bullet(self.x, self.y + 20, vx2, vy2, "enemy")
                     
                if self.difficulty == 'extreme':
                     spread_angle = -0.4
                     cs = math.cos(spread_angle); sn = math.sin(spread_angle)
                     vx3 = vx * cs - vy * sn; vy3 = vx * sn + vy * cs
                     self.bullet_manager.spawn_bullet(self.x, self.y + 20, vx3, vy3, "enemy")
                     
                     spread_angle = 0.4
                     cs = math.cos(spread_angle); sn = math.sin(spread_angle)
                     vx4 = vx * cs - vy * sn; vy4 = vx * sn + vy * cs
                     self.bullet_manager.spawn_bullet(self.x, self.y + 20, vx4, vy4, "enemy")
                
        elif self.type_id == 4: # Orbit
            if self.shoot_timer > 0.5 * fire_rate_mult:
                self.shoot_timer = 0
                angle = self.time * 2
                dx = math.cos(angle) * 200
                dy = math.sin(angle) * 200 + 200
                self.bullet_manager.spawn_bullet(self.x, self.y + 20, dx, dy, "enemy")

    def render(self):
        glPushMatrix()
        glTranslatef(self.x, self.y, 0)
        glRotatef(self.angle, 0, 0, 1) 
        
        # Define Colors (Neon Palette)
        if self.type_id == 0: color = (1.0, 0.2, 0.0) # Neon Red/Orange
        elif self.type_id == 1: color = (0.2, 1.0, 0.2) # Neon Green
        elif self.type_id == 2: color = (0.0, 0.8, 1.0) # Cyan
        elif self.type_id == 3: color = (1.0, 0.9, 0.0) # Gold
        elif self.type_id == 4: color = (1.0, 0.0, 1.0) # Magenta
        else: color = (1.0, 1.0, 1.0)
        
        # --- Glow Pass ---
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE) # Additive blending for glow
        
        glPushMatrix()
        glScalef(1.3, 1.3, 1.0) # Scale up for glow
        glColor4f(color[0], color[1], color[2], 0.5) # Semi-transparent
        
        glBegin(GL_TRIANGLES)
        glVertex2f(0, 20)
        glVertex2f(-15, -15)
        glVertex2f(15, -15)
        glEnd()
        glPopMatrix()
        
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA) # Restore blending
        
        # --- Core Pass ---
        glColor3f(color[0], color[1], color[2])
        
        # Draw Ship Shape (Arrow/Dart)
        glBegin(GL_TRIANGLES)
        glVertex2f(0, 20) # Tip (Up)
        glVertex2f(-15, -15)
        glVertex2f(15, -15)
        glEnd()
        
        # Inner detail (White core)
        glColor3f(1.0, 1.0, 1.0)
        glBegin(GL_TRIANGLES)
        glVertex2f(0, 10)
        glVertex2f(-5, -5)
        glVertex2f(5, -5)
        glEnd()
        
        glPopMatrix()
