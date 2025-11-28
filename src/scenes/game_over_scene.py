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
        btn_retry = Button(cx - btn_w // 2, start_y, btn_w, btn_h, "RETRY", self.retry_game, self.text_renderer)
        self.ui_elements.append(btn_retry)
        
        # Menu Button
        btn_menu = Button(cx - btn_w // 2, start_y + spacing, btn_w, btn_h, "MAIN MENU", self.goto_menu, self.text_renderer)
        self.ui_elements.append(btn_menu)
        
    def retry_game(self):
        from src.scenes.game_scene import GameScene
        self.game.scene_manager.set_scene(GameScene(self.game))
        
    def goto_menu(self):
        from src.scenes.menu_scene import MenuScene
        self.game.scene_manager.set_scene(MenuScene(self.game))
        
    def get_mouse_pos(self):
        mx, my = pygame.mouse.get_pos()
        vw, vh = self.game.virtual_width, self.game.virtual_height
        ww, wh = self.game.window.width, self.game.window.height
        scale = min(ww / vw, wh / vh)
        tx = (ww - vw * scale) / 2
        ty = (wh - vh * scale) / 2
        return (mx - tx) / scale, (my - ty) / scale

    def handle_events(self, events):
        vmx, vmy = self.get_mouse_pos()
        for element in self.ui_elements:
            element.update(0.016, events, vmx, vmy)
            
    def update(self, dt):
        self.particle_system.update(dt)
        
    def render(self):
        # Use the warp background but maybe red tinted?
        # For now just standard render
        self.game.warp_bg.render(self.game.global_time)
        
        vw, vh = self.game.virtual_width, self.game.virtual_height
        ww, wh = self.game.window.width, self.game.window.height
        scale = min(ww / vw, wh / vh)
        tx = (ww - vw * scale) / 2
        ty = (wh - vh * scale) / 2
        
        glPushMatrix()
        glTranslatef(tx, ty, 0)
        glScalef(scale, scale, 1.0)
        
        glDisable(GL_TEXTURE_2D)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        # Dark Overlay
        glColor4f(0.0, 0.0, 0.0, 0.7)
        glBegin(GL_QUADS)
        glVertex2f(0, 0)
        glVertex2f(vw, 0)
        glVertex2f(vw, vh)
        glVertex2f(0, vh)
        glEnd()
        
        cx = vw // 2
        cy = vh // 2
        
        # Title "GAME OVER"
        title = "GAME OVER"
        tw, th = self.title_renderer.measure_text(title)
        self.title_renderer.render_text(title, cx - tw // 2, cy - 200, (255, 50, 50))
        
        # Stats Panel
        panel_y = cy - 100
        spacing = 50
        
        # Score
        score_text = f"SCORE: {self.score}"
        sw, sh = self.stats_renderer.measure_text(score_text)
        self.stats_renderer.render_text(score_text, cx - sw // 2, panel_y, (255, 255, 255))
        
        # Wave
        wave_text = f"WAVE REACHED: {self.wave}"
        ww_text, wh_text = self.stats_renderer.measure_text(wave_text)
        self.stats_renderer.render_text(wave_text, cx - ww_text // 2, panel_y + spacing, (200, 200, 255))
        
        # Boss Status
        boss_text = "BOSS DEFEATED!" if self.boss_beaten else "BOSS SURVIVED"
        color = (100, 255, 100) if self.boss_beaten else (255, 100, 100)
        bw, bh = self.stats_renderer.measure_text(boss_text)
        self.stats_renderer.render_text(boss_text, cx - bw // 2, panel_y + spacing * 2, color)
        
        # Buttons
        for element in self.ui_elements:
            element.render()
            
        self.particle_system.render()
        
        glPopMatrix()
