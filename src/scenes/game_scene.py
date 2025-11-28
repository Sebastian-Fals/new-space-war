import pygame
from src.scenes.scene_manager import Scene
from src.graphics.starfield import Starfield
from src.entities.player import Player
from src.entities.bullet_manager import BulletManager
from src.scenes.scene_manager import Scene
from src.graphics.starfield import Starfield
from src.entities.player import Player
from src.entities.bullet_manager import BulletManager
from src.core.wave_manager import WaveManager
from src.graphics.particle_system import ParticleSystem
from OpenGL.GL import *

class GameScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.starfield = Starfield(game.virtual_width, game.virtual_height)
        self.paused = False
        self.time = 0
        
        self.particle_system = ParticleSystem()
        
        # Initialize other components
        self.bullet_manager = BulletManager(self.particle_system)
        self.player = Player(game.virtual_width // 2, game.virtual_height // 2, self.bullet_manager)
        self.wave_manager = WaveManager(self)
        self.wave_manager.game = self
        
        from src.graphics.text_renderer import TextRenderer
        self.text_renderer = TextRenderer()
        
    def get_mouse_pos(self):
        mx, my = pygame.mouse.get_pos()
        
        # Calculate scale and offset (same as in render)
        vw, vh = self.game.virtual_width, self.game.virtual_height
        ww, wh = self.game.window.width, self.game.window.height
        
        scale = min(ww / vw, wh / vh)
        tx = (ww - vw * scale) / 2
        ty = (wh - vh * scale) / 2
        
        # Transform mouse to virtual coords
        vmx = (mx - tx) / scale
        vmy = (my - ty) / scale
        
        return vmx, vmy

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.paused = not self.paused
                
                if self.paused:
                    if event.key == pygame.K_q: # Quit to Menu
                        from src.scenes.menu_scene import MenuScene
                        self.game.scene_manager.set_scene(MenuScene(self.game))
                    elif event.key == pygame.K_r: # Restart
                        self.__init__(self.game)
                        
            if not self.paused:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1: # Left click
                        self.player.shoot()

    def update(self, dt):
        if self.paused:
            return
            
        self.time += dt
        
        # Update player with virtual mouse coordinates
        vmx, vmy = self.get_mouse_pos()
        self.player.update(dt, vmx, vmy)
        
        self.wave_manager.update(dt)
        self.bullet_manager.update(dt)
        self.particle_system.update(dt)
        
        # Collision Logic
        
        # Difficulty Multipliers
        diff = getattr(self.game, 'difficulty', 'medium')
        dmg_mult = 1.0
        if diff == 'easy': dmg_mult = 0.5
        elif diff == 'hard': dmg_mult = 1.5
        
        # Player Bullet -> Enemy
        for b in self.bullet_manager.bullets:
            if b["type"] == "player":
                for e in self.wave_manager.enemies:
                    if abs(b["x"] - e.x) < 32 and abs(b["y"] - e.y) < 32:
                        e.active = False
                        b["active"] = False
                        self.game.score += 100
                        
        # Enemy Bullet -> Player
        if self.player.invulnerable_timer <= 0:
            player_hit = False
            for b in self.bullet_manager.bullets:
                if b["type"] == "enemy":
                    if abs(b["x"] - self.player.x) < 16 and abs(b["y"] - self.player.y) < 16:
                        self.player.hp -= 10 * dmg_mult
                        b["active"] = False
                        player_hit = True
            
            # Enemy Body -> Player
            for e in self.wave_manager.enemies:
                if abs(e.x - self.player.x) < 32 and abs(e.y - self.player.y) < 32:
                    self.player.hp -= 20 * dmg_mult
                    e.active = False # Enemy crashes
                    player_hit = True
                    
            if player_hit:
                self.player.invulnerable_timer = 1.0 # 1 second invulnerability
                if self.player.hp <= 0:
                    # Game Over
                    print("GAME OVER")
                    # For now restart
                    self.__init__(self.game)
                        
        if self.wave_manager.boss:
            boss = self.wave_manager.boss
            for b in self.bullet_manager.bullets:
                if b["type"] == "player":
                     if abs(b["x"] - boss.x) < 50 and abs(b["y"] - boss.y) < 50:
                        boss.hp -= 1
                        b["active"] = False
                        if boss.hp <= 0:
                            boss.active = False
                            self.game.score += 5000

    def render(self):
        # Calculate scale factors
        vw, vh = self.game.virtual_width, self.game.virtual_height
        ww, wh = self.game.window.width, self.game.window.height
        
        scale = min(ww / vw, wh / vh)
        tx = (ww - vw * scale) / 2
        ty = (wh - vh * scale) / 2
        
        glPushMatrix()
        glTranslatef(tx, ty, 0)
        glScalef(scale, scale, 1.0)
        
        # Render Starfield
        self.starfield.render(self.time, (self.player.x, self.player.y))
import pygame
from src.scenes.scene_manager import Scene
from src.graphics.starfield import Starfield
from src.entities.player import Player
from src.entities.bullet_manager import BulletManager
from src.core.wave_manager import WaveManager
from src.graphics.particle_system import ParticleSystem
from src.ui.button import Button
from OpenGL.GL import *
import random

class GameScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.starfield = Starfield(game.virtual_width, game.virtual_height)
        self.paused = False
        self.time = 0
        
        self.particle_system = ParticleSystem()
        
        # UI Juice
        self.display_score = 0
        self.score_scale = 1.0
        self.shake_timer = 0
        self.shake_magnitude = 0
        
        # Initialize other components
        self.bullet_manager = BulletManager(self.particle_system)
        self.player = Player(game.virtual_width // 2, game.virtual_height // 2, self.bullet_manager)
        self.wave_manager = WaveManager(self)
        self.wave_manager.game = self
        
        self.boss_beaten = False
        
        from src.graphics.text_renderer import TextRenderer
        self.text_renderer = TextRenderer()
        
        # Pause Menu UI
        self.pause_buttons = []
        self.init_pause_menu()
        
    def init_pause_menu(self):
        # Create buttons with wrapped callbacks for effects
        def wrap(cb):
            return lambda: self.on_button_click(None, cb) 
            
        self.btn_resume = Button(0, 0, 200, 50, "RESUME", None, self.text_renderer)
        self.btn_restart = Button(0, 0, 200, 50, "RESTART", None, self.text_renderer)
        self.btn_quit = Button(0, 0, 200, 50, "QUIT", None, self.text_renderer)
        
        self.pause_buttons = [self.btn_resume, self.btn_restart, self.btn_quit]
        
        # Now assign callbacks with button reference
        self.btn_resume.callback = lambda: self.on_button_click(self.btn_resume, lambda: self.toggle_pause())
        self.btn_restart.callback = lambda: self.on_button_click(self.btn_restart, lambda: self.restart_game())
        self.btn_quit.callback = lambda: self.on_button_click(self.btn_quit, lambda: self.quit_to_menu())
             
        self.recalculate_layout()
        
    def recalculate_layout(self):
        cx = self.game.virtual_width // 2
        cy = self.game.virtual_height // 2
        
        # Center buttons vertically
        start_y = cy - 50
        spacing = 70
        
        self.btn_resume.x = cx - 100
        self.btn_resume.y = start_y
        
        self.btn_restart.x = cx - 100
        self.btn_restart.y = start_y + spacing
        
        self.btn_quit.x = cx - 100
        self.btn_quit.y = start_y + spacing * 2

    def on_button_click(self, button, callback):
        # Spawn particles
        for _ in range(20):
            # Spawn along the edges
            side = random.randint(0, 3)
            if side == 0: # Top
                px = button.x + random.random() * button.width
                py = button.y
                vx = (random.random() - 0.5) * 100
                vy = -random.random() * 100 - 50
            elif side == 1: # Bottom
                px = button.x + random.random() * button.width
                py = button.y + button.height
                vx = (random.random() - 0.5) * 100
                vy = random.random() * 100 + 50
            elif side == 2: # Left
                px = button.x
                py = button.y + random.random() * button.height
                vx = -random.random() * 100 - 50
                vy = (random.random() - 0.5) * 100
            else: # Right
                px = button.x + button.width
                py = button.y + random.random() * button.height
                vx = random.random() * 100 + 50
                vy = (random.random() - 0.5) * 100
                
            self.particle_system.emit(px, py, count=1, color=(0.5, 0.8, 1.0), vx=vx, vy=vy)
            
        # Execute action immediately (no delay needed for pause menu usually, but consistent feel is good)
        if callback:
            callback()

    def toggle_pause(self):
        self.paused = not self.paused
        
    def restart_game(self):
        self.__init__(self.game)
        
    def quit_to_menu(self):
        from src.scenes.menu_scene import MenuScene
        self.game.scene_manager.set_scene(MenuScene(self.game))

    def get_mouse_pos(self):
        mx, my = pygame.mouse.get_pos()
        
        # Calculate scale and offset (same as in render)
        vw, vh = self.game.virtual_width, self.game.virtual_height
        ww, wh = self.game.window.width, self.game.window.height
        
        scale = min(ww / vw, wh / vh)
        tx = (ww - vw * scale) / 2
        ty = (wh - vh * scale) / 2
        
        # Transform mouse to virtual coords
        vmx = (mx - tx) / scale
        vmy = (my - ty) / scale
        
        return vmx, vmy

    def handle_events(self, events):
        # Always handle resize/quit
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.toggle_pause()
                    
        if self.paused:
            vmx, vmy = self.get_mouse_pos()
            for btn in self.pause_buttons:
                btn.update(0, events, vmx, vmy)
        else:
            for event in events:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 3: # Right click
                        self.player.shoot()

    def trigger_shake(self, magnitude, duration):
        self.shake_magnitude = magnitude
        self.shake_timer = duration

    def update(self, dt):
        if self.paused:
            # Update UI animations
            vmx, vmy = self.get_mouse_pos()
            for btn in self.pause_buttons:
                btn.update(dt, [], vmx, vmy) # Pass empty events to just update anims
            
            self.particle_system.update(dt)
            return
            
        self.time += dt
        
        # Update Juice
        # Score Rolling
        diff = self.game.score - self.display_score
        if abs(diff) > 0:
            self.display_score += diff * 5 * dt
            if abs(self.game.score - self.display_score) < 1:
                self.display_score = self.game.score
                
        # Score Pulse Decay
        self.score_scale += (1.0 - self.score_scale) * 5 * dt
        
        # Screen Shake
        if self.shake_timer > 0:
            self.shake_timer -= dt
            if self.shake_timer <= 0:
                self.shake_magnitude = 0
        
        # Update player with virtual mouse coordinates
        vmx, vmy = self.get_mouse_pos()
        self.player.update(dt, vmx, vmy)
        
        self.wave_manager.update(dt)
        self.bullet_manager.update(dt)
        self.particle_system.update(dt)
        
        # Collision Logic
        
        # Difficulty Multipliers
        diff = getattr(self.game, 'difficulty', 'medium')
        dmg_mult = 1.0
        if diff == 'easy': dmg_mult = 1.0
        elif diff == 'medium': dmg_mult = 1.5
        elif diff == 'hard': dmg_mult = 2.0
        elif diff == 'extreme': dmg_mult = 3.0
        
        # Player Bullet -> Enemy
        for b in self.bullet_manager.bullets:
            if b["type"] == "player":
                for e in self.wave_manager.enemies:
                    if abs(b["x"] - e.x) < 32 and abs(b["y"] - e.y) < 32:
                        e.active = False
                        b["active"] = False
                        self.game.score += 100
                        self.score_scale = 1.5 # Pulse score
                        self.trigger_shake(5, 0.2) # Shake screen
                        
        # Enemy Bullet -> Player
        if self.player.invulnerable_timer <= 0:
            player_hit = False
            for b in self.bullet_manager.bullets:
                if b["type"] == "enemy":
                    if abs(b["x"] - self.player.x) < 16 and abs(b["y"] - self.player.y) < 16:
                        self.player.hp -= 10 * dmg_mult
                        b["active"] = False
                        player_hit = True
            
            # Enemy Body -> Player
            for e in self.wave_manager.enemies:
                if abs(e.x - self.player.x) < 32 and abs(e.y - self.player.y) < 32:
                    self.player.hp -= 20 * dmg_mult
                    e.active = False # Enemy crashes
                    player_hit = True
                    
            if player_hit:
                self.player.invulnerable_timer = 1.0 # 1 second invulnerability
                self.trigger_shake(10, 0.4) # Big shake on hit
                if self.player.hp <= 0:
                    # Game Over
                    print("GAME OVER")
                    from src.scenes.game_over_scene import GameOverScene
                    self.game.scene_manager.set_scene(GameOverScene(self.game, self.game.score, self.wave_manager.wave, self.boss_beaten))
                        
        if self.wave_manager.boss:
            boss = self.wave_manager.boss
            for b in self.bullet_manager.bullets:
                if b["type"] == "player":
                     if abs(b["x"] - boss.x) < 50 and abs(b["y"] - boss.y) < 50:
                        boss.hp -= 1
                        b["active"] = False
                        if boss.hp <= 0:
                            boss.active = False
                            self.boss_beaten = True
                            self.game.score += 5000
                            self.score_scale = 2.0
                            self.trigger_shake(20, 1.0) # Massive shake on boss death

    def render(self):
        # Calculate scale factors
        vw, vh = self.game.virtual_width, self.game.virtual_height
        ww, wh = self.game.window.width, self.game.window.height
        
        scale = min(ww / vw, wh / vh)
        tx = (ww - vw * scale) / 2
        ty = (wh - vh * scale) / 2
        
        glPushMatrix()
        glTranslatef(tx, ty, 0)
        glScalef(scale, scale, 1.0)
        
        # Apply Screen Shake
        if self.shake_timer > 0:
            sx = (random.random() - 0.5) * self.shake_magnitude
            sy = (random.random() - 0.5) * self.shake_magnitude
            glTranslatef(sx, sy, 0)
        
        # Render Starfield
        self.starfield.render(self.time, (self.player.x, self.player.y))
        
        # Render Entities
        self.particle_system.render()
        self.wave_manager.render()
        self.player.render()
        self.bullet_manager.render()
        
        # Render UI (Health Bar) - In Virtual Space (Scaled)
        glDisable(GL_TEXTURE_2D)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        # Health Bar - Top Left
        bar_x, bar_y = 20, 20
        bar_w, bar_h = 250, 25
        
        # Bar Background (Dark Grey)
        glColor4f(0.1, 0.1, 0.1, 0.8)
        glBegin(GL_QUADS)
        glVertex2f(bar_x, bar_y)
        glVertex2f(bar_x + bar_w, bar_y)
        glVertex2f(bar_x + bar_w, bar_y + bar_h)
        glVertex2f(bar_x, bar_y + bar_h)
        glEnd()
        
        # Health Fill (Gradient Green to Red)
        hp_percent = max(0, self.player.hp / self.player.max_hp)
        fill_w = bar_w * hp_percent
        
        # Color based on HP
        if hp_percent > 0.6:
            glColor4f(0.0, 1.0, 0.2, 1.0) # Green
        elif hp_percent > 0.3:
            glColor4f(1.0, 1.0, 0.0, 1.0) # Yellow
        else:
            glColor4f(1.0, 0.0, 0.0, 1.0) # Red
            
        glBegin(GL_QUADS)
        glVertex2f(bar_x, bar_y)
        glVertex2f(bar_x + fill_w, bar_y)
        glVertex2f(bar_x + fill_w, bar_y + bar_h)
        glVertex2f(bar_x, bar_y + bar_h)
        glEnd()
        
        # Bar Border (White)
        glLineWidth(2)
        glColor4f(1.0, 1.0, 1.0, 1.0)
        glBegin(GL_LINE_LOOP)
        glVertex2f(bar_x, bar_y)
        glVertex2f(bar_x + bar_w, bar_y)
        glVertex2f(bar_x + bar_w, bar_y + bar_h)
        glVertex2f(bar_x, bar_y + bar_h)
        glEnd()
        
        # Score Panel with Pulse
        score_text = f"SCORE: {int(self.display_score)}"
        sw, sh = self.text_renderer.measure_text(score_text)
        panel_x = 20
        panel_y = 60
        
        # Score Background
        glColor4f(0.0, 0.0, 0.0, 0.5)
        glBegin(GL_QUADS)
        glVertex2f(panel_x - 5, panel_y - 5)
        glVertex2f(panel_x + sw + 15, panel_y - 5)
        glVertex2f(panel_x + sw + 15, panel_y + sh + 5)
        glVertex2f(panel_x - 5, panel_y + sh + 5)
        glEnd()
        
        # Render Score Text with Scaling
        glPushMatrix()
        # Center of scaling
        scx = panel_x + sw / 2
        scy = panel_y + sh / 2
        glTranslatef(scx, scy, 0)
        glScalef(self.score_scale, self.score_scale, 1.0)
        glTranslatef(-scx, -scy, 0)
        
        self.text_renderer.render_text(score_text, panel_x, panel_y, (255, 255, 255))
        glPopMatrix()
        
        # Wave UI
        wave_text = f"WAVE {self.wave_manager.wave}"
        
        # Calculate target badge position (Top Right)
        tw, th = self.text_renderer.measure_text(wave_text)
        badge_x = self.game.virtual_width - tw - 40
        badge_y = 20
        badge_w = tw + 20
        badge_h = th + 10
        
        # Center Position
        cx, cy = self.game.virtual_width // 2, self.game.virtual_height // 2
        
        if self.wave_manager.wave_timer < 3.0: 
             # Animation Phases
             t = self.wave_manager.wave_timer
             
             current_x, current_y = cx - tw // 2, cy
             current_scale = 1.0
             current_color = (1.0, 1.0, 1.0, 1.0)
             show_alert = False
             
             if t < 0.5: 
                 # Phase 1: Slam Entrance (0.0 - 0.5s)
                 # Scale 3.0 -> 1.5
                 progress = t / 0.5
                 current_scale = 3.0 - 1.5 * progress
                 current_color = (1.0, 0.84, 0.0, progress) # Fade in Gold
                 
             elif t < 2.0:
                 # Phase 2: Alert Pulse (0.5s - 2.0s)
                 # Scale Pulse 1.5 -> 1.6 -> 1.5
                 pulse_t = (t - 0.5) * 4 # Speed multiplier
                 import math
                 pulse = 0.1 * math.sin(pulse_t)
                 current_scale = 1.5 + pulse
                 
                 # Color Pulse: Red -> Orange
                 # Red: (1.0, 0.0, 0.0)
                 # Orange: (1.0, 0.5, 0.0)
                 color_t = (math.sin(pulse_t * 2) + 1) / 2 # 0 to 1
                 current_color = (1.0, 0.5 * color_t, 0.0, 1.0)
                 show_alert = True
                 
             else:
                 # Phase 3: Exit to Badge (2.0s - 3.0s)
                 # Interpolate Position: Center -> Badge
                 # Interpolate Scale: 1.5 -> 1.0
                 progress = (t - 2.0) / 1.0
                 # Ease in out
                 progress = progress * progress * (3 - 2 * progress)
                 
                 start_x = cx - tw // 2
                 start_y = cy
                 end_x = badge_x + 10
                 end_y = badge_y + 5
                 
                 current_x = start_x + (end_x - start_x) * progress
                 current_y = start_y + (end_y - start_y) * progress
                 current_scale = 1.5 - 0.5 * progress
                 current_color = (1.0, 1.0, 1.0, 1.0) # Back to white
                 
             # Render Wave Text
             glPushMatrix()
             # Scale around center of text
             text_cx = current_x + tw / 2
             text_cy = current_y + th / 2
             glTranslatef(text_cx, text_cy, 0)
             glScalef(current_scale, current_scale, 1.0)
             glTranslatef(-text_cx, -text_cy, 0)
             
             self.text_renderer.render_text(wave_text, current_x, current_y, current_color)
             
             if show_alert:
                 # Render "GET READY" below
                 alert_text = "GET READY"
                 aw, ah = self.text_renderer.measure_text(alert_text)
                 # Pulse alpha
                 alpha = (math.sin(t * 10) + 1) / 2 * 0.5 + 0.5
                 self.text_renderer.render_text(alert_text, cx - aw // 2, cy + 60, (1.0, 0.2, 0.2, alpha))
                 
             glPopMatrix()
             
        else:
             # Persistent Badge (Top Right)
             
             # Badge Background
             glColor4f(0.2, 0.2, 0.8, 0.6) # Blueish
             glBegin(GL_QUADS)
             glVertex2f(badge_x, badge_y)
             glVertex2f(badge_x + badge_w, badge_y)
             glVertex2f(badge_x + badge_w, badge_y + badge_h)
             glVertex2f(badge_x, badge_y + badge_h)
             glEnd()
             
             # Badge Border
             glLineWidth(2)
             glColor4f(0.5, 0.5, 1.0, 1.0)
             glBegin(GL_LINE_LOOP)
             glVertex2f(badge_x, badge_y)
             glVertex2f(badge_x + badge_w, badge_y)
             glVertex2f(badge_x + badge_w, badge_y + badge_h)
             glVertex2f(badge_x, badge_y + badge_h)
             glEnd()
             
             self.text_renderer.render_text(wave_text, badge_x + 10, badge_y + 5, (255, 255, 255))
             
        if self.paused:
            # Draw Pause Overlay
            # Fullscreen dark overlay
            glDisable(GL_TEXTURE_2D)
            glEnable(GL_BLEND)
            glColor4f(0.0, 0.0, 0.0, 0.7)
            glBegin(GL_QUADS)
            glVertex2f(0, 0)
            glVertex2f(self.game.virtual_width, 0)
            glVertex2f(self.game.virtual_width, self.game.virtual_height)
            glVertex2f(0, self.game.virtual_height)
            glEnd()
            
            # Panel Background
            cx, cy = self.game.virtual_width // 2, self.game.virtual_height // 2
            panel_w, panel_h = 300, 400
            panel_x = cx - panel_w // 2
            panel_y = cy - panel_h // 2
            
            glColor4f(0.0, 0.1, 0.2, 0.9) # Dark Blue
            glBegin(GL_QUADS)
            glVertex2f(panel_x, panel_y)
            glVertex2f(panel_x + panel_w, panel_y)
            glVertex2f(panel_x + panel_w, panel_y + panel_h)
            glVertex2f(panel_x, panel_y + panel_h)
            glEnd()
            
            # Panel Border
            glLineWidth(2)
            glColor4f(0.0, 0.8, 1.0, 1.0) # Cyan
            glBegin(GL_LINE_LOOP)
            glVertex2f(panel_x, panel_y)
            glVertex2f(panel_x + panel_w, panel_y)
            glVertex2f(panel_x + panel_w, panel_y + panel_h)
            glVertex2f(panel_x, panel_y + panel_h)
            glEnd()
            
            # Title
            title_text = "PAUSED"
            tw, th = self.text_renderer.measure_text(title_text)
            self.text_renderer.render_text(title_text, cx - tw // 2, panel_y + 40, (255, 255, 255))
            
            # Buttons
            for btn in self.pause_buttons:
                btn.render()
                
        glPopMatrix()
