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
            e.update(dt)
            
    def spawn_enemy(self, difficulty):
        x = random.randint(100, 1180)
        y = -50
        type_id = random.randint(0, 4)
        # We need bullet_manager here. 
        # WaveManager has 'game' (which is actually GameScene now).
        # GameScene has bullet_manager.
        enemy = Enemy(x, y, type_id, self.game.bullet_manager, difficulty)
        self.enemies.append(enemy)

    def render(self):
        for e in self.enemies:
            e.render()
        if self.boss:
            self.boss.render()
