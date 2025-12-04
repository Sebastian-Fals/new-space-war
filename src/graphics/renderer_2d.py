import pygame
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import numpy as np
import ctypes

class Renderer2D:
    def __init__(self):
        self.shader = self._create_shader()
        self.vao = glGenVertexArrays(1)
        self.vbo = glGenBuffers(1)
        
        # Vertex format: x, y, u, v, r, g, b, a (8 floats)
        self.vertex_size = 8 * 4 # 4 bytes per float
        
        glBindVertexArray(self.vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        
        # Initial buffer size (can grow)
        self.max_vertices = 10000
        glBufferData(GL_ARRAY_BUFFER, self.max_vertices * self.vertex_size, None, GL_DYNAMIC_DRAW)
        
        # Position (0)
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, self.vertex_size, ctypes.c_void_p(0))
        
        # UV (1)
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, self.vertex_size, ctypes.c_void_p(2 * 4))
        
        # Color (2)
        glEnableVertexAttribArray(2)
        glVertexAttribPointer(2, 4, GL_FLOAT, GL_FALSE, self.vertex_size, ctypes.c_void_p(4 * 4))
        
        glBindVertexArray(0)
        
        self.projection_loc = glGetUniformLocation(self.shader, "projection")
        
    def _create_shader(self):
        vertex_src = """
        #version 330 core
        layout (location = 0) in vec2 aPos;
        layout (location = 1) in vec2 aTexCoord;
        layout (location = 2) in vec4 aColor;
        
        out vec2 TexCoord;
        out vec4 Color;
        
        uniform mat4 projection;
        
        void main() {
            gl_Position = projection * vec4(aPos, 0.0, 1.0);
            TexCoord = aTexCoord;
            Color = aColor;
        }
        """
        
        fragment_src = """
        #version 330 core
        in vec2 TexCoord;
        in vec4 Color;
        
        out vec4 FragColor;
        
        uniform sampler2D textTexture;
        uniform bool useTexture;
        
        void main() {
            if (useTexture) {
                vec4 texColor = texture(textTexture, TexCoord);
                FragColor = texColor * Color;
            } else {
                FragColor = Color;
            }
        }
        """
        
        return compileProgram(
            compileShader(vertex_src, GL_VERTEX_SHADER),
            compileShader(fragment_src, GL_FRAGMENT_SHADER)
        )
        
    def begin_frame(self, vw, vh, ww, wh):
        glUseProgram(self.shader)
        
        # Calculate scale and offset for letterboxing
        scale = min(ww / vw, wh / vh)
        tx = (ww - vw * scale) / 2
        ty = (wh - vh * scale) / 2
        
        # Orthographic projection for the WINDOW
        # Maps 0..ww, 0..wh to -1..1
        left, right, bottom, top = 0, ww, wh, 0
        near, far = -1, 1
        
        ortho = np.array([
            [2/(right-left), 0, 0, 0],
            [0, 2/(top-bottom), 0, 0],
            [0, 0, -2/(far-near), 0],
            [-(right+left)/(right-left), -(top+bottom)/(top-bottom), -(far+near)/(far-near), 1]
        ], dtype=np.float32)
        
        # Model matrix: Scale and Translate
        # We want to transform Virtual Coords to Window Coords
        # x_win = x_virt * scale + tx
        # y_win = y_virt * scale + ty
        
        # Matrix multiplication order (column-major in OpenGL, but numpy is row-major, 
        # so we usually transpose or write it carefully.
        # Here we construct matrices and multiply them.
        
        # Scale Matrix
        S = np.array([
            [scale, 0, 0, 0],
            [0, scale, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ], dtype=np.float32)
        
        # Translate Matrix
        T = np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 1, 0],
            [tx, ty, 0, 1]
        ], dtype=np.float32)
        
        # MVP = Ortho * Translate * Scale
        # Note: In numpy (row-major), v' = v * M
        # So v_win = v_virt * S * T
        # v_ndc = v_win * Ortho
        # v_ndc = v_virt * S * T * Ortho
        
        # Wait, standard math is usually column vectors: v' = M * v
        # OpenGL expects column-major matrices.
        # glUniformMatrix4fv with transpose=GL_FALSE expects column-major.
        # Numpy arrays are row-major.
        # If we write [ [1, 0, 0, tx], ... ] that's a row-major representation of a matrix.
        # If we pass it as is, OpenGL reads it as column-major.
        # So [1, 0, 0, tx] becomes the first COLUMN.
        # Which means T[0][3] is tx.
        
        # Let's stick to standard OpenGL matrix layout (Column-Major) flattened.
        # Or just use numpy matmul and transpose=GL_TRUE?
        # Or construct it correctly.
        
        # Let's use the simple approach:
        # We want to map (0,0) -> (-1 + 2*tx/ww, 1 - 2*ty/wh) ...
        
        # Let's just construct the final matrix directly.
        # x_ndc = (x_virt * scale + tx) / ww * 2 - 1
        # y_ndc = (y_virt * scale + ty) / wh * -2 + 1 (flipped Y)
        
        # x_ndc = x_virt * (2*scale/ww) + (2*tx/ww - 1)
        # y_ndc = y_virt * (-2*scale/wh) + (1 - 2*ty/wh)
        
        m00 = 2 * scale / ww
        m11 = -2 * scale / wh
        m30 = 2 * tx / ww - 1
        m31 = 1 - 2 * ty / wh
        
        mvp = np.array([
            [m00, 0, 0, 0],
            [0, m11, 0, 0],
            [0, 0, -1, 0],
            [m30, m31, 0, 1]
        ], dtype=np.float32)
        
        glUniformMatrix4fv(self.projection_loc, 1, GL_FALSE, mvp)
        
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        glBindVertexArray(self.vao)
        
    def end_frame(self):
        glBindVertexArray(0)
        glUseProgram(0)
        
    def draw_rect(self, x, y, w, h, color, gradient_bot=None):
        # 6 vertices for a quad (2 triangles)
        # x, y, u, v, r, g, b, a
        r, g, b, a = color
        
        if gradient_bot:
            r2, g2, b2, a2 = gradient_bot
        else:
            r2, g2, b2, a2 = r, g, b, a
            
        # Top vertices use color, Bottom vertices use gradient_bot (or color)
        vertices = np.array([
            x, y, 0, 0, r, g, b, a,          # Top Left
            x+w, y, 0, 0, r, g, b, a,        # Top Right
            x+w, y+h, 0, 0, r2, g2, b2, a2,  # Bottom Right
            
            x, y, 0, 0, r, g, b, a,          # Top Left
            x+w, y+h, 0, 0, r2, g2, b2, a2,  # Bottom Right
            x, y+h, 0, 0, r2, g2, b2, a2     # Bottom Left
        ], dtype=np.float32)
        
        self._upload_and_draw(vertices)

    def draw_chamfered_rect(self, x, y, w, h, color, radius=10, gradient_bot=None):
        # Approximate chamfered rect with a triangle fan or just multiple rects/triangles
        
        cut = min(radius, min(w, h) / 2)
        r, g, b, a = color
        
        if gradient_bot:
            r2, g2, b2, a2 = gradient_bot
        else:
            r2, g2, b2, a2 = r, g, b, a
            
        # Helper to interpolate color based on Y
        def get_color(py):
            # 0 at y, 1 at y+h
            t = (py - y) / h
            t = max(0, min(1, t))
            return (
                r * (1-t) + r2 * t,
                g * (1-t) + g2 * t,
                b * (1-t) + b2 * t,
                a * (1-t) + a2 * t
            )
            
        # Center
        cx, cy = x + w/2, y + h/2
        cr, cg, cb, ca = get_color(cy)
        
        # Vertices for the perimeter
        perimeter = [
            (x + cut, y), (x + w - cut, y), # Top
            (x + w, y + cut), (x + w, y + h - cut), # Right
            (x + w - cut, y + h), (x + cut, y + h), # Bottom
            (x, y + h - cut), (x, y + cut) # Left
        ]
        
        vertices = []
        for i in range(len(perimeter)):
            p1 = perimeter[i]
            p2 = perimeter[(i + 1) % len(perimeter)]
            
            # Colors for p1, p2
            c1 = get_color(p1[1])
            c2 = get_color(p2[1])
            
            # Triangle: Center, P1, P2
            vertices.extend([
                cx, cy, 0, 0, cr, cg, cb, ca,
                p1[0], p1[1], 0, 0, c1[0], c1[1], c1[2], c1[3],
                p2[0], p2[1], 0, 0, c2[0], c2[1], c2[2], c2[3]
            ])
            
        self._upload_and_draw(np.array(vertices, dtype=np.float32))

    def _upload_and_draw(self, vertices):
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        # Orphan buffer or use subdata? For now, subdata is fine for immediate-like mode
        # But actually, glBufferSubData is better if we are not replacing everything
        # For this simple implementation, we'll just upload and draw immediately
        # NOTE: This is not the most efficient batching, but it replaces glBegin/glEnd correctly
        
        glBufferSubData(GL_ARRAY_BUFFER, 0, vertices.nbytes, vertices)
        
        glUniform1i(glGetUniformLocation(self.shader, "useTexture"), False)
        glDrawArrays(GL_TRIANGLES, 0, len(vertices) // 8)

    def draw_texture(self, texture_id, x, y, w, h, color=(1,1,1,1)):
        r, g, b, a = color
        
        vertices = np.array([
            x, y, 0, 1, r, g, b, a,
            x+w, y, 1, 1, r, g, b, a,
            x+w, y+h, 1, 0, r, g, b, a,
            
            x, y, 0, 1, r, g, b, a,
            x+w, y+h, 1, 0, r, g, b, a,
            x, y+h, 0, 0, r, g, b, a
        ], dtype=np.float32)
        
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferSubData(GL_ARRAY_BUFFER, 0, vertices.nbytes, vertices)
        
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, texture_id)
        glUniform1i(glGetUniformLocation(self.shader, "useTexture"), True)
        glUniform1i(glGetUniformLocation(self.shader, "textTexture"), 0)
        
        glDrawArrays(GL_TRIANGLES, 0, 6)
