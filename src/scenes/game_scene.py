import pygame
from src.scenes.scene_manager import Scene
from src.graphics.starfield import Starfield
from src.entities.player import Player
from src.entities.bullet_manager import BulletManager
from src.core.wave_manager import WaveManager
from src.graphics.particle_system import ParticleSystem
from src.ui.button import Button
from src.utils.spatial_grid import SpatialGrid
from OpenGL.GL import *
import random

class GameScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.game.score = 0 # Reset score
        self.game.audio_manager.play_music("game", force_restart=True)
        self.starfield = Starfield(game.virtual_width, game.virtual_height)
        self.paused = False
        self.time = 0
        
        self.particle_system = ParticleSystem()
        self.grid = SpatialGrid(game.virtual_width, game.virtual_height, 100)
        
        # UI Juice
        self.display_score = 0
        self.score_scale = 1.0
        self.shake_timer = 0
        self.shake_magnitude = 0
        
        # Initialize other components
        self.bullet_manager = BulletManager(self.particle_system)
        self.player = Player(game.virtual_width // 2, game.virtual_height // 2, self.bullet_manager)
        self.displayed_hp = self.player.hp # Initialize for lerp
        self.wave_manager = WaveManager(self)
        self.wave_manager.game = self
        
        self.boss_beaten = False
        
        from src.graphics.text_renderer import TextRenderer
        self.text_renderer = TextRenderer()
        
        # Pause Menu UI
        self.pause_buttons = []
        self.init_pause_menu()
        
        # Hide mouse and grab input
        pygame.mouse.set_visible(False)
        pygame.event.set_grab(True)
        
    def init_pause_menu(self):
        # Create buttons with wrapped callbacks for effects
        def wrap(cb):
            return lambda: self.on_button_click(None, cb) 
            
        self.btn_resume = Button(0, 0, 200, 50, self.game.localization.get("resume").upper(), None, self.text_renderer)
        self.btn_restart = Button(0, 0, 200, 50, self.game.localization.get("restart").upper(), None, self.text_renderer)
        self.btn_quit = Button(0, 0, 200, 50, self.game.localization.get("main_menu").upper(), None, self.text_renderer)
        
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
        if self.paused:
            pygame.mouse.set_visible(True)
            pygame.event.set_grab(False)
        else:
            pygame.mouse.set_visible(False)
            pygame.event.set_grab(True)
        
    def restart_game(self):
        self.__init__(self.game)
        
    def quit_to_menu(self):
        pygame.mouse.set_visible(True)
        pygame.event.set_grab(False)
        from src.scenes.menu_scene import MenuScene
        self.game.scene_manager.set_scene(MenuScene(self.game))

    def get_mouse_pos(self):
        return self.game.input_manager.get_mouse_pos()

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
        
        # Health Bar Lerp
        hp_diff = self.player.hp - self.displayed_hp
        if abs(hp_diff) > 0.1:
            self.displayed_hp += hp_diff * 5 * dt
        else:
            self.displayed_hp = self.player.hp
        
        # Screen Shake
        if self.shake_timer > 0:
            self.shake_timer -= dt
            if self.shake_timer <= 0:
                self.shake_magnitude = 0
        
        # Store Player Previous Position for CCD
        player_prev_x, player_prev_y = self.player.x, self.player.y
        
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
        
        # Update Spatial Grid
        self.grid.clear()
        for e in self.wave_manager.enemies:
            if e.active:
                self.grid.insert(e)
        
        # Helper for Line-Circle Intersection
        def line_intersects_circle(p1, p2, center, radius):
            # p1, p2: (x, y) tuples
            # center: (cx, cy) tuple
            # radius: float
            x1, y1 = p1
            x2, y2 = p2
            cx, cy = center
            
            dx, dy = x2 - x1, y2 - y1
            if dx == 0 and dy == 0:
                return (x1 - cx)**2 + (y1 - cy)**2 <= radius**2
                
            # t = ((cx - x1) * dx + (cy - y1) * dy) / (dx*dx + dy*dy)
            t = ((cx - x1) * dx + (cy - y1) * dy) / (dx*dx + dy*dy)
            t = max(0, min(1, t)) # Clamp to segment
            
            closest_x = x1 + t * dx
            closest_y = y1 + t * dy
            
            dist_sq = (closest_x - cx)**2 + (closest_y - cy)**2
            return dist_sq <= radius**2

        # Player Bullet -> Enemy (CCD)
        # Iterate active player bullets (numpy)
        for i in range(self.bullet_manager.p_count):
            bx = self.bullet_manager.p_data[i, 0]
            by = self.bullet_manager.p_data[i, 1]
            bdx = self.bullet_manager.p_data[i, 2]
            bdy = self.bullet_manager.p_data[i, 3]
            
            # Previous position
            prev_bx = bx - bdx * dt
            prev_by = by - bdy * dt
            
            # Query grid around the segment bounding box
            min_x, max_x = min(prev_bx, bx), max(prev_bx, bx)
            min_y, max_y = min(prev_by, by), max(prev_by, by)
            
            # Simplified query: just query around current pos + margin?
            # Or query around midpoint?
            # Let's query around current pos with a larger radius to catch fast movers?
            # Or just query standard size but check intersection.
            # Grid query is coarse anyway.
            potential_hits = self.grid.query(bx, by, 64, 64) # Increased range
            
            for e in potential_hits:
                if e.active:
                    # Check CCD
                    if line_intersects_circle((prev_bx, prev_by), (bx, by), (e.x, e.y), 20): # Enemy radius ~20
                        e.active = False
                        self.bullet_manager.p_data[i, 1] = -1000 # Move offscreen to remove
                        self.game.score += 100
                        self.score_scale = 1.5
                        self.trigger_shake(5, 0.2)
                        break # Bullet hits one enemy
                        
        # Enemy Bullet -> Player (CCD)
        if self.player.invulnerable_timer <= 0:
            player_hit = False
            px, py = self.player.x, self.player.y
            
            for i in range(self.bullet_manager.e_count):
                bx = self.bullet_manager.e_data[i, 0]
                by = self.bullet_manager.e_data[i, 1]
                bdx = self.bullet_manager.e_data[i, 2]
                bdy = self.bullet_manager.e_data[i, 3]
                
                prev_bx = bx - bdx * dt
                prev_by = by - bdy * dt
                
                # Player radius ~15
                if line_intersects_circle((prev_bx, prev_by), (bx, by), (px, py), self.player.hitbox_radius):
                    self.player.hp -= 10 * dmg_mult
                    self.bullet_manager.e_data[i, 1] = -1000 # Remove
                    player_hit = True
            
            # Enemy Body -> Player (CCD)
            # Check intersection of Player Movement Segment with Enemy Circle
            # Player moved from (player_prev_x, player_prev_y) to (px, py)
            for e in self.wave_manager.enemies:
                if e.active:
                    # Check if Player path intersects Enemy
                    # Also check if Enemy path intersects Player? (Both moving)
                    # For simplicity, assume Enemy is static during frame relative to fast player?
                    # Or just check distance.
                    # Let's use CCD for player path vs Enemy Circle.
                    if line_intersects_circle((player_prev_x, player_prev_y), (px, py), (e.x, e.y), 20 + self.player.hitbox_radius): # Combined radius (Enemy ~20)
                        self.player.hp -= 40 * dmg_mult # Double damage (4x bullet)
                        e.active = False # Enemy crashes/destroyed
                        player_hit = True
                        self.trigger_shake(20, 0.5) # Big shake
                    
            if player_hit:
                self.player.invulnerable_timer = 1.0 # 1 second invulnerability
                self.trigger_shake(10, 0.4)
                if self.player.hp <= 0:
                    # Game Over
                    if self.game.score > self.game.high_score:
                        self.game.high_score = self.game.score
                        self.game.save_settings()
                    
                    print("GAME OVER")
                    from src.scenes.game_over_scene import GameOverScene
                    self.game.scene_manager.set_scene(GameOverScene(self.game, self.game.score, self.wave_manager.wave, self.boss_beaten))
                        
        if self.wave_manager.boss:
            boss = self.wave_manager.boss
            if boss.active:
                for i in range(self.bullet_manager.p_count):
                     bx = self.bullet_manager.p_data[i, 0]
                     by = self.bullet_manager.p_data[i, 1]
                     bdx = self.bullet_manager.p_data[i, 2]
                     bdy = self.bullet_manager.p_data[i, 3]
                     
                     prev_bx = bx - bdx * dt
                     prev_by = by - bdy * dt
                     
                     if line_intersects_circle((prev_bx, prev_by), (bx, by), (boss.x, boss.y), 50):
                        boss.hp -= 1
                        self.bullet_manager.p_data[i, 1] = -1000 # Remove
                        if boss.hp <= 0:
                            boss.active = False
                            self.boss_beaten = True
                            self.game.score += 5000
                            self.score_scale = 2.0
                            self.trigger_shake(20, 1.0)

    def render(self):
        # Calculate scale factors
        vw, vh = self.game.virtual_width, self.game.virtual_height
        ww, wh = self.game.window.width, self.game.window.height
        
        scale = min(ww / vw, wh / vh)
        tx = (ww - vw * scale) / 2
        ty = (wh - vh * scale) / 2
        
        # Setup Legacy Projection
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, ww, wh, 0, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
        # Scissor Test to clip legacy rendering to virtual viewport
        glEnable(GL_SCISSOR_TEST)
        glScissor(int(tx), int(ty), int(vw * scale), int(vh * scale))
        
        # --- POST PROCESSING START ---
        # Capture World Rendering
        self.game.post_processor.begin_capture()
        
        # We need to clear the FBO (it has its own clear color)
        # But wait, begin_capture clears it.
        # We need to setup projection for the FBO?
        # The FBO is size of window.
        # Legacy projection is setup for window size (0..ww, 0..wh).
        # So rendering should work fine.
        
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
        self.particle_system.render(scale)
        self.wave_manager.render()
        self.player.render()
        self.bullet_manager.render()
        
        glPopMatrix()
        
        self.game.post_processor.end_capture()
        # --- POST PROCESSING END ---
        
        glDisable(GL_SCISSOR_TEST)
        
        # Render Post-Processed Scene to Screen
        # We might want to apply scissor here too if we want black bars?
        # PostProcessor renders full screen quad.
        # If we want letterboxing, we should render quad inside the viewport?
        # Or just render full screen and let the black bars be black (cleared screen).
        # But PostProcessor texture contains the whole window content (including black bars area if we cleared it black).
        # Wait, we rendered to FBO with scissor test. So FBO has content only in viewport area.
        # So rendering full screen quad of FBO texture will show the content correctly.
        
        self.game.post_processor.render()
        
        # Render UI (Health Bar) - In Virtual Space (Scaled)
        # glDisable(GL_TEXTURE_2D)
        # glEnable(GL_BLEND)
        # glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        renderer = self.game.renderer
        renderer.begin_frame(self.game.virtual_width, self.game.virtual_height, self.game.window.width, self.game.window.height)
        
        # Health Bar - Top Left
        bar_x, bar_y = 20, 20
        bar_w, bar_h = 250, 25
        
        # Bar Background (Dark Grey)
        renderer.draw_rect(bar_x, bar_y, bar_w, bar_h, (0.1, 0.1, 0.1, 0.8))
        
        # Health Fill (Gradient Green to Red)
        hp_percent = max(0, self.displayed_hp / self.player.max_hp)
        fill_w = bar_w * hp_percent
        
        # Smooth Color Lerp (Red -> Yellow -> Green)
        if hp_percent > 0.5:
            # Yellow to Green (0.5 to 1.0)
            t = (hp_percent - 0.5) * 2
            # Yellow (1, 1, 0) -> Green (0, 1, 0.2)
            r = 1.0 * (1 - t) + 0.0 * t
            g = 1.0 # Both are 1.0
            b = 0.0 * (1 - t) + 0.2 * t
            color = (r, g, b, 1.0)
        else:
            # Red to Yellow (0.0 to 0.5)
            t = hp_percent * 2
            # Red (1, 0, 0) -> Yellow (1, 1, 0)
            r = 1.0
            g = 0.0 * (1 - t) + 1.0 * t
            b = 0.0
            color = (r, g, b, 1.0)
            
        renderer.draw_rect(bar_x, bar_y, fill_w, bar_h, color)
        
        # Bar Border (White)
        # renderer.draw_rect_outline(bar_x, bar_y, bar_w, bar_h, (1.0, 1.0, 1.0, 1.0), 2)
        # Simulate border with larger rect behind? No, we are drawing on top.
        # Draw 4 lines or just skip border for now?
        # Let's skip border or implement draw_rect_outline in Renderer2D later.
        # For now, just draw a slightly larger white rect behind?
        # But we already drew background.
        # Let's draw 4 thin rects for border.
        border_thickness = 2
        border_color = (1.0, 1.0, 1.0, 1.0)
        # Top
        renderer.draw_rect(bar_x, bar_y, bar_w, border_thickness, border_color)
        # Bottom
        renderer.draw_rect(bar_x, bar_y + bar_h - border_thickness, bar_w, border_thickness, border_color)
        # Left
        renderer.draw_rect(bar_x, bar_y, border_thickness, bar_h, border_color)
        # Right
        renderer.draw_rect(bar_x + bar_w - border_thickness, bar_y, border_thickness, bar_h, border_color)
        
        # Score Panel with Pulse
        score_lbl = self.game.localization.get("score")
        score_text = f"{score_lbl}: {int(self.display_score)}"
        sw, sh = self.text_renderer.measure_text(score_text)
        panel_x = 20
        panel_y = 60
        
        # Score Background
        renderer.draw_rect(panel_x - 5, panel_y - 5, sw + 20, sh + 10, (0.0, 0.0, 0.0, 0.5))
        
        # Render Score Text with Scaling
        # Renderer2D doesn't support scaling text yet (except via font size or separate draw calls).
        # But we can use the model matrix in Renderer2D if we expose it?
        # Or just ignore scaling for now?
        # The scaling is for "juice" (pulse effect).
        # TextRenderer uses Renderer2D.draw_texture.
        # Renderer2D.draw_texture draws a quad.
        # We can implement scaling in TextRenderer or Renderer2D.
        # For now, let's just render without scaling to avoid complexity, or implement a simple scale in TextRenderer?
        # TextRenderer.render_text calls renderer.draw_texture.
        # We can add a scale parameter to render_text?
        # Let's just render it normally for now.
        
        self.text_renderer.render_text(renderer, score_text, panel_x, panel_y, (255, 255, 255))
        
        # Wave UI
        wave_lbl = self.game.localization.get("wave_reached").replace("REACHED", "").strip() # Reuse key or just "WAVE"
        # Actually let's use a simple "WAVE" if possible, but for now reuse
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
             # Ignoring scale for now
             self.text_renderer.render_text(renderer, wave_text, current_x, current_y, current_color)
             
             if show_alert:
                 # Render "GET READY" below
                 alert_text = "GET READY"
                 aw, ah = self.text_renderer.measure_text(alert_text)
                 # Pulse alpha
                 alpha = (math.sin(t * 10) + 1) / 2 * 0.5 + 0.5
                 self.text_renderer.render_text(renderer, alert_text, cx - aw // 2, cy + 60, (1.0, 0.2, 0.2, alpha))
             
        else:
             # Persistent Badge (Top Right)
             
             # Badge Background
             renderer.draw_rect(badge_x, badge_y, badge_w, badge_h, (0.2, 0.2, 0.8, 0.6))
             
             # Badge Border
             renderer.draw_rect(badge_x, badge_y, badge_w, 2, (0.5, 0.5, 1.0, 1.0)) # Top
             renderer.draw_rect(badge_x, badge_y + badge_h - 2, badge_w, 2, (0.5, 0.5, 1.0, 1.0)) # Bottom
             renderer.draw_rect(badge_x, badge_y, 2, badge_h, (0.5, 0.5, 1.0, 1.0)) # Left
             renderer.draw_rect(badge_x + badge_w - 2, badge_y, 2, badge_h, (0.5, 0.5, 1.0, 1.0)) # Right
             
             self.text_renderer.render_text(renderer, wave_text, badge_x + 10, badge_y + 5, (255, 255, 255))
             
        if self.paused:
            # Draw Pause Overlay
            # Fullscreen dark overlay
            # glDisable(GL_TEXTURE_2D)
            # glEnable(GL_BLEND)
            renderer.draw_rect(0, 0, self.game.virtual_width, self.game.virtual_height, (0.0, 0.0, 0.0, 0.7))
            
            # Panel Background
            cx, cy = self.game.virtual_width // 2, self.game.virtual_height // 2
            panel_w, panel_h = 300, 400
            panel_x = cx - panel_w // 2
            panel_y = cy - panel_h // 2
            
            # Panel Background (Gradient)
            # renderer.draw_chamfered_rect(panel_x, panel_y, panel_w, panel_h, (0.05, 0.1, 0.25, 0.9), radius=10, gradient_bot=(0.02, 0.05, 0.15, 0.95))
            # Renderer2D doesn't support gradient_bot yet in draw_chamfered_rect call?
            # Wait, I implemented draw_chamfered_rect in Renderer2D but I didn't check if it supports gradient.
            # I implemented it with a single color.
            # So let's just use single color for now.
            renderer.draw_chamfered_rect(panel_x, panel_y, panel_w, panel_h, (0.05, 0.1, 0.25, 0.9), radius=10)
            
            # Panel Border (Glowing Cyan)
            renderer.draw_chamfered_rect(panel_x - 3, panel_y - 3, panel_w + 6, panel_h + 6, (0.0, 0.8, 1.0, 0.8), radius=10)
            renderer.draw_chamfered_rect(panel_x, panel_y, panel_w, panel_h, (0.05, 0.1, 0.25, 0.9), radius=10)
            
            # Title
            title_text = self.game.localization.get("paused")
            tw, th = self.text_renderer.measure_text(title_text)
            self.text_renderer.render_text(renderer, title_text, cx - tw // 2, panel_y + 40, (255, 255, 255))
            
            # Buttons
            for btn in self.pause_buttons:
                btn.render(renderer)
                
        renderer.end_frame()
        
        # glPopMatrix() # Removed because we are not using glPushMatrix for UI anymore (Renderer2D handles it)
        # But wait, we used glPushMatrix at start of render() for the legacy world rendering.
        # We need to pop it!
        # But we called renderer.begin_frame() which sets up its own projection.
        # Does renderer.end_frame() restore the previous projection? No.
        # But we are at the end of render().
        # The legacy glPopMatrix corresponds to the glPushMatrix at line 285.
        # We should pop it to be clean, although next frame will reset.
        # However, Renderer2D uses a shader, so the fixed function matrix stack is ignored during Renderer2D pass.
        # But we should pop it for correctness if we are mixing.
        
        # glPopMatrix() # Removed extra pop
