from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader

class Shader:
    def __init__(self, vertex_path, fragment_path):
        self.program = self.load_shaders(vertex_path, fragment_path)

    def load_shaders(self, vertex_path, fragment_path):
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
