import pygame
import os

import sys

class AudioManager:
    def __init__(self):
        pygame.mixer.init()
        self.music_volume = 0.5
        self.sfx_volume = 0.5
        self.current_track = None
        
        # Resolve base path
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.getcwd()
            
        # Preload paths
        self.music_path = os.path.join(base_path, "assets", "music")
        self.tracks = {
            "menu": os.path.join(self.music_path, "Main_menu-theme.mp3"),
            "game": os.path.join(self.music_path, "Galactic-Showdown.mp3"),
            "boss": os.path.join(self.music_path, "Boss-theme.mp3")
        }
        
    def play_music(self, track_name, fade_ms=1000, loop=-1, force_restart=False):
        if track_name not in self.tracks:
            print(f"Track {track_name} not found.")
            return
            
        path = self.tracks[track_name]
        
        if self.current_track == track_name and pygame.mixer.music.get_busy() and not force_restart:
            return # Already playing
            
        self.current_track = track_name
        
        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(self.music_volume)
            pygame.mixer.music.play(loops=loop, fade_ms=fade_ms)
        except Exception as e:
            print(f"Failed to play music {track_name}: {e}")
            
    def stop_music(self, fade_ms=1000):
        pygame.mixer.music.fadeout(fade_ms)
        self.current_track = None
        
    def set_music_volume(self, volume):
        self.music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.music_volume)
        
    def set_sfx_volume(self, volume):
        self.sfx_volume = max(0.0, min(1.0, volume))
        # Update any active channels if needed, or just store for future sounds
