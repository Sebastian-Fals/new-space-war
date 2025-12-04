import random
import math
from OpenGL.GL import *

class GameHUD:
    def __init__(self, game_scene):
        self.game_scene = game_scene
        self.game = game_scene.game
        self.text_renderer = game_scene.text_renderer
        
    def render(self, renderer):
        self.render_health_bar(renderer)
        self.render_score(renderer)
        self.render_wave_badge(renderer)
        
        if self.game_scene.paused:
            self.render_pause_menu(renderer)
            
    def render_health_bar(self, renderer):
        # Health Bar - Top Left
        bar_x, bar_y = 20, 20
        bar_w, bar_h = 250, 25
        
        # Bar Background (Dark Grey)
        renderer.draw_rect(bar_x, bar_y, bar_w, bar_h, (0.1, 0.1, 0.1, 0.8))
        
        # Health Fill (Gradient Green to Red)
        hp_percent = max(0, self.game_scene.displayed_hp / self.game_scene.player.max_hp)
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

    def render_score(self, renderer):
        # Score Panel with Pulse
        score_lbl = self.game.localization.get("score")
        score_text = f"{score_lbl}: {int(self.game_scene.display_score)}"
        sw, sh = self.text_renderer.measure_text(score_text)
        panel_x = 20
        panel_y = 60
        
        # Score Background
        renderer.draw_rect(panel_x - 5, panel_y - 5, sw + 20, sh + 10, (0.0, 0.0, 0.0, 0.5))
        
        self.text_renderer.render_text(renderer, score_text, panel_x, panel_y, (255, 255, 255))

    def render_wave_badge(self, renderer):
        # Wave UI
        wave_lbl = self.game.localization.get("wave_reached").replace("REACHED", "").strip()
        wave_text = f"WAVE {self.game_scene.wave_manager.wave}"
        
        # Calculate target badge position (Top Right)
        tw, th = self.text_renderer.measure_text(wave_text)
        badge_x = self.game.virtual_width - tw - 40
        badge_y = 20
        badge_w = tw + 20
        badge_h = th + 10
        
        # Center Position
        cx, cy = self.game.virtual_width // 2, self.game.virtual_height // 2
        
        if self.game_scene.wave_manager.wave_timer < 3.0: 
             # Animation Phases
             t = self.game_scene.wave_manager.wave_timer
             
             current_x, current_y = cx - tw // 2, cy
             current_scale = 1.0
             current_color = (1.0, 1.0, 1.0, 1.0)
             show_alert = False
             
             if t < 0.5: 
                 # Phase 1: Slam Entrance (0.0 - 0.5s)
                 progress = t / 0.5
                 current_scale = 3.0 - 1.5 * progress
                 current_color = (1.0, 0.84, 0.0, progress) # Fade in Gold
                 
             elif t < 2.0:
                 # Phase 2: Alert Pulse (0.5s - 2.0s)
                 pulse_t = (t - 0.5) * 4 # Speed multiplier
                 pulse = 0.1 * math.sin(pulse_t)
                 current_scale = 1.5 + pulse
                 
                 # Color Pulse: Red -> Orange
                 color_t = (math.sin(pulse_t * 2) + 1) / 2 # 0 to 1
                 current_color = (1.0, 0.5 * color_t, 0.0, 1.0)
                 show_alert = True
                 
             else:
                 # Phase 3: Exit to Badge (2.0s - 3.0s)
                 progress = (t - 2.0) / 1.0
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
             self.text_renderer.render_text(renderer, wave_text, current_x, current_y, current_color)
             
             if show_alert:
                 # Render "GET READY" below
                 alert_text = "GET READY"
                 aw, ah = self.text_renderer.measure_text(alert_text)
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

    def render_pause_menu(self, renderer):
        # Fullscreen dark overlay
        renderer.draw_rect(0, 0, self.game.virtual_width, self.game.virtual_height, (0.0, 0.0, 0.0, 0.7))
        
        # Panel Background
        cx, cy = self.game.virtual_width // 2, self.game.virtual_height // 2
        panel_w, panel_h = 300, 400
        panel_x = cx - panel_w // 2
        panel_y = cy - panel_h // 2
        
        renderer.draw_chamfered_rect(panel_x, panel_y, panel_w, panel_h, (0.05, 0.1, 0.25, 0.9), radius=10)
        
        # Panel Border (Glowing Cyan)
        renderer.draw_chamfered_rect(panel_x - 3, panel_y - 3, panel_w + 6, panel_h + 6, (0.0, 0.8, 1.0, 0.8), radius=10)
        renderer.draw_chamfered_rect(panel_x, panel_y, panel_w, panel_h, (0.05, 0.1, 0.25, 0.9), radius=10)
        
        # Title
        title_text = self.game.localization.get("paused")
        tw, th = self.text_renderer.measure_text(title_text)
        self.text_renderer.render_text(renderer, title_text, cx - tw // 2, panel_y + 40, (255, 255, 255))
        
        # Buttons
        for btn in self.game_scene.pause_buttons:
            btn.render(renderer)
