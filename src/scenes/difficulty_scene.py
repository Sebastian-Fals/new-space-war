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
            'easy': "For beginners. Balanced challenge.",
            'medium': "For veterans. More enemies, faster bullets.",
            'hard': "For experts. Bullet hell awaits.",
            'extreme': "NIGHTMARE. Good luck, you'll need it.",
            'back': "Return to main menu."
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
        btn_easy = Button(cx - btn_w // 2, start_y, btn_w, btn_h, "EASY", lambda: self.on_button_click('easy', 0), self.text_renderer)
        self.ui_elements.append(btn_easy)
        
        # Medium Button
        btn_med = Button(cx - btn_w // 2, start_y + spacing, btn_w, btn_h, "MEDIUM", lambda: self.on_button_click('medium', 1), self.text_renderer)
        self.ui_elements.append(btn_med)
        
        # Hard Button
        btn_hard = Button(cx - btn_w // 2, start_y + spacing * 2, btn_w, btn_h, "HARD", lambda: self.on_button_click('hard', 2), self.text_renderer)
        self.ui_elements.append(btn_hard)
        
        # Extreme Button
        btn_extreme = Button(cx - btn_w // 2, start_y + spacing * 3, btn_w, btn_h, "EXTREME", lambda: self.on_button_click('extreme', 3), self.text_renderer)
        self.ui_elements.append(btn_extreme)
        
        # Back Button
        btn_back = Button(cx - btn_w // 2, self.panel_y + 520, btn_w, btn_h, "BACK", lambda: self.on_button_click('back', 4), self.text_renderer)
        self.ui_elements.append(btn_back)
            
    def get_mouse_pos(self):
        mx, my = pygame.mouse.get_pos()
        vw, vh = self.game.virtual_width, self.game.virtual_height
        ww, wh = self.game.window.width, self.game.window.height
        scale = min(ww / vw, wh / vh)
        tx = (ww - vw * scale) / 2
        ty = (wh - vh * scale) / 2
        return (mx - tx) / scale, (my - ty) / scale
        
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
                    self.description = self.descriptions[keys[i]]

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
        
        # Panel Border
        glLineWidth(2)
        glColor4f(0.3, 0.7, 1.0, 1.0)
        glBegin(GL_LINE_LOOP)
        glVertex2f(self.panel_x, self.panel_y)
        glVertex2f(self.panel_x + self.panel_w, self.panel_y)
        glVertex2f(self.panel_x + self.panel_w, self.panel_y + self.panel_h)
        glVertex2f(self.panel_x, self.panel_y + self.panel_h)
        glEnd()
        
        cx = 1280 // 2
        title = "SELECT DIFFICULTY"
        tw, th = self.title_renderer.measure_text(title)
        self.title_renderer.render_text(title, cx - tw // 2, self.panel_y + 30, (255, 255, 0))
        
        # Render Description
        if self.description:
            dw, dh = self.text_renderer.measure_text(self.description)
            self.text_renderer.render_text(self.description, cx - dw // 2, self.panel_y + 450, (200, 255, 255))
        
        for element in self.ui_elements:
            element.render()
            
        self.particle_system.render()
            
        glPopMatrix()
