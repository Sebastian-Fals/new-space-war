import numpy as np
from OpenGL.GL import *
import random
import ctypes

class BulletManager:
    def __init__(self, particle_system=None):
        self.particle_system = particle_system
        self.capacity = 5000
        
        # x, y, dx, dy
        self.p_data = np.zeros((self.capacity, 4), dtype=np.float32)
        self.p_count = 0
        
        self.e_data = np.zeros((self.capacity, 4), dtype=np.float32)
        self.e_count = 0
        
        self.p_vbo = glGenBuffers(1)
        self.e_vbo = glGenBuffers(1)
        
    def spawn_bullet(self, x, y, dx, dy, type_str="player"):
        if type_str == "player":
            if self.p_count < self.capacity:
                self.p_data[self.p_count] = [x, y, dx, dy]
                self.p_count += 1
        else:
            if self.e_count < self.capacity:
                self.e_data[self.e_count] = [x, y, dx, dy]
                self.e_count += 1
                
    def update(self, dt):
        self._update_group(self.p_data, self.p_count, dt)
        self._update_group(self.e_data, self.e_count, dt)
        
        # Compact
        self.p_count = self._compact(self.p_data, self.p_count)
        self.e_count = self._compact(self.e_data, self.e_count)
        
        # Particles (Simplified)
        if self.particle_system:
            # Random emit logic...
            pass
            
    def _update_group(self, data, count, dt):
        if count == 0: return
        slice_ = data[:count]
        slice_[:, 0] += slice_[:, 2] * dt
        slice_[:, 1] += slice_[:, 3] * dt
        
    def _compact(self, data, count):
        if count == 0: return 0
        slice_ = data[:count]
        mask = (slice_[:, 0] >= -50) & (slice_[:, 0] <= 1330) & \
               (slice_[:, 1] >= -50) & (slice_[:, 1] <= 770)
        if not np.all(mask):
            kept = slice_[mask]
            k_len = len(kept)
            data[:k_len] = kept
            return k_len
        return count
        
    def render(self):
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE)
        glDisable(GL_TEXTURE_2D)
        glEnableClientState(GL_VERTEX_ARRAY)
        
        # Render Player Bullets (Cyan)
        if self.p_count > 0:
            glBindBuffer(GL_ARRAY_BUFFER, self.p_vbo)
            glBufferData(GL_ARRAY_BUFFER, self.p_count * 4 * 4, self.p_data[:self.p_count], GL_DYNAMIC_DRAW)
            glVertexPointer(2, GL_FLOAT, 16, ctypes.c_void_p(0)) # stride 16 (4 floats)
            
            # Glow
            glPointSize(12) # Revert to original size
            glColor4f(0.0, 1.0, 1.0, 0.8) # Higher alpha for intensity
            glDrawArrays(GL_POINTS, 0, self.p_count)
            
            # Core
            glPointSize(4)
            glColor4f(1.0, 1.0, 1.0, 0.9)
            glDrawArrays(GL_POINTS, 0, self.p_count)
            
        # Render Enemy Bullets (Orange/Red)
        if self.e_count > 0:
            glBindBuffer(GL_ARRAY_BUFFER, self.e_vbo)
            glBufferData(GL_ARRAY_BUFFER, self.e_count * 4 * 4, self.e_data[:self.e_count], GL_DYNAMIC_DRAW)
            glVertexPointer(2, GL_FLOAT, 16, ctypes.c_void_p(0))
            
            # Glow
            glPointSize(12) # Revert to original size
            glColor4f(1.0, 0.2, 0.0, 0.8) # Higher alpha for intensity
            glDrawArrays(GL_POINTS, 0, self.e_count)
            
            # Core
            glPointSize(4)
            glColor4f(1.0, 1.0, 1.0, 0.9)
            glDrawArrays(GL_POINTS, 0, self.e_count)
            
        glDisableClientState(GL_VERTEX_ARRAY)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
    # Compatibility wrapper for existing code accessing .bullets list
    # We need to expose a property 'bullets' that returns a list of dicts?
    # This would kill performance.
    # We need to update GameScene to NOT use .bullets list but use SpatialGrid or direct access.
    @property
    def bullets(self):
        # This is a fallback for collision logic if not updated yet.
        # Construct list of dicts from data. Very slow.
        res = []
        for i in range(self.p_count):
            res.append({"x": self.p_data[i,0], "y": self.p_data[i,1], "type": "player", "active": True})
        for i in range(self.e_count):
            res.append({"x": self.e_data[i,0], "y": self.e_data[i,1], "type": "enemy", "active": True})
        return res
