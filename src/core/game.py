import pygame
import json
import os
import traceback
from src.core.window import Window
from src.utils.localization import Localization
from src.graphics.text_renderer import TextRenderer

class Game:
    def __init__(self):
        from src.core.settings_manager import SettingsManager
        self.settings_manager = SettingsManager()
        
        # Apply settings
        self.width = self.settings_manager.get("width")
        self.height = self.settings_manager.get("height")
        self.fps = self.settings_manager.get("fps")
        self.language = self.settings_manager.get("language")
        self.fullscreen = self.settings_manager.get("fullscreen")
        self.show_fps = self.settings_manager.get("show_fps")
        self.music_volume = self.settings_manager.get("music_volume")
        self.sfx_volume = self.settings_manager.get("sfx_volume")
        self.high_score = self.settings_manager.get("high_score")
        self.msaa_enabled = self.settings_manager.get("msaa_enabled")
        
        # Graphics
        self.use_bloom = self.settings_manager.get("use_bloom")
        self.use_vignette = self.settings_manager.get("use_vignette")
        self.use_chromatic = self.settings_manager.get("use_chromatic")
        self.use_fxaa = self.settings_manager.get("use_fxaa")

        self.window = Window(self.width, self.height, "Danmaku Space War v2", fullscreen=self.fullscreen, msaa=self.msaa_enabled)
        # Sync dimensions with actual window size
        self.width = self.window.width
        self.height = self.window.height
        
        # Init Audio Manager early to set volume
        from src.core.audio_manager import AudioManager
        self.audio_manager = AudioManager()
        self.audio_manager.set_music_volume(self.music_volume)
        self.audio_manager.set_sfx_volume(self.sfx_volume)
            
        self.virtual_width = 1280
        self.virtual_height = 720
        
        self.running = True
        self.score = 0
        self.clock = pygame.time.Clock()
        self.global_time = 0
        
        self.localization = Localization()
        self.localization.set_language(self.language)
        
        self.fps_renderer = TextRenderer(font_name="pixel", size=20, antialias=False)
        
        from src.scenes.scene_manager import SceneManager
        from src.scenes.menu_scene import MenuScene
        from src.graphics.starfield import Starfield
        from src.graphics.warp_background import WarpBackground
        from src.graphics.post_processor import PostProcessor
        
        self.starfield = Starfield(self.virtual_width, self.virtual_height)
        self.warp_bg = WarpBackground(self.window.width, self.window.height)
        
        # Initialize PostProcessor
        self.post_processor = PostProcessor(self.window.width, self.window.height)
        # Apply saved graphics settings
        self.post_processor.use_bloom = self.use_bloom
        self.post_processor.use_vignette = self.use_vignette
        self.post_processor.use_chromatic = self.use_chromatic
        self.post_processor.use_fxaa = self.use_fxaa
        
        from src.core.input_manager import InputManager
        self.input_manager = InputManager(self)
        
        from src.graphics.renderer_2d import Renderer2D
        self.renderer = Renderer2D()
        
        self.scene_manager = SceneManager(self)
        self.scene_manager.set_scene(MenuScene(self))
        
    def save_settings(self):
        # Update settings manager with current values
        self.settings_manager.set("fps", self.fps)
        self.settings_manager.set("width", self.width)
        self.settings_manager.set("height", self.height)
        self.settings_manager.set("language", self.language)
        self.settings_manager.set("fullscreen", self.fullscreen)
        self.settings_manager.set("show_fps", self.show_fps)
        self.settings_manager.set("music_volume", self.audio_manager.music_volume)
        self.settings_manager.set("sfx_volume", self.audio_manager.sfx_volume)
        self.settings_manager.set("high_score", self.high_score)
        self.settings_manager.set("use_bloom", self.post_processor.use_bloom)
        self.settings_manager.set("use_vignette", self.post_processor.use_vignette)
        self.settings_manager.set("use_chromatic", self.post_processor.use_chromatic)
        self.settings_manager.set("use_fxaa", self.post_processor.use_fxaa)
        self.settings_manager.set("msaa_enabled", self.msaa_enabled)
        
        self.settings_manager.save()

    def run(self):
        while self.running:
            dt = self.clock.tick(self.fps) / 1000.0
            self.global_time += dt
            
            self.input_manager.update()
            
            # Handle Events
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.VIDEORESIZE:
                    self.width = event.w
                    self.height = event.h
                    self.window.resize(event.w, event.h)
                    self.post_processor.resize(event.w, event.h)
                    self.warp_bg.resize(event.w, event.h)
                
                self.scene_manager.handle_events(events)
                
            self.scene_manager.update(dt)
            
            try:
                self.scene_manager.render()
                
                if self.show_fps:
                    self.renderer.begin_frame(self.window.width, self.window.height, self.window.width, self.window.height)
                    fps_text = f"FPS: {int(self.clock.get_fps())}"
                    self.fps_renderer.render_text(self.renderer, fps_text, self.window.width - 120, 10, (0, 255, 0))
                    self.renderer.end_frame()
                    
                self.window.flip()
                
            except Exception as e:
                with open("crash.log", "w") as f:
                    f.write(traceback.format_exc())
                print("Game Crashed! See crash.log")
                raise e
                
        pygame.quit()
