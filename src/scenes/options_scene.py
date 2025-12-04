from src.scenes.scene_manager import Scene
from src.graphics.text_renderer import TextRenderer
from src.utils.localization import Localization
from OpenGL.GL import *
from src.ui.button import Button
from src.ui.checkbox import Checkbox
from src.ui.dropdown import Dropdown
from src.ui.slider import Slider
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
        
        # Restore mouse visibility and release grab
        pygame.mouse.set_visible(True)
        pygame.event.set_grab(False)
        
        self.restart_required = False
        
        # Staged settings
        self.staged_fps = game.fps
        self.staged_res = (game.width, game.height)
        self.staged_lang = game.language
        self.staged_fullscreen = game.fullscreen
        self.staged_show_fps = game.show_fps
        
        # Graphics Settings
        self.staged_msaa = 1 # Default 1 (Off) or 4? Need to read from pygame display?
        # Actually we can't easily read current MSAA. Let's assume default or read from settings if we saved it.
        self.staged_fxaa = getattr(game.post_processor, 'use_fxaa', False)
        self.staged_bloom = getattr(game.post_processor, 'use_bloom', True)
        self.staged_vignette = getattr(game.post_processor, 'use_vignette', True)
        self.staged_chromatic = getattr(game.post_processor, 'use_chromatic', False)
        self.staged_msaa = getattr(game, 'msaa_enabled', True) # Default True
        
        self.current_tab = 0 # 0: General, 1: Graphics, 2: Audio
        self.tabs = ["General", "Graphics", "Audio"]
        
        self.recalculate_layout()
        
    def recalculate_layout(self):
        self.ui_elements = []
        self.labels = [] # Store (key, y) for rendering
        
        # Virtual Resolution Layout (1280x720)
        w, h = 1280, 720
        
        self.panel_w = 800
        self.panel_h = 650 
        self.panel_x = (w - self.panel_w) // 2
        self.panel_y = (h - self.panel_h) // 2
        
        cx = w // 2 
        
        # Tabs
        tab_w = 200
        tab_h = 40
        tab_start_x = cx - (len(self.tabs) * tab_w) // 2
        tab_y = self.panel_y + 80
        
        for i, tab_name in enumerate(self.tabs):
            # Highlight current tab
            # We can use Button for tabs
            btn = Button(tab_start_x + i * tab_w, tab_y, tab_w, tab_h, tab_name.upper(), lambda idx=i: self.set_tab(idx), self.text_renderer)
            if i == self.current_tab:
                btn.base_color = (0.0, 0.5, 1.0, 1.0) # Active color
            else:
                btn.base_color = (0.1, 0.1, 0.1, 0.8) # Inactive
            self.ui_elements.append(btn)
            
        # Layout Constants
        col_left_x = cx - 20 # Right align labels here
        col_right_x = cx + 20 # Left align controls here
        
        start_y = tab_y + 60
        spacing = 55 
        current_y = start_y
        
        # Helper to add a row
        def add_row(label_key, element, height=40):
            nonlocal current_y
            label_y = current_y + (height - 24) // 2
            self.labels.append((label_key, label_y))
            self.ui_elements.append(element)
            current_y += spacing
            
        if self.current_tab == 0: # GENERAL
            # Language
            self.lang_opts = ['en', 'es']
            lang_labels = ["English", "Español"]
            cur_lang_idx = self.lang_opts.index(self.staged_lang) if self.staged_lang in self.lang_opts else 0
            add_row("language", Dropdown(col_right_x, current_y, 250, 40, lang_labels, cur_lang_idx, self.set_lang, self.text_renderer))
            
            # Resolution
            self.res_opts = [
                (1280, 720), (1366, 768), (1600, 900), (1920, 1080), (2560, 1440), (3840, 2160)
            ]
            cur_res = self.staged_res
            if cur_res not in self.res_opts:
                self.res_opts.append(cur_res)
                self.res_opts.sort()
            cur_res_idx = self.res_opts.index(cur_res)
            add_row("resolution", Dropdown(col_right_x, current_y, 250, 40, [f"{w}x{h}" for w,h in self.res_opts], cur_res_idx, self.set_res, self.text_renderer))
            
            # Fullscreen
            add_row("fullscreen", Checkbox(col_right_x, current_y, 30, self.staged_fullscreen, self.set_fullscreen, self.text_renderer, self.localization.get("fullscreen")), height=30)
            
            # Show FPS
            add_row("show_fps", Checkbox(col_right_x, current_y, 30, self.staged_show_fps, self.set_show_fps, self.text_renderer, self.localization.get("show_fps")), height=30)

        elif self.current_tab == 1: # GRAPHICS
            # FPS Limit
            fps_opts = [30, 60, 120, 144, 0]
            fps_labels = [str(f) if f > 0 else self.localization.get("unlimited") for f in fps_opts]
            cur_fps_idx = fps_opts.index(self.staged_fps) if self.staged_fps in fps_opts else 1
            add_row("fps", Dropdown(col_right_x, current_y, 250, 40, fps_labels, cur_fps_idx, self.set_fps, self.text_renderer))
            
            # Bloom
            add_row("Bloom", Checkbox(col_right_x, current_y, 30, self.staged_bloom, self.set_bloom, self.text_renderer, "Enable Bloom"), height=30)
            
            # Vignette
            add_row("Vignette", Checkbox(col_right_x, current_y, 30, self.staged_vignette, self.set_vignette, self.text_renderer, "Enable Vignette"), height=30)
            
            # Chromatic Aberration
            add_row("Chromatic", Checkbox(col_right_x, current_y, 30, self.staged_chromatic, self.set_chromatic, self.text_renderer, "Enable Chromatic"), height=30)
            
            # FXAA
            add_row("FXAA", Checkbox(col_right_x, current_y, 30, self.staged_fxaa, self.set_fxaa, self.text_renderer, "Enable FXAA"), height=30)
            
            # MSAA (Requires Restart)
            add_row("MSAA", Checkbox(col_right_x, current_y, 30, self.staged_msaa, self.set_msaa, self.text_renderer, "MSAA (Restart Required)"), height=30)
            
        elif self.current_tab == 2: # AUDIO
            # Music
            add_row("music_vol", Slider(col_right_x, current_y, 250, 20, 0.0, 1.0, self.game.audio_manager.music_volume, self.set_music_vol, self.text_renderer, ""), height=20)
            
            # SFX
            add_row("sfx_vol", Slider(col_right_x, current_y, 250, 20, 0.0, 1.0, self.game.audio_manager.sfx_volume, self.set_sfx_vol, self.text_renderer, ""), height=20)
        
        # --- BOTTOM BUTTONS ---
        btn_y = self.panel_y + self.panel_h - 80 
        self.ui_elements.append(Button(cx - 160, btn_y, 150, 50, self.localization.get("apply"), lambda: self.on_button_click('apply', -2), self.text_renderer))
        self.ui_elements.append(Button(cx + 10, btn_y, 150, 50, self.localization.get("back"), lambda: self.on_button_click('back', -1), self.text_renderer))
        
        self.restart_text_y = current_y + 20

    def set_tab(self, idx):
        self.current_tab = idx
        self.recalculate_layout()

    def set_fps(self, idx): 
        opts = [30, 60, 120, 144, 0]
        self.staged_fps = opts[idx]
        
    def set_res(self, idx): 
        self.staged_res = self.res_opts[idx]
        
    def set_lang(self, idx): 
        self.staged_lang = self.lang_opts[idx]
        self.game.localization.set_language(self.staged_lang)
        self.recalculate_layout()
        
    def set_fullscreen(self, val): self.staged_fullscreen = val
    def set_show_fps(self, val): self.staged_show_fps = val
    
    def set_bloom(self, val): self.staged_bloom = val
    def set_vignette(self, val): self.staged_vignette = val
    def set_chromatic(self, val): self.staged_chromatic = val
    def set_fxaa(self, val): self.staged_fxaa = val
    def set_msaa(self, val): self.staged_msaa = val
    
    def set_music_vol(self, val): self.game.audio_manager.set_music_volume(val)
    def set_sfx_vol(self, val): self.game.audio_manager.set_sfx_volume(val)
    
    def on_button_click(self, action, idx):
        # Get button dimensions
        # btn = self.ui_elements[idx] # Removed as idx is no longer reliable for particle effects
        # x, y, w, h = btn.x, btn.y, btn.width, btn.height
        
        # Spawn particles (particle logic removed as per user's provided snippet)
        # import random
        # offset = 5 
        # for _ in range(60): 
        #     side = random.randint(0, 3)
        #     vx, vy = 0, 0
        #     if side == 0: # Top
        #         px = random.uniform(x, x + w); py = y - offset; vy = -150
        #     elif side == 1: # Right
        #         px = x + w + offset; py = random.uniform(y, y + h); vx = 150
        #     elif side == 2: # Bottom
        #         px = random.uniform(x, x + w); py = y + h + offset; vy = 150
        #     else: # Left
        #         px = x - offset; py = random.uniform(y, y + h); vx = -150
                
        #     self.particle_system.emit(px, py, count=1, vx=vx, vy=vy)
        
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
        
        # Graphics
        self.game.post_processor.use_bloom = self.staged_bloom
        self.game.post_processor.use_vignette = self.staged_vignette
        self.game.post_processor.use_chromatic = self.staged_chromatic
        self.game.post_processor.use_fxaa = self.staged_fxaa
        
        # MSAA
        if self.staged_msaa != self.game.msaa_enabled:
            self.game.msaa_enabled = self.staged_msaa
            self.restart_required = True
        
        # Save settings to file
        # We need to update save_settings to include graphics options
        # For now, just save what we have.
        self.game.save_settings()
        print("Settings saved.")
        
        # Re-layout to update restart alert if needed
        self.recalculate_layout()

    def get_mouse_pos(self):
        return self.game.input_manager.get_mouse_pos()

    def handle_events(self, events):
        vmx, vmy = self.get_mouse_pos()
        
        if self.pending_action: return
            
        # Iterate in normal order to handle top-most elements first (First added = Top most in render due to reversed render loop)
        blocked = False
        for element in self.ui_elements: # Normal order (Tabs first)
            if blocked:
                # If blocked, update with off-screen mouse and empty events to reset hover state
                element.update(0.016, [], -1000, -1000)
            else:
                if element.update(0.016, events, vmx, vmy):
                    # If element handled the event (e.g. clicked or captured hover), block subsequent elements
                    blocked = True

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
        
        # Draw Panel Background (Glassmorphism)
        # Top (Dark Blue) -> Bottom (Darker)
        renderer.draw_chamfered_rect(self.panel_x, self.panel_y, self.panel_w, self.panel_h, (0.05, 0.1, 0.25, 0.9), radius=10, gradient_bot=(0.02, 0.05, 0.15, 0.95))
        
        # Panel Border (Glowing Cyan)
        renderer.draw_chamfered_rect(self.panel_x - 3, self.panel_y - 3, self.panel_w + 6, self.panel_h + 6, (0.0, 0.8, 1.0, 0.8), radius=10)
        renderer.draw_chamfered_rect(self.panel_x, self.panel_y, self.panel_w, self.panel_h, (0.05, 0.1, 0.25, 0.9), radius=10, gradient_bot=(0.02, 0.05, 0.15, 0.95))
        
        # Title
        cx = 1280 // 2
        self.title_renderer.render_text(renderer, self.localization.get("options"), cx - 100, self.panel_y + 20, (255, 255, 0), outline_color=(255, 100, 0), outline_width=2)
        
        # Labels
        # Right align labels to center line
        label_x_align = cx - 30 
        
        # Render labels from the list we built in recalculate_layout
        for key, y in self.labels:
            if key in ["fullscreen", "show_fps", "Bloom", "Vignette", "Chromatic", "FXAA", "MSAA"]:
                continue # Let checkbox render it
                
            text = self.localization.get(key)
            if not text: text = key # Fallback
            tw, th = self.text_renderer.measure_text(text)
            self.text_renderer.render_text(renderer, text, label_x_align - tw, y, (200, 220, 255))
        
        # Restart Alert
        if self.restart_required:
            self.text_renderer.render_text(renderer, self.localization.get("restart_required"), cx - 150, self.restart_text_y, (255, 100, 100))
        
        # Render Elements (Reverse order for dropdowns to be on top)
        for element in reversed(self.ui_elements):
            element.render(renderer)
            
        renderer.end_frame()
