import ctypes
from OpenGL.GL import *
from src.graphics.shader import Shader
import numpy as np

class PostProcessor:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        
        # Settings
        self.use_bloom = True
        self.use_vignette = True
        self.use_chromatic = False
        self.use_fxaa = False # Placeholder
        
        # Load Shaders
        self.shader_post = Shader('assets/shaders/post_process.vert', 'assets/shaders/uber_post.frag')
        self.shader_bloom_threshold = Shader('assets/shaders/post_process.vert', 'assets/shaders/bloom_threshold.frag')
        self.shader_bloom_blur = Shader('assets/shaders/post_process.vert', 'assets/shaders/bloom_blur.frag')
        
        # Initialize FBOs
        self.init_framebuffers(width, height)
        
        # Quad VAO
        self.quad_vao = glGenVertexArrays(1)
        self.quad_vbo = glGenBuffers(1)
        
        # Full screen quad
        quad_vertices = np.array([
            # Pos        # TexCoords
            -1.0,  1.0,  0.0, 1.0,
            -1.0, -1.0,  0.0, 0.0,
             1.0, -1.0,  1.0, 0.0,

            -1.0,  1.0,  0.0, 1.0,
             1.0, -1.0,  1.0, 0.0,
             1.0,  1.0,  1.0, 1.0
        ], dtype=np.float32)
        
        glBindVertexArray(self.quad_vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.quad_vbo)
        glBufferData(GL_ARRAY_BUFFER, quad_vertices.nbytes, quad_vertices, GL_STATIC_DRAW)
        
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 4 * 4, ctypes.c_void_p(0))
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 4 * 4, ctypes.c_void_p(2 * 4))
        glBindVertexArray(0)
        
    def init_framebuffers(self, width, height):
        # Main FBO (Scene)
        self.msfbo = glGenFramebuffers(1)
        glBindFramebuffer(GL_FRAMEBUFFER, self.msfbo)
        
        self.tex_color = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.tex_color)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB16F, width, height, 0, GL_RGB, GL_FLOAT, None) # HDR
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, self.tex_color, 0)
        
        # RBO for Depth/Stencil
        self.rbo = glGenRenderbuffers(1)
        glBindRenderbuffer(GL_RENDERBUFFER, self.rbo)
        glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH24_STENCIL8, width, height)
        glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_STENCIL_ATTACHMENT, GL_RENDERBUFFER, self.rbo)
        
        if glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE:
            print("ERROR::FRAMEBUFFER:: Framebuffer is not complete!")
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        
        # PingPong FBOs for Bloom (Downsampled to half resolution)
        self.pingpong_fbo = glGenFramebuffers(2)
        self.pingpong_colorbuffers = glGenTextures(2)
        
        # Half resolution for bloom
        self.bloom_width = width // 2
        self.bloom_height = height // 2
        
        for i in range(2):
            glBindFramebuffer(GL_FRAMEBUFFER, self.pingpong_fbo[i])
            glBindTexture(GL_TEXTURE_2D, self.pingpong_colorbuffers[i])
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB16F, self.bloom_width, self.bloom_height, 0, GL_RGB, GL_FLOAT, None)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE) 
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
            glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, self.pingpong_colorbuffers[i], 0)
            
            if glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE:
                print(f"ERROR::FRAMEBUFFER:: PingPong Framebuffer {i} is not complete!")
                
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        
    def resize(self, width, height):
        self.width = width
        self.height = height
        # Delete old
        glDeleteFramebuffers(1, [self.msfbo])
        glDeleteTextures(1, [self.tex_color])
        glDeleteRenderbuffers(1, [self.rbo])
        glDeleteFramebuffers(2, self.pingpong_fbo)
        glDeleteTextures(2, self.pingpong_colorbuffers)
        
        # Re-init
        self.init_framebuffers(width, height)
        
    def begin_capture(self):
        glBindFramebuffer(GL_FRAMEBUFFER, self.msfbo)
        glViewport(0, 0, self.width, self.height) # Ensure full viewport
        glClearColor(0.0, 0.0, 0.0, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
    def end_capture(self):
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        
    def render(self):
        # 1. Bloom Threshold (Extract Brights) -> PingPong[0]
        
        horizontal = True
        first_iteration = True
        amount = 4 # Reduced iterations (was 10)
        
        if self.use_bloom:
            # Set viewport to half size for bloom
            glViewport(0, 0, self.bloom_width, self.bloom_height)
            
            glBindFramebuffer(GL_FRAMEBUFFER, self.pingpong_fbo[0])
            glClear(GL_COLOR_BUFFER_BIT)
            self.shader_bloom_threshold.use()
            self.shader_bloom_threshold.set_uniform_1i("sceneTexture", 0)
            self.shader_bloom_threshold.set_uniform_1f("threshold", 0.6)
            glActiveTexture(GL_TEXTURE0)
            glBindTexture(GL_TEXTURE_2D, self.tex_color)
            self.render_quad()
            
            # 2. Blur PingPong[0] -> PingPong[1] -> PingPong[0]...
            self.shader_bloom_blur.use()
            self.shader_bloom_blur.set_uniform_1i("image", 0)
            
            for i in range(amount):
                glBindFramebuffer(GL_FRAMEBUFFER, self.pingpong_fbo[int(horizontal)])
                self.shader_bloom_blur.set_uniform_1i("horizontal", int(horizontal))
                
                glActiveTexture(GL_TEXTURE0)
                
                if first_iteration:
                    glBindTexture(GL_TEXTURE_2D, self.pingpong_colorbuffers[0]) # Read from extracted
                    first_iteration = False
                else:
                    glBindTexture(GL_TEXTURE_2D, self.pingpong_colorbuffers[int(not horizontal)])
                    
                self.render_quad()
                horizontal = not horizontal
                
        # 3. Final Combine (Uber Shader)
        glBindFramebuffer(GL_FRAMEBUFFER, 0) # Back to screen
        # Restore full viewport
        glViewport(0, 0, self.width, self.height)
        
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        self.shader_post.use()
        self.shader_post.set_uniform_1i("sceneTexture", 0)
        self.shader_post.set_uniform_1i("bloomTexture", 1)
        self.shader_post.set_uniform_1i("useBloom", int(self.use_bloom))
        self.shader_post.set_uniform_1i("useVignette", int(self.use_vignette))
        self.shader_post.set_uniform_1i("useChromaticAberration", int(self.use_chromatic))
        
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.tex_color)
        
        glActiveTexture(GL_TEXTURE1)
        # The last write was to the buffer we just unbound.
        # If amount is even (4), last write was to 0.
        glBindTexture(GL_TEXTURE_2D, self.pingpong_colorbuffers[0] if self.use_bloom else 0)
        
        self.render_quad()
        
    def render_quad(self):
        glBindVertexArray(self.quad_vao)
        glDrawArrays(GL_TRIANGLES, 0, 6)
        glBindVertexArray(0)
