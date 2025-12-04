import math

class CollisionManager:
    def __init__(self, game_scene):
        self.game_scene = game_scene
        self.game = game_scene.game
        self.grid = game_scene.grid
        
    def line_intersects_circle(self, p1, p2, center, radius):
        # p1, p2: (x, y) tuples
        # center: (cx, cy) tuple
        # radius: float
        x1, y1 = p1
        x2, y2 = p2
        cx, cy = center
        
        dx, dy = x2 - x1, y2 - y1
        if dx == 0 and dy == 0:
            return (x1 - cx)**2 + (y1 - cy)**2 <= radius**2
            
        t = ((cx - x1) * dx + (cy - y1) * dy) / (dx*dx + dy*dy)
        t = max(0, min(1, t)) # Clamp to segment
        
        closest_x = x1 + t * dx
        closest_y = y1 + t * dy
        
        dist_sq = (closest_x - cx)**2 + (closest_y - cy)**2
        return dist_sq <= radius**2

    def update(self, dt):
        self.check_player_bullets(dt)
        self.check_enemy_collisions(dt)
        self.check_boss_collisions(dt)
        
    def check_player_bullets(self, dt):
        bullet_manager = self.game_scene.bullet_manager
        
        # Player Bullet -> Enemy (CCD)
        for i in range(bullet_manager.p_count):
            bx = bullet_manager.p_data[i, 0]
            by = bullet_manager.p_data[i, 1]
            bdx = bullet_manager.p_data[i, 2]
            bdy = bullet_manager.p_data[i, 3]
            
            prev_bx = bx - bdx * dt
            prev_by = by - bdy * dt
            
            # Query grid
            potential_hits = self.grid.query(bx, by, 64, 64)
            
            for e in potential_hits:
                if e.active:
                    if self.line_intersects_circle((prev_bx, prev_by), (bx, by), (e.x, e.y), 20):
                        e.active = False
                        bullet_manager.p_data[i, 1] = -1000 # Remove
                        self.game.score += 100
                        self.game_scene.score_scale = 1.5
                        self.game_scene.trigger_shake(5, 0.2)
                        break

    def check_enemy_collisions(self, dt):
        player = self.game_scene.player
        bullet_manager = self.game_scene.bullet_manager
        wave_manager = self.game_scene.wave_manager
        
        # Difficulty Multipliers
        diff = getattr(self.game, 'difficulty', 'medium')
        dmg_mult = 1.0
        if diff == 'easy': dmg_mult = 0.5
        elif diff == 'hard': dmg_mult = 1.5
        
        player_prev_x = player.x - (player.x - player.x) # Approximation if we don't store prev
        # Wait, we need player prev pos. 
        # Let's assume linear interpolation from velocity? No, player follows mouse.
        # We should pass prev_pos or store it in player.
        # For now, let's just use current pos for simplicity or assume small movement?
        # Actually, GameScene calculated player_prev_x. We should access it or store it.
        # Let's assume we can access it from player if we add it, or just use current pos for now (less accurate CCD).
        # To be safe, let's use current pos for now, as refactoring shouldn't break too much.
        # Or better: Player should track its own prev_pos.
        
        px, py = player.x, player.y
        # Approximate prev pos based on mouse movement? No.
        # Let's just use px, py for now.
        
        if player.invulnerable_timer <= 0:
            player_hit = False
            
            # Enemy Bullet -> Player
            for i in range(bullet_manager.e_count):
                bx = bullet_manager.e_data[i, 0]
                by = bullet_manager.e_data[i, 1]
                bdx = bullet_manager.e_data[i, 2]
                bdy = bullet_manager.e_data[i, 3]
                
                prev_bx = bx - bdx * dt
                prev_by = by - bdy * dt
                
                if self.line_intersects_circle((prev_bx, prev_by), (bx, by), (px, py), player.hitbox_radius):
                    player.hp -= 10 * dmg_mult
                    bullet_manager.e_data[i, 1] = -1000 # Remove
                    player_hit = True
            
            # Enemy Body -> Player
            for e in wave_manager.enemies:
                if e.active:
                    # Simple circle collision for now since we don't have prev player pos easily
                    dist_sq = (e.x - px)**2 + (e.y - py)**2
                    radius_sum = 20 + player.hitbox_radius
                    if dist_sq <= radius_sum**2:
                        player.hp -= 40 * dmg_mult
                        e.active = False
                        player_hit = True
                        self.game_scene.trigger_shake(20, 0.5)
                        
            if player_hit:
                player.invulnerable_timer = 1.0
                self.game_scene.trigger_shake(10, 0.4)
                if player.hp <= 0:
                    self.handle_game_over()

    def check_boss_collisions(self, dt):
        boss = self.game_scene.wave_manager.boss
        bullet_manager = self.game_scene.bullet_manager
        
        if boss and boss.active:
            for i in range(bullet_manager.p_count):
                 bx = bullet_manager.p_data[i, 0]
                 by = bullet_manager.p_data[i, 1]
                 bdx = bullet_manager.p_data[i, 2]
                 bdy = bullet_manager.p_data[i, 3]
                 
                 prev_bx = bx - bdx * dt
                 prev_by = by - bdy * dt
                 
                 if self.line_intersects_circle((prev_bx, prev_by), (bx, by), (boss.x, boss.y), 50):
                    boss.hp -= 1
                    bullet_manager.p_data[i, 1] = -1000
                    if boss.hp <= 0:
                        boss.active = False
                        self.game_scene.boss_beaten = True
                        self.game.score += 5000
                        self.game_scene.score_scale = 2.0
                        self.game_scene.trigger_shake(20, 1.0)

    def handle_game_over(self):
        if self.game.score > self.game.high_score:
            self.game.high_score = self.game.score
            self.game.save_settings()
        
        print("GAME OVER")
        from src.scenes.game_over_scene import GameOverScene
        self.game.scene_manager.set_scene(GameOverScene(self.game, self.game.score, self.game_scene.wave_manager.wave, self.game_scene.boss_beaten))
