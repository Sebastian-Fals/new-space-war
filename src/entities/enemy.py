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
        
    def update(self, dt):
        self.time += dt
        
        # Calculate Velocity based on type
        if self.type_id == 0: # Sine wave
            self.vy = 100
            self.vx = math.cos(self.time * 2) * 150
        elif self.type_id == 1: # Zigzag
            self.vy = 80
            self.vx = 100 if (int(self.time) % 2 == 0) else -100
        elif self.type_id == 2: # Kamikaze
            self.vy = 300 # Faster
            self.vx = 0
        elif self.type_id == 3: # Stop and shoot
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
            self.vx *= -1 # Bounce? Or just slide. Let's slide for now or reverse pattern.
        elif self.x > 1260:
            self.x = 1260
            
        # Calculate Target Angle
        if self.type_id == 3: # Stop and shoot - Face player? For now face down
            self.target_angle = 180
        elif abs(self.vx) > 10 or abs(self.vy) > 10:
            # Rotate towards movement vector
            # atan2 returns radians, convert to degrees. 
            # -90 offset because 0 degrees is usually right, but our sprites face up/down?
            # Actually standard math: 0 is Right, 90 is Up.
            # Our sprite points "Up" (triangle tip).
            # So if moving Down (270 deg), we want angle 270.
            # math.atan2(dy, dx)
            rads = math.atan2(self.vy, self.vx)
            degs = math.degrees(rads)
            self.target_angle = degs - 90 # Adjust for sprite orientation (Tip is Up)
            
        # Smooth Rotation
        # Shortest angle interpolation
        diff = (self.target_angle - self.angle + 180) % 360 - 180
        self.angle += diff * 5 * dt # Speed 5
        
        # Shooting logic
        self.shoot_timer += dt
        
        # Difficulty Multipliers for Shooting
        fire_rate_mult = 1.0
        if self.difficulty == 'easy': fire_rate_mult = 1.0
        elif self.difficulty == 'medium': fire_rate_mult = 0.7
        elif self.difficulty == 'hard': fire_rate_mult = 0.5
        elif self.difficulty == 'extreme': fire_rate_mult = 0.3
        
        # Fire rate and pattern based on type
        if self.type_id == 0: # Sine wave - Shoot straight down
            if self.shoot_timer > 1.5 * fire_rate_mult:
                self.shoot_timer = 0
                self.bullet_manager.spawn_bullet(self.x, self.y + 20, 0, 300, "enemy")
                
        elif self.type_id == 1: # Zigzag - Shoot 3-way (5-way on hard)
            if self.shoot_timer > 2.0 * fire_rate_mult:
                self.shoot_timer = 0
                self.bullet_manager.spawn_bullet(self.x, self.y + 20, 0, 300, "enemy")
                self.bullet_manager.spawn_bullet(self.x, self.y + 20, -100, 250, "enemy")
                self.bullet_manager.spawn_bullet(self.x, self.y + 20, 100, 250, "enemy")
                
                if self.difficulty in ['hard', 'extreme']:
                    self.bullet_manager.spawn_bullet(self.x, self.y + 20, -200, 200, "enemy")
                    self.bullet_manager.spawn_bullet(self.x, self.y + 20, 200, 200, "enemy")
                
                if self.difficulty == 'extreme': # Extreme: 7-way spread!
                    self.bullet_manager.spawn_bullet(self.x, self.y + 20, -300, 150, "enemy")
                    self.bullet_manager.spawn_bullet(self.x, self.y + 20, 300, 150, "enemy")
                
        elif self.type_id == 2: # Kamikaze - No shoot, just crash
            pass
            
        elif self.type_id == 3: # Stop and shoot - Aimed at player (simplified to down-ish for now)
            if self.shoot_timer > 1.0 * fire_rate_mult and self.time > 1.0: 
                self.shoot_timer = 0
                # Aim roughly down but spread
                import random
                spread = random.uniform(-50, 50)
                self.bullet_manager.spawn_bullet(self.x, self.y + 20, spread, 400, "enemy")
                
                if self.difficulty in ['hard', 'extreme']: # Double shot
                     self.bullet_manager.spawn_bullet(self.x, self.y + 20, spread - 30, 400, "enemy")
                     self.bullet_manager.spawn_bullet(self.x, self.y + 20, spread + 30, 400, "enemy")
                     
                if self.difficulty == 'extreme': # Triple shot (Center + Wide)
                     self.bullet_manager.spawn_bullet(self.x, self.y + 20, spread - 60, 350, "enemy")
                     self.bullet_manager.spawn_bullet(self.x, self.y + 20, spread + 60, 350, "enemy")
                
        elif self.type_id == 4: # Orbit - Spiral shot
            if self.shoot_timer > 0.5 * fire_rate_mult:
                self.shoot_timer = 0
                angle = self.time * 2
                dx = math.cos(angle) * 200
                dy = math.sin(angle) * 200 + 200 # Bias down
                self.bullet_manager.spawn_bullet(self.x, self.y + 20, dx, dy, "enemy")

    def render(self):
        glPushMatrix()
        glTranslatef(self.x, self.y, 0)
        
        glRotatef(self.angle, 0, 0, 1) 
        
        if self.type_id == 0: glColor3f(1.0, 0.0, 0.0)
        elif self.type_id == 1: glColor3f(0.0, 1.0, 0.0)
        elif self.type_id == 2: glColor3f(0.0, 0.0, 1.0)
        elif self.type_id == 3: glColor3f(1.0, 1.0, 0.0)
        elif self.type_id == 4: glColor3f(1.0, 0.0, 1.0)
        
        # Draw Ship Shape (Arrow/Dart)
        glBegin(GL_TRIANGLES)
        glVertex2f(0, 20) # Tip (Up)
        glVertex2f(-15, -15)
        glVertex2f(15, -15)
        glEnd()
        
        # Inner detail
        glColor3f(1.0, 1.0, 1.0)
        glBegin(GL_TRIANGLES)
        glVertex2f(0, 10)
        glVertex2f(-5, -5)
        glVertex2f(5, -5)
        glEnd()
        
        glPopMatrix()
