import numpy as np
from OpenGL.GL import *
import random
import ctypes

class ParticleSystem:
    def __init__(self):
        self.capacity = 5000
        self.count = 0
        
        # New Layout: x, y, r, g, b, life(a), size, vx, vy
        # Indices:    0, 1, 2, 3, 4, 5,       6,    7,  8
        self.data = np.zeros((self.capacity, 9), dtype=np.float32)
        
        self.vbo = glGenBuffers(1)
        
    def emit(self, x, y, count=1, color=(1, 1, 1), vx=None, vy=None):
        if self.count + count > self.capacity:
            count = self.capacity - self.count
            if count <= 0: return
            
        # Base values
        start = self.count
        end = start + count
        
        # Positions (0, 1)
        self.data[start:end, 0] = x
        self.data[start:end, 1] = y
        
        # Color & Life (2, 3, 4, 5)
        self.data[start:end, 2] = color[0]
        self.data[start:end, 3] = color[1]
        self.data[start:end, 4] = color[2]
        self.data[start:end, 5] = 1.0 # Life starts at 1.0
        
        # Size (6)
        self.data[start:end, 6] = np.random.uniform(2, 4, count)
        
        # Velocities (7, 8)
        if vx is not None and vy is not None:
             self.data[start:end, 7] = vx + np.random.uniform(-50, 50, count)
             self.data[start:end, 8] = vy + np.random.uniform(-50, 50, count)
        else:
             self.data[start:end, 7] = np.random.uniform(-150, 150, count)
             self.data[start:end, 8] = np.random.uniform(-150, 150, count)
        
        self.count += count
        
    def update(self, dt):
        if self.count == 0: return
        
        slice_ = self.data[:self.count]
        
        # Update pos (x+=vx*dt, y+=vy*dt)
        slice_[:, 0] += slice_[:, 7] * dt
        slice_[:, 1] += slice_[:, 8] * dt
        
        # Gravity (vy += 200 * dt) -> Index 8
        slice_[:, 8] += 200 * dt
        
        # Life (index 5)
        slice_[:, 5] -= dt * 1.5
        
        # Size (index 6)
        slice_[:, 6] -= dt * 1.0
        
        # Remove dead (life > 0) AND off-screen
        mask = (slice_[:, 5] > 0) & \
               (slice_[:, 0] >= -50) & (slice_[:, 0] <= 1330) & \
               (slice_[:, 1] >= -50) & (slice_[:, 1] <= 770)
        if not np.all(mask):
            kept = slice_[mask]
            k_len = len(kept)
            self.data[:k_len] = kept
            self.count = k_len
            
    def render(self, scale=1.0):
        if self.count == 0: return
        
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE)
        glDisable(GL_TEXTURE_2D)
        
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        # Upload data
        # Stride is 9 floats * 4 = 36 bytes
        glBufferData(GL_ARRAY_BUFFER, self.count * 9 * 4, self.data[:self.count], GL_DYNAMIC_DRAW)
        
        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_COLOR_ARRAY)
        
        # Vertex: x, y (offset 0)
        glVertexPointer(2, GL_FLOAT, 36, ctypes.c_void_p(0))
        
        # Color: r, g, b, a (offset 2 floats * 4 = 8 bytes)
        glColorPointer(4, GL_FLOAT, 36, ctypes.c_void_p(8))
        
        # We can also use glPointSize to vary size if we want, but it's global in fixed pipeline usually,
        # unless we use vertex shader or GL_PROGRAM_POINT_SIZE.
        # For now, fixed size or average size.
        glPointSize(3 * scale) 
        
        glDrawArrays(GL_POINTS, 0, self.count)
        
        glDisableClientState(GL_VERTEX_ARRAY)
        glDisableClientState(GL_COLOR_ARRAY)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
