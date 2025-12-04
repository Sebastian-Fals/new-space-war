from OpenGL.GL import *
import numpy as np
from src.graphics.shader import Shader
import os
import sys

class WarpBackground:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            
        v_path = os.path.join(base_path, 'assets', 'shaders', 'starfield.vert') # Reuse vert
        f_path = os.path.join(base_path, 'assets', 'shaders', 'warp.frag')
        self.shader = Shader(v_path, f_path)
        
        self.vertices = np.array([
            -1.0, -1.0,
             1.0, -1.0,
             1.0,  1.0,
            -1.0,  1.0
        ], dtype=np.float32)
        
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)

    def resize(self, width, height):
        self.width = width
        self.height = height

    def render(self, time):
        self.shader.use()
        self.shader.set_uniform_1f("time", time)
        self.shader.set_uniform_2f("resolution", self.width, self.height)
        
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        position = glGetAttribLocation(self.shader.program, "position")
        glEnableVertexAttribArray(position)
        glVertexAttribPointer(position, 2, GL_FLOAT, GL_FALSE, 0, None)
        
        glDrawArrays(GL_QUADS, 0, 4)
        
        glDisableVertexAttribArray(position)
        glUseProgram(0)
