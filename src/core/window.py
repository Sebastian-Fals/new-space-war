import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

class Window:
    def __init__(self, width, height, title, fullscreen=False, msaa=True):
        self.width = width
        self.height = height
        self.fullscreen = fullscreen
        
        pygame.init()
        
        # MSAA
        if msaa:
            pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLEBUFFERS, 1)
            pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLESAMPLES, 4)
        else:
            pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLEBUFFERS, 0)
            pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLESAMPLES, 0)
        
        flags = DOUBLEBUF | OPENGL | RESIZABLE
        if fullscreen:
            flags |= FULLSCREEN
            
        self.screen = pygame.display.set_mode((width, height), flags)
        pygame.display.set_caption(title)
        
        glViewport(0, 0, width, height)
        
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(0, self.width, self.height, 0) # Top-left origin
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    def resize(self, w, h):
        self.width = w
        self.height = h
        self.screen = pygame.display.set_mode((self.width, self.height), DOUBLEBUF | OPENGL | RESIZABLE | (FULLSCREEN if self.fullscreen else 0))
        glViewport(0, 0, self.width, self.height)
        
        # Update legacy projection
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(0, self.width, self.height, 0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    def flip(self):
        pygame.display.flip()

    def clear(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
