import pygame
import json
import os
from src.core.window import Window
from src.utils.localization import Localization
from src.graphics.text_renderer import TextRenderer

class Game:
    def __init__(self):
        self.load_settings()
        self.window = Window(self.width, self.height, "Danmaku Space War", fullscreen=self.fullscreen)
            
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
        
        self.starfield = Starfield(self.virtual_width, self.virtual_height)
        self.warp_bg = WarpBackground(self.window.width, self.window.height)
        self.scene_manager = SceneManager(self)
        self.scene_manager.set_scene(MenuScene(self))
        
    def load_settings(self):
        default_settings = {
            "fps": 60,
            "width": 1280,
            "height": 720,
            "language": "en",
            "fullscreen": False,
            "show_fps": False
        }
        try:
            if os.path.exists("settings.json"):
                with open("settings.json", "r") as f:
                    saved = json.load(f)
                    default_settings.update(saved)
        except Exception as e:
            print(f"Failed to load settings: {e}")
            
        self.fps = default_settings["fps"]
        self.width = default_settings["width"]
        self.height = default_settings["height"]
        self.language = default_settings["language"]
        self.fullscreen = default_settings["fullscreen"]
        self.show_fps = default_settings["show_fps"]

    def save_settings(self):
        settings = {
            "fps": self.fps,
            "width": self.width,
            "height": self.height,
            "language": self.language,
            "fullscreen": self.fullscreen,
            "show_fps": self.show_fps
        }
        try:
            with open("settings.json", "w") as f:
                json.dump(settings, f)
        except Exception as e:
            print(f"Failed to save settings: {e}")

    def run(self):
        while self.running:
            dt = self.clock.tick(self.fps) / 1000.0
            self.global_time += dt
            
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False
            
            self.scene_manager.handle_events(events)
            self.scene_manager.update(dt)
            
            self.window.clear()
            self.scene_manager.render()
            
            if self.show_fps:
                fps_text = f"FPS: {int(self.clock.get_fps())}"
                # Render top-right
                self.fps_renderer.render_text(fps_text, self.window.width - 120, 10, (0, 255, 0))
                
            self.window.flip()
            
    def handle_events(self):
        pass

    def update(self, dt):
        pass

    def render(self):
        pass
