import random
from src.entities.enemy import Enemy
from src.entities.boss import Boss

class WaveManager:
    def __init__(self, game):
        self.game = game
        self.wave = 1
        self.enemies = []
        self.wave_timer = 0
        self.spawn_timer = 0
        self.boss = None
        
    def update(self, dt):
        self.wave_timer += dt
        self.spawn_timer += dt
        
        # Clean up dead enemies
        self.enemies = [e for e in self.enemies if e.active]
        
        if self.boss:
            self.boss.update(dt)
            if not self.boss.active:
                self.boss = None
                # Win condition or next loop
            return

        # Wave logic
        if self.wave == 10:
            if not self.boss:
                self.boss = Boss(640, -100, self.game.bullet_manager)
                self.game.game.audio_manager.play_music("boss")
            return
            
        # Spawn enemies for current wave
        diff = getattr(self.game.game, 'difficulty', 'medium')
        spawn_mult = 1.0
        if diff == 'easy': spawn_mult = 1.0
        elif diff == 'medium': spawn_mult = 0.7
        elif diff == 'hard': spawn_mult = 0.5
        elif diff == 'extreme': spawn_mult = 0.3
        
        base_interval = 2.0 - (self.wave * 0.1)
        if base_interval < 0.5: base_interval = 0.5
        
        if self.wave_timer > 3.0 and self.spawn_timer > base_interval * spawn_mult: 
            self.spawn_enemy(diff)
            self.spawn_timer = 0
            
        # Next wave condition (time based for now)
        if self.wave_timer > 25.0: # Longer waves
            self.wave += 1
            self.wave_timer = 0
            print(f"Wave {self.wave} Started!")

        for e in self.enemies:
            e.update(dt, self.game.player)
            
    def spawn_enemy(self, difficulty):
        # Determine if we should spawn a group
        # All types spawn in groups of 1-5
        type_id = random.randint(0, 4)
        count = random.randint(1, 5)
        
        # Spacing/Mode based on type
        spacing = 50
        mode = 'tight'
        
        if type_id == 0: # Red - Sine
            spacing = 60
            mode = 'tight'
        elif type_id == 1: # Green - Zigzag
            spacing = 200
            mode = 'spread'
        elif type_id == 2: # Blue - Kamikaze
            spacing = 50
            mode = 'tight'
        elif type_id == 3: # Yellow - Stop/Shoot
            spacing = 250
            mode = 'spread'
        elif type_id == 4: # Purple - Orbit
            spacing = 40
            mode = 'tight'
            
        self.spawn_group(type_id, difficulty, count, spacing, mode)

    def spawn_group(self, type_id, difficulty, count, spacing, mode='tight'):
        if mode == 'tight':
            # Spawn a group centered around a random X
            center_x = random.randint(100 + (count * spacing)//2, 1180 - (count * spacing)//2)
            start_x = center_x - ((count - 1) * spacing) // 2
            
            for i in range(count):
                x = start_x + i * spacing
                y = -50 - (i * 30) # Stagger Y slightly
                enemy = Enemy(x, y, type_id, self.game.bullet_manager, difficulty)
                self.enemies.append(enemy)
        else: # spread
            # Distribute across screen width or random positions
            # Simple approach: Pick random X for each, ensuring some distance?
            # Or just random X.
            for i in range(count):
                x = random.randint(100, 1180)
                y = -50 - (i * 50) # More stagger
                enemy = Enemy(x, y, type_id, self.game.bullet_manager, difficulty)
                self.enemies.append(enemy)

    def render(self):
        for e in self.enemies:
            e.render()
        if self.boss:
            self.boss.render()
