import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

class Window:
    def __init__(self, width=800, height=600, title="Danmaku Game", fullscreen=False):
        self.width = width
        self.height = height
        self.title = title
        self.fullscreen = fullscreen
        
        self.init_window()

    def init_window(self):
        pygame.init()
        flags = DOUBLEBUF | OPENGL
        if self.fullscreen:
            flags |= FULLSCREEN
        
        self.screen = pygame.display.set_mode((self.width, self.height), flags)
        pygame.display.set_caption(self.title)
        
        # OpenGL Setup
        glViewport(0, 0, self.width, self.height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(0, self.width, self.height, 0) # Top-left origin
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    def flip(self):
        pygame.display.flip()

    def clear(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
