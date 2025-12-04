from OpenGL.GL import *
import ctypes

class BulletRenderer:
    def __init__(self):
        pass

    def render(self, bullet_manager):
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE)
        glDisable(GL_TEXTURE_2D)
        glEnableClientState(GL_VERTEX_ARRAY)
        
        # Render Player Bullets (Cyan)
        if bullet_manager.p_count > 0:
            glBindBuffer(GL_ARRAY_BUFFER, bullet_manager.p_vbo)
            glBufferData(GL_ARRAY_BUFFER, bullet_manager.p_count * 4 * 4, bullet_manager.p_data[:bullet_manager.p_count], GL_DYNAMIC_DRAW)
            glVertexPointer(2, GL_FLOAT, 16, ctypes.c_void_p(0)) # stride 16 (4 floats)
            
            # Glow
            glPointSize(12) # Revert to original size
            glColor4f(0.0, 1.0, 1.0, 0.8) # Higher alpha for intensity
            glDrawArrays(GL_POINTS, 0, bullet_manager.p_count)
            
            # Core
            glPointSize(4)
            glColor4f(1.0, 1.0, 1.0, 0.9)
            glDrawArrays(GL_POINTS, 0, bullet_manager.p_count)
            
        # Render Enemy Bullets (Orange/Red)
        if bullet_manager.e_count > 0:
            glBindBuffer(GL_ARRAY_BUFFER, bullet_manager.e_vbo)
            glBufferData(GL_ARRAY_BUFFER, bullet_manager.e_count * 4 * 4, bullet_manager.e_data[:bullet_manager.e_count], GL_DYNAMIC_DRAW)
            glVertexPointer(2, GL_FLOAT, 16, ctypes.c_void_p(0))
            
            # Glow
            glPointSize(12) # Revert to original size
            glColor4f(1.0, 0.2, 0.0, 0.8) # Higher alpha for intensity
            glDrawArrays(GL_POINTS, 0, bullet_manager.e_count)
            
            # Core
            glPointSize(4)
            glColor4f(1.0, 1.0, 1.0, 0.9)
            glDrawArrays(GL_POINTS, 0, bullet_manager.e_count)
            
        glDisableClientState(GL_VERTEX_ARRAY)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
