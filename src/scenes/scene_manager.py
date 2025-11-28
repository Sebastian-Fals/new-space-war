class Scene:
    def __init__(self, game):
        self.game = game

    def handle_events(self, events):
        pass

    def update(self, dt):
        pass

    def render(self):
        pass

class SceneManager:
    def __init__(self, game):
        self.game = game
        self.current_scene = None
        
    def set_scene(self, scene):
        self.current_scene = scene
        
    def update(self, dt):
        if self.current_scene:
            self.current_scene.update(dt)
            
    def render(self):
        if self.current_scene:
            self.current_scene.render()
            
    def handle_events(self, events):
        if self.current_scene:
            self.current_scene.handle_events(events)
