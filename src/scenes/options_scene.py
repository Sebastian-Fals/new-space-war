from src.scenes.scene_manager import Scene
from src.scenes.scene_manager import Scene
from src.graphics.text_renderer import TextRenderer
from src.utils.localization import Localization
from OpenGL.GL import *
from src.ui.button import Button
from src.ui.checkbox import Checkbox
from src.ui.dropdown import Dropdown
from src.graphics.particle_system import ParticleSystem
import pygame

class OptionsScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.text_renderer = TextRenderer(font_name="pixel", size=24, antialias=False)
        self.title_renderer = TextRenderer(font_name="pixel", size=48, antialias=False)
        
        # Use game's localization instance
        self.localization = game.localization
        
        self.particle_system = ParticleSystem()
        self.pending_action = None
        self.action_timer = 0.0
        
        self.ui_elements = []
        self.recalculate_layout()
        
        self.restart_required = False
        
        # Staged settings
        self.staged_fps = game.fps
        self.staged_res = (game.window.width, game.window.height)
        self.staged_lang = game.language
        self.staged_fullscreen = game.window.fullscreen
        self.staged_show_fps = game.show_fps
        
    def recalculate_layout(self):
        self.ui_elements = []
        
        # Virtual Resolution Layout (1280x720)
        w, h = 1280, 720
        
        self.panel_w = 680
        self.panel_h = 500
        self.panel_x = (w - self.panel_w) // 2
        self.panel_y = (h - self.panel_h) // 2
        
        cx = w // 2 
        start_y = self.panel_y + 70
        
        # FPS Dropdown
        fps_opts = [30, 60, 120]
        cur_fps_idx = fps_opts.index(self.game.fps) if self.game.fps in fps_opts else 1
        self.ui_elements.append(Dropdown(cx + 50, start_y, 200, 40, fps_opts, cur_fps_idx, self.set_fps, self.text_renderer))
        
        # Resolution Dropdown
        self.res_opts = [(800, 600), (1280, 720), (1920, 1080)]
        cur_res = (self.game.width, self.game.height) # Use pending settings
        if cur_res not in self.res_opts:
            self.res_opts.append(cur_res)
        cur_res_idx = self.res_opts.index(cur_res)
        self.ui_elements.append(Dropdown(cx + 50, start_y + 60, 200, 40, [f"{w}x{h}" for w,h in self.res_opts], cur_res_idx, self.set_res, self.text_renderer))
        
        # Language Dropdown
        self.lang_opts = ['en', 'es']
        cur_lang_idx = self.lang_opts.index(self.game.language) if self.game.language in self.lang_opts else 0
        self.ui_elements.append(Dropdown(cx + 50, start_y + 120, 200, 40, self.lang_opts, cur_lang_idx, self.set_lang, self.text_renderer))
        
        # Fullscreen Checkbox
        self.ui_elements.append(Checkbox(cx + 50, start_y + 180, 30, self.game.window.fullscreen, self.set_fullscreen, self.text_renderer, "Fullscreen"))
        
        # Show FPS Checkbox
        self.ui_elements.append(Checkbox(cx + 50, start_y + 220, 30, self.game.show_fps, self.set_show_fps, self.text_renderer, "Show FPS"))
        
        # Apply Button
        # Pass the button object itself to the callback? No, callback takes no args usually.
        # But for on_button_click we need to know WHICH button.
        # We can pass the index in ui_elements.
        # Index 5 is Apply, Index 6 is Back.
        self.ui_elements.append(Button(cx - 160, self.panel_y + 400, 150, 50, "APPLY", lambda: self.on_button_click('apply', 5), self.text_renderer))
        
        # Back Button
        self.ui_elements.append(Button(cx + 10, self.panel_y + 400, 150, 50, "BACK", lambda: self.on_button_click('back', 6), self.text_renderer))

    def set_fps(self, idx): self.staged_fps = [30, 60, 120][idx]
    def set_res(self, idx): self.staged_res = self.res_opts[idx]
    def set_lang(self, idx): self.staged_lang = self.lang_opts[idx]
    def set_fullscreen(self, val): self.staged_fullscreen = val
    def set_show_fps(self, val): self.staged_show_fps = val
    
    def on_button_click(self, action, idx):
        # Get button dimensions
        btn = self.ui_elements[idx]
        x, y, w, h = btn.x, btn.y, btn.width, btn.height
        
        # Spawn particles along the margins (outside)
        import random
        offset = 5 # Distance from button edge
        for _ in range(60): 
            side = random.randint(0, 3)
            vx, vy = 0, 0
            if side == 0: # Top -> Move Up
                px = random.uniform(x, x + w)
                py = y - offset
                vy = -150
            elif side == 1: # Right -> Move Right
                px = x + w + offset
                py = random.uniform(y, y + h)
                vx = 150
            elif side == 2: # Bottom -> Move Down
                px = random.uniform(x, x + w)
                py = y + h + offset
                vy = 150
            else: # Left -> Move Left
                px = x - offset
                py = random.uniform(y, y + h)
                vx = -150
                
            self.particle_system.emit(px, py, count=1, vx=vx, vy=vy)
        
        # Delay action by 0.5 seconds to let animation play
        if not self.pending_action:
            self.pending_action = action
            self.action_timer = 0.5
            
    def execute_action(self, action):
        if action == 'back':
            from src.scenes.menu_scene import MenuScene
            self.game.scene_manager.set_scene(MenuScene(self.game))
        elif action == 'apply':
            self.apply_settings()
        
    def apply_settings(self):
        self.game.fps = self.staged_fps
        
        # Resolution & Fullscreen
        w, h = self.staged_res
        if w != self.game.window.width or h != self.game.window.height or self.staged_fullscreen != self.game.window.fullscreen:
            self.restart_required = True
            self.game.width = w
            self.game.height = h
            self.game.fullscreen = self.staged_fullscreen
            
        # Language
        self.game.language = self.staged_lang
        self.game.localization.set_language(self.staged_lang)
        
        # Show FPS
        self.game.show_fps = self.staged_show_fps
        
        # Save settings to file
        self.game.save_settings()
        print("Settings saved. Restart required for some changes." if self.restart_required else "Settings applied and saved!")

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
        
        # Block input if delayed action pending
        if self.pending_action:
            return
            
        for element in self.ui_elements:
            element.update(0.016, events, vmx, vmy)

    def update(self, dt):
        self.particle_system.update(dt)
        
        if self.pending_action:
            self.action_timer -= dt
            if self.action_timer <= 0:
                self.execute_action(self.pending_action)
                self.pending_action = None

    def render(self):
        vw, vh = self.game.virtual_width, self.game.virtual_height
        ww, wh = self.game.window.width, self.game.window.height
        scale = min(ww / vw, wh / vh)
        tx = (ww - vw * scale) / 2
        ty = (wh - vh * scale) / 2
        
        # Render Background (Warp Nebula)
        self.game.warp_bg.render(self.game.global_time)
        
        glPushMatrix()
        glTranslatef(tx, ty, 0)
        glScalef(scale, scale, 1.0)
        
        glDisable(GL_TEXTURE_2D)
        
        # Draw Panel Background
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        # Panel Body
        glColor4f(0.05, 0.1, 0.2, 0.85)
        glBegin(GL_QUADS)
        glVertex2f(self.panel_x, self.panel_y)
        glVertex2f(self.panel_x + self.panel_w, self.panel_y)
        glVertex2f(self.panel_x + self.panel_w, self.panel_y + self.panel_h)
        glVertex2f(self.panel_x, self.panel_y + self.panel_h)
        glEnd()
        
        # Panel Border (Cyan/Blue)
        glLineWidth(2)
        glColor4f(0.3, 0.7, 1.0, 1.0)
        glBegin(GL_LINE_LOOP)
        glVertex2f(self.panel_x, self.panel_y)
        glVertex2f(self.panel_x + self.panel_w, self.panel_y)
        glVertex2f(self.panel_x + self.panel_w, self.panel_y + self.panel_h)
        glVertex2f(self.panel_x, self.panel_y + self.panel_h)
        glEnd()
        
        # Title
        cx = 1280 // 2
        self.title_renderer.render_text("OPTIONS", cx - 100, self.panel_y + 10, (255, 255, 0))
        
        # Labels
        start_y = self.panel_y + 70
        self.text_renderer.render_text("FPS", cx - 150, start_y + 10, (255, 255, 255))
        self.text_renderer.render_text("Resolution", cx - 200, start_y + 70, (255, 255, 255))
        self.text_renderer.render_text("Language", cx - 170, start_y + 130, (255, 255, 255))
        
        # Restart Alert
        if self.restart_required:
            self.text_renderer.render_text("! Restart Required !", cx - 120, self.panel_y + 350, (255, 50, 50))
        
        # Render Elements (Reverse order for dropdowns to be on top)
        for element in reversed(self.ui_elements):
            element.render()
            
        self.particle_system.render()
            
        glPopMatrix()
