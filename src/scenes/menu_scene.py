import pygame
from src.scenes.scene_manager import Scene
from src.graphics.text_renderer import TextRenderer
from OpenGL.GL import *

from src.ui.button import Button
from src.graphics.warp_background import WarpBackground

from src.graphics.particle_system import ParticleSystem

class MenuScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.game.audio_manager.play_music("menu")
        self.options = ['play', 'options', 'exit']
        # Use 'pixel' font hint (mapped to consolas in TextRenderer)
        self.text_renderer = TextRenderer(font_name="pixel", size=48, antialias=False) 
        self.title_renderer = TextRenderer(font_name="pixel", size=96, antialias=False)
        
        self.particle_system = ParticleSystem()
        
        self.pending_action = None
        self.action_timer = 0.0
        
        self.ui_elements = []
        self.ui_elements = []
        
        # Restore mouse visibility and release grab
        pygame.mouse.set_visible(True)
        pygame.event.set_grab(False)
        
        self.recalculate_layout()
        
    def recalculate_layout(self):
        self.ui_elements = []
        # Define layout in Virtual Resolution (1280x720)
        cx = 1280 // 2
        
        btn_w = 480
        btn_h = 70
        start_y = 720 * 0.5 
        spacing = 90
        
        for i, opt in enumerate(self.options):
            y = start_y + i * spacing
            x = cx - btn_w // 2
            # Pass a wrapper to trigger particles AND action
            action = lambda o=opt, idx=i: self.on_button_click(o, idx)
            # Use localization for display text
            text = self.game.localization.get(opt).upper()
            btn = Button(x, y, btn_w, btn_h, text, action, self.text_renderer)
            self.ui_elements.append(btn)

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

    def handle_events(self, events):
        vmx, vmy = self.get_mouse_pos()
        
        # Block input if delayed action pending
        if self.pending_action: # Changed from self.delayed_action to self.pending_action
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
                
    def execute_action(self, option):
        if option == 'play':
            from src.scenes.difficulty_scene import DifficultyScene
            self.game.scene_manager.set_scene(DifficultyScene(self.game))
        elif option == 'options':
            from src.scenes.options_scene import OptionsScene
            self.game.scene_manager.set_scene(OptionsScene(self.game))
        elif option == 'exit':
            self.game.running = False

    def render(self):
        # --- POST PROCESSING START ---
        self.game.post_processor.begin_capture()
        
        # Render Background (Warp Nebula)
        # Setup Legacy Projection
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
        
        # --- UI RENDERING (On Top, Unaffected by Bloom) ---
        self.game.renderer.begin_frame(self.game.virtual_width, self.game.virtual_height, self.game.window.width, self.game.window.height)
        
        # Render Title (Centered in Virtual Space)
        cx = 1280 // 2
        title_text = "DANMAKU"
        tw, th = self.title_renderer.measure_text(title_text)
        # Add a glow effect to title
        self.title_renderer.render_text(self.game.renderer, title_text, cx - tw // 2, 100, (255, 255, 0), outline_color=(255, 100, 0), outline_width=4)
        
        # Render Buttons
        for element in self.ui_elements:
            element.render(self.game.renderer)
            
        self.game.renderer.end_frame()
