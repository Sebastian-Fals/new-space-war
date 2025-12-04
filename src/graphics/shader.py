from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader

import sys
import os

class Shader:
    def __init__(self, vertex_path, fragment_path):
        self.program = self.load_shaders(vertex_path, fragment_path)

    def resolve_path(self, path):
        if getattr(sys, 'frozen', False):
            # If frozen (PyInstaller), use _MEIPASS
            base_path = sys._MEIPASS
            return os.path.join(base_path, path)
        return path

    def load_shaders(self, vertex_path, fragment_path):
        vertex_path = self.resolve_path(vertex_path)
        fragment_path = self.resolve_path(fragment_path)
        
        with open(vertex_path, 'r') as f:
            vertex_src = f.read()
        
        with open(fragment_path, 'r') as f:
            fragment_src = f.read()
            
        shader = compileProgram(
            compileShader(vertex_src, GL_VERTEX_SHADER),
            compileShader(fragment_src, GL_FRAGMENT_SHADER)
        )
        return shader

    def use(self):
        glUseProgram(self.program)
        
    def set_uniform_1f(self, name, value):
        loc = glGetUniformLocation(self.program, name)
        glUniform1f(loc, value)
        
    def set_uniform_2f(self, name, x, y):
        loc = glGetUniformLocation(self.program, name)
        glUniform2f(loc, x, y)

    def set_uniform_1i(self, name, value):
        loc = glGetUniformLocation(self.program, name)
        glUniform1i(loc, value)
        
    def set_uniform_3f(self, name, x, y, z):
        loc = glGetUniformLocation(self.program, name)
        glUniform3f(loc, x, y, z)
