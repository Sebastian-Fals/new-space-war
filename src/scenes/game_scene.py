import pygame
from src.scenes.scene_manager import Scene
from src.graphics.starfield import Starfield
from src.entities.player import Player
from src.entities.bullet_manager import BulletManager
from src.core.wave_manager import WaveManager
from src.graphics.particle_system import ParticleSystem
from src.ui.button import Button
from src.utils.spatial_grid import SpatialGrid
from OpenGL.GL import *
import random

class GameScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.game.score = 0 # Reset score
        self.game.audio_manager.play_music("game", force_restart=True)
        self.starfield = Starfield(game.virtual_width, game.virtual_height)
        self.paused = False
        self.time = 0
        
        self.particle_system = ParticleSystem()
        self.grid = SpatialGrid(game.virtual_width, game.virtual_height, 100)
        
        # UI Juice
        self.display_score = 0
        self.score_scale = 1.0
        self.shake_timer = 0
        self.shake_magnitude = 0
        
        # Initialize other components
        self.bullet_manager = BulletManager(self.particle_system)
        self.player = Player(game.virtual_width // 2, game.virtual_height // 2, self.bullet_manager)
        self.displayed_hp = self.player.hp # Initialize for lerp
        self.wave_manager = WaveManager(self)
        self.wave_manager.game = self
        
        from src.core.collision_manager import CollisionManager
        self.collision_manager = CollisionManager(self)
        
        self.boss_beaten = False
        
        from src.graphics.text_renderer import TextRenderer
        self.text_renderer = TextRenderer()
        
        from src.graphics.renderers.player_renderer import PlayerRenderer
        self.player_renderer = PlayerRenderer()
        
        from src.graphics.renderers.bullet_renderer import BulletRenderer
        self.bullet_renderer = BulletRenderer()
        
        from src.ui.game_hud import GameHUD
        self.hud = GameHUD(self)
        
        # Pause Menu UI
        self.pause_buttons = []
        self.init_pause_menu()
        
        # Hide mouse and grab input
        pygame.mouse.set_visible(False)
        pygame.event.set_grab(True)
        
    def init_pause_menu(self):
        # Create buttons with wrapped callbacks for effects
        def wrap(cb):
            return lambda: self.on_button_click(None, cb) 
            
        self.btn_resume = Button(0, 0, 200, 50, self.game.localization.get("resume").upper(), None, self.text_renderer)
        self.btn_restart = Button(0, 0, 200, 50, self.game.localization.get("restart").upper(), None, self.text_renderer)
        self.btn_quit = Button(0, 0, 200, 50, self.game.localization.get("main_menu").upper(), None, self.text_renderer)
        
        self.pause_buttons = [self.btn_resume, self.btn_restart, self.btn_quit]
        
        # Now assign callbacks with button reference
        self.btn_resume.callback = lambda: self.on_button_click(self.btn_resume, lambda: self.toggle_pause())
        self.btn_restart.callback = lambda: self.on_button_click(self.btn_restart, lambda: self.restart_game())
        self.btn_quit.callback = lambda: self.on_button_click(self.btn_quit, lambda: self.quit_to_menu())
             
        self.recalculate_layout()
        
    def recalculate_layout(self):
        cx = self.game.virtual_width // 2
        cy = self.game.virtual_height // 2
        
        # Center buttons vertically
        start_y = cy - 50
        spacing = 70
        
        self.btn_resume.x = cx - 100
        self.btn_resume.y = start_y
        
        self.btn_restart.x = cx - 100
        self.btn_restart.y = start_y + spacing
        
        self.btn_quit.x = cx - 100
        self.btn_quit.y = start_y + spacing * 2

    def on_button_click(self, button, callback):
        # Spawn particles
        for _ in range(20):
            # Spawn along the edges
            side = random.randint(0, 3)
            if side == 0: # Top
                px = button.x + random.random() * button.width
                py = button.y
                vx = (random.random() - 0.5) * 100
                vy = -random.random() * 100 - 50
            elif side == 1: # Bottom
                px = button.x + random.random() * button.width
                py = button.y + button.height
                vx = (random.random() - 0.5) * 100
                vy = random.random() * 100 + 50
            elif side == 2: # Left
                px = button.x
                py = button.y + random.random() * button.height
                vx = -random.random() * 100 - 50
                vy = (random.random() - 0.5) * 100
            else: # Right
                px = button.x + button.width
                py = button.y + random.random() * button.height
                vx = random.random() * 100 + 50
                vy = (random.random() - 0.5) * 100
                
            self.particle_system.emit(px, py, count=1, color=(0.5, 0.8, 1.0), vx=vx, vy=vy)
            
        # Execute action immediately (no delay needed for pause menu usually, but consistent feel is good)
        if callback:
            callback()

    def toggle_pause(self):
        self.paused = not self.paused
        if self.paused:
            pygame.mouse.set_visible(True)
            pygame.event.set_grab(False)
        else:
            pygame.mouse.set_visible(False)
            pygame.event.set_grab(True)
        
    def restart_game(self):
        self.__init__(self.game)
        
    def quit_to_menu(self):
        pygame.mouse.set_visible(True)
        pygame.event.set_grab(False)
        from src.scenes.menu_scene import MenuScene
        self.game.scene_manager.set_scene(MenuScene(self.game))

    def get_mouse_pos(self):
        return self.game.input_manager.get_mouse_pos()

    def handle_events(self, events):
        # Always handle resize/quit
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.toggle_pause()
                    
        if self.paused:
            vmx, vmy = self.get_mouse_pos()
            for btn in self.pause_buttons:
                btn.update(0, events, vmx, vmy)
        else:
            for event in events:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 3: # Right click
                        self.player.shoot()

    def trigger_shake(self, magnitude, duration):
        self.shake_magnitude = magnitude
        self.shake_timer = duration

    def update(self, dt):
        if self.paused:
            # Update UI animations
            vmx, vmy = self.get_mouse_pos()
            for btn in self.pause_buttons:
                btn.update(dt, [], vmx, vmy) # Pass empty events to just update anims
            
            self.particle_system.update(dt)
            return
            
        self.time += dt
        
        # Update Juice
        # Score Rolling
        diff = self.game.score - self.display_score
        if abs(diff) > 0:
            self.display_score += diff * 5 * dt
            if abs(self.game.score - self.display_score) < 1:
                self.display_score = self.game.score
                
        # Score Pulse Decay
        self.score_scale += (1.0 - self.score_scale) * 5 * dt
        
        # Health Bar Lerp
        hp_diff = self.player.hp - self.displayed_hp
        if abs(hp_diff) > 0.1:
            self.displayed_hp += hp_diff * 5 * dt
        else:
            self.displayed_hp = self.player.hp
        
        # Screen Shake
        if self.shake_timer > 0:
            self.shake_timer -= dt
            if self.shake_timer <= 0:
                self.shake_magnitude = 0
        
        # Store Player Previous Position for CCD
        player_prev_x, player_prev_y = self.player.x, self.player.y
        
        # Update player with virtual mouse coordinates
        vmx, vmy = self.get_mouse_pos()
        self.player.update(dt, vmx, vmy)
        
        self.wave_manager.update(dt)
        self.bullet_manager.update(dt)
        self.particle_system.update(dt)
        
        # Update Spatial Grid
        self.grid.clear()
        for e in self.wave_manager.enemies:
            if e.active:
                self.grid.insert(e)
                
        # Collision Logic
        self.collision_manager.update(dt)

    def render(self):
        # Calculate scale factors
        vw, vh = self.game.virtual_width, self.game.virtual_height
        ww, wh = self.game.window.width, self.game.window.height
        
        scale = min(ww / vw, wh / vh)
        tx = (ww - vw * scale) / 2
        ty = (wh - vh * scale) / 2
        
        # Setup Legacy Projection
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, ww, wh, 0, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
        # Scissor Test to clip legacy rendering to virtual viewport
        glEnable(GL_SCISSOR_TEST)
        glScissor(int(tx), int(ty), int(vw * scale), int(vh * scale))
        
        # --- POST PROCESSING START ---
        # Capture World Rendering
        self.game.post_processor.begin_capture()
        
        # We need to clear the FBO (it has its own clear color)
        # But wait, begin_capture clears it.
        # We need to setup projection for the FBO?
        # The FBO is size of window.
        # Legacy projection is setup for window size (0..ww, 0..wh).
        # So rendering should work fine.
        
        glPushMatrix()
        glTranslatef(tx, ty, 0)
        glScalef(scale, scale, 1.0)
        
        # Apply Screen Shake
        if self.shake_timer > 0:
            sx = (random.random() - 0.5) * self.shake_magnitude
            sy = (random.random() - 0.5) * self.shake_magnitude
            glTranslatef(sx, sy, 0)
        
        # Render Starfield
        self.starfield.render(self.time, (self.player.x, self.player.y))
        
        # Render Entities
        self.particle_system.render(scale)
        self.wave_manager.render()
        self.player_renderer.render(self.player)
        self.bullet_renderer.render(self.bullet_manager)
        
        glPopMatrix()
        
        self.game.post_processor.end_capture()
        # --- POST PROCESSING END ---
        
        glDisable(GL_SCISSOR_TEST)
        
        # Render Post-Processed Scene to Screen
        # We might want to apply scissor here too if we want black bars?
        # PostProcessor renders full screen quad.
        # If we want letterboxing, we should render quad inside the viewport?
        # Or just render full screen and let the black bars be black (cleared screen).
        # But PostProcessor texture contains the whole window content (including black bars area if we cleared it black).
        # Wait, we rendered to FBO with scissor test. So FBO has content only in viewport area.
        # So rendering full screen quad of FBO texture will show the content correctly.
        
        self.game.post_processor.render()
        
        self.game.post_processor.render()
        
        # Render UI (Health Bar) - In Virtual Space (Scaled)
        renderer = self.game.renderer
        renderer.begin_frame(self.game.virtual_width, self.game.virtual_height, self.game.window.width, self.game.window.height)
        
        self.hud.render(renderer)
                
        renderer.end_frame()
