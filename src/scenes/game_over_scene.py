from src.scenes.scene_manager import Scene
from src.ui.button import Button
from src.graphics.text_renderer import TextRenderer
from src.graphics.particle_system import ParticleSystem
from OpenGL.GL import *
import pygame
import random

class GameOverScene(Scene):
    def __init__(self, game, score, wave, boss_beaten):
        super().__init__(game)
        self.score = score
        self.wave = wave
        self.boss_beaten = boss_beaten
        
        self.text_renderer = TextRenderer(font_name="pixel", size=24, antialias=False)
        self.title_renderer = TextRenderer(font_name="pixel", size=64, antialias=False)
        self.stats_renderer = TextRenderer(font_name="pixel", size=32, antialias=False)
        
        self.particle_system = ParticleSystem()
        self.ui_elements = []
        
        # Restore mouse visibility and release grab
        pygame.mouse.set_visible(True)
        pygame.event.set_grab(False)
        
        self.recalculate_layout()
        
    def recalculate_layout(self):
        self.ui_elements = []
        w, h = 1280, 720
        cx = w // 2
        cy = h // 2
        
        # Buttons
        btn_w = 300
        btn_h = 60
        spacing = 80
        start_y = cy + 150
        
        # Retry Button
        btn_retry = Button(cx - btn_w // 2, start_y, btn_w, btn_h, self.game.localization.get("retry").upper(), self.retry_game, self.text_renderer)
        self.ui_elements.append(btn_retry)
        
        # Menu Button
        btn_menu = Button(cx - btn_w // 2, start_y + spacing, btn_w, btn_h, self.game.localization.get("main_menu").upper(), self.goto_menu, self.text_renderer)
        self.ui_elements.append(btn_menu)
        
    def retry_game(self):
        from src.scenes.game_scene import GameScene
        self.game.scene_manager.set_scene(GameScene(self.game))
        
    def goto_menu(self):
        from src.scenes.menu_scene import MenuScene
        self.game.scene_manager.set_scene(MenuScene(self.game))
        
    def get_mouse_pos(self):
        return self.game.input_manager.get_mouse_pos()

    def handle_events(self, events):
        vmx, vmy = self.get_mouse_pos()
        for element in self.ui_elements:
            element.update(0.016, events, vmx, vmy)
            
    def update(self, dt):
        self.particle_system.update(dt)
        
    def render(self):
        # --- POST PROCESSING START ---
        self.game.post_processor.begin_capture()
        
        # Use the warp background but maybe red tinted?
        # For now just standard render
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, self.game.window.width, self.game.window.height, 0, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
        # Calculate Scissor Rect
        vw, vh = self.game.virtual_width, self.game.virtual_height
        ww, wh = self.game.window.width, self.game.window.height
        scale = min(ww / vw, wh / vh)
        tx = (ww - vw * scale) / 2
        ty = (wh - vh * scale) / 2
        
        glEnable(GL_SCISSOR_TEST)
        glScissor(int(tx), int(ty), int(vw * scale), int(vh * scale))
        
        self.game.warp_bg.render(self.game.global_time)
        
        glDisable(GL_SCISSOR_TEST)
        
        self.game.post_processor.end_capture()
        # --- POST PROCESSING END ---
        
        # Render Post-Processed Scene to Screen (Background Only)
        self.game.post_processor.render()
        
        # --- UI RENDERING (On Top) ---
        renderer = self.game.renderer
        renderer.begin_frame(self.game.virtual_width, self.game.virtual_height, self.game.window.width, self.game.window.height)
        
        vw, vh = self.game.virtual_width, self.game.virtual_height
        
        # Dark Overlay (Rendered on top of bloom to dim it)
        renderer.draw_rect(0, 0, vw, vh, (0.0, 0.0, 0.0, 0.7))
        
        cx = vw // 2
        cy = vh // 2
        
        # Title "GAME OVER"
        title = self.game.localization.get("game_over")
        tw, th = self.title_renderer.measure_text(title)
        self.title_renderer.render_text(renderer, title, cx - tw // 2, cy - 200, (255, 50, 50), outline_color=(100, 0, 0), outline_width=4)
        
        # Stats Panel
        panel_y = cy - 100
        spacing = 50
        
        # Score
        score_lbl = self.game.localization.get("score")
        score_text = f"{score_lbl}: {int(self.score)}"
        sw, sh = self.stats_renderer.measure_text(score_text)
        self.stats_renderer.render_text(renderer, score_text, cx - sw // 2, panel_y, (255, 255, 255))
        
        # High Score
        high_score_text = f"HIGH SCORE: {int(self.game.high_score)}"
        hsw, hsh = self.stats_renderer.measure_text(high_score_text)
        self.stats_renderer.render_text(renderer, high_score_text, cx - hsw // 2, panel_y - 40, (255, 215, 0)) # Gold color
        
        # Wave
        wave_lbl = self.game.localization.get("wave_reached")
        wave_text = f"{wave_lbl}: {self.wave}"
        ww_text, wh_text = self.stats_renderer.measure_text(wave_text)
        self.stats_renderer.render_text(renderer, wave_text, cx - ww_text // 2, panel_y + spacing, (200, 200, 255))
        
        # Boss Status
        boss_key = "boss_defeated" if self.boss_beaten else "boss_survived"
        boss_text = self.game.localization.get(boss_key)
        color = (100, 255, 100) if self.boss_beaten else (255, 100, 100)
        bw, bh = self.stats_renderer.measure_text(boss_text)
        self.stats_renderer.render_text(renderer, boss_text, cx - bw // 2, panel_y + spacing * 2, color)
        
        # Buttons
        for element in self.ui_elements:
            element.render(renderer)
            
        renderer.end_frame()
