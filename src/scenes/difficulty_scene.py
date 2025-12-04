from src.scenes.scene_manager import Scene
from src.ui.button import Button
from src.graphics.warp_background import WarpBackground
from src.graphics.text_renderer import TextRenderer
from src.graphics.particle_system import ParticleSystem
from OpenGL.GL import *
import pygame

class DifficultyScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.options = ['easy', 'medium', 'hard', 'extreme', 'back']
        self.text_renderer = TextRenderer(font_name="pixel", size=24, antialias=False)
        self.title_renderer = TextRenderer(font_name="pixel", size=48, antialias=False)
        
        self.particle_system = ParticleSystem()
        self.pending_action = None
        self.action_timer = 0.0
        
        self.description = ""
        self.descriptions = {
            'easy': "desc_easy",
            'medium': "desc_medium",
            'hard': "desc_hard",
            'extreme': "desc_extreme",
            'back': "desc_back"
        }
        
        self.ui_elements = []
        self.recalculate_layout()
        
    def recalculate_layout(self):
        self.ui_elements = []
        # Virtual Resolution
        w, h = 1280, 720
        
        self.panel_w = 700 # Wider panel
        self.panel_h = 600 # Taller panel
        self.panel_x = (w - self.panel_w) // 2
        self.panel_y = (h - self.panel_h) // 2
        
        cx = w // 2
        
        btn_w = 400
        btn_h = 50 # Slightly smaller to fit
        start_y = self.panel_y + 100 
        spacing = 70
        
        # Easy Button
        btn_easy = Button(cx - btn_w // 2, start_y, btn_w, btn_h, self.game.localization.get("easy").upper(), lambda: self.on_button_click('easy', 0), self.text_renderer)
        self.ui_elements.append(btn_easy)
        
        # Medium Button
        btn_med = Button(cx - btn_w // 2, start_y + spacing, btn_w, btn_h, self.game.localization.get("medium").upper(), lambda: self.on_button_click('medium', 1), self.text_renderer)
        self.ui_elements.append(btn_med)
        
        # Hard Button
        btn_hard = Button(cx - btn_w // 2, start_y + spacing * 2, btn_w, btn_h, self.game.localization.get("hard").upper(), lambda: self.on_button_click('hard', 2), self.text_renderer)
        self.ui_elements.append(btn_hard)
        
        # Extreme Button
        btn_extreme = Button(cx - btn_w // 2, start_y + spacing * 3, btn_w, btn_h, self.game.localization.get("extreme").upper(), lambda: self.on_button_click('extreme', 3), self.text_renderer)
        self.ui_elements.append(btn_extreme)
        
        # Back Button
        btn_back = Button(cx - btn_w // 2, self.panel_y + 520, btn_w, btn_h, self.game.localization.get("back").upper(), lambda: self.on_button_click('back', 4), self.text_renderer)
        self.ui_elements.append(btn_back)
            
    def get_mouse_pos(self):
        return self.game.input_manager.get_mouse_pos()
        
    def on_button_click(self, option, idx):
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
            self.pending_action = option
            self.action_timer = 0.5
            
    def execute_action(self, difficulty):
        if difficulty == 'back':
            from src.scenes.menu_scene import MenuScene
            self.game.scene_manager.set_scene(MenuScene(self.game))
        else:
            self.game.difficulty = difficulty
            from src.scenes.game_scene import GameScene
            self.game.scene_manager.set_scene(GameScene(self.game))

    def handle_events(self, events):
        vmx, vmy = self.get_mouse_pos()
        
        # Block input if delayed action pending
        if self.pending_action:
            return
        
        # Update description based on hover
        self.description = ""
        for i, element in enumerate(self.ui_elements):
            element.update(0.016, events, vmx, vmy)
            if element.hovered:
                # Map index to option key
                keys = ['easy', 'medium', 'hard', 'extreme', 'back']
                if i < len(keys):
                    self.description = self.game.localization.get(self.descriptions[keys[i]])

    def update(self, dt):
        self.particle_system.update(dt)
        
        if self.pending_action:
            self.action_timer -= dt
            if self.action_timer <= 0:
                self.execute_action(self.pending_action)
                self.pending_action = None

    def render(self):
        # --- POST PROCESSING START ---
        self.game.post_processor.begin_capture()
        
        # Render Background (Warp Nebula)
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
        
        # Draw Panel Background
        # Panel Body (Gradient)
        renderer.draw_chamfered_rect(self.panel_x, self.panel_y, self.panel_w, self.panel_h, (0.05, 0.1, 0.25, 0.9), radius=10, gradient_bot=(0.02, 0.05, 0.15, 0.95))
        
        # Panel Border (Glowing Cyan)
        renderer.draw_chamfered_rect(self.panel_x - 3, self.panel_y - 3, self.panel_w + 6, self.panel_h + 6, (0.0, 0.8, 1.0, 0.8), radius=10)
        renderer.draw_chamfered_rect(self.panel_x, self.panel_y, self.panel_w, self.panel_h, (0.05, 0.1, 0.25, 0.9), radius=10, gradient_bot=(0.02, 0.05, 0.15, 0.95))
        
        cx = 1280 // 2
        title = self.game.localization.get("difficulty").upper()
        tw, th = self.title_renderer.measure_text(title)
        self.title_renderer.render_text(renderer, title, cx - tw // 2, self.panel_y + 30, (255, 255, 0), outline_color=(255, 100, 0), outline_width=4)
        
        # Render Description
        if self.description:
            dw, dh = self.text_renderer.measure_text(self.description)
            self.text_renderer.render_text(renderer, self.description, cx - dw // 2, self.panel_y + 450, (200, 255, 255))
        
        for element in self.ui_elements:
            element.render(renderer)
            
        renderer.end_frame()
            
        # self.particle_system.render()
