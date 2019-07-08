import pyrr
import numpy as np
from OpenGL.GL import *
from Entity import Entity


class Renderer:
    def __init__(self, shader):
        self.shapeBuffers = []
        self.shader = shader
        self.quadVAO = -1
        self.VBO = -1
        self.IBO = -1
        self.init_render_data()

    def draw_polygon(self, polygon: Entity):
        vertex_float_list = polygon.get_vertices()
        index_list = Entity.basis_arrays[polygon.sides].indexBuffer

        # Configure VBO
        glBindBuffer(GL_ARRAY_BUFFER, self.VBO)
        glBufferData(GL_ARRAY_BUFFER, vertex_float_list, GL_DYNAMIC_DRAW)

        # Configure IBO
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.IBO)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, index_list, GL_DYNAMIC_DRAW)

        # Transformation is unused; identity matrix
        final_model = pyrr.matrix44.create_identity(np.float32)
        self.shader.set_matrix("model", final_model)  # False parameter is a guess

        self.shader.set_vector("spriteColor", polygon.color)  # False parameter is a guess

        glBindVertexArray(self.quadVAO)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.IBO)
        glDrawElements(GL_LINES, len(index_list), GL_UNSIGNED_INT, None)
        glBindVertexArray(0)

    def init_render_data(self):
        self.quadVAO = glGenVertexArrays(1)
        self.VBO = glGenBuffers(1)
        self.IBO = glGenBuffers(1)

        glBindBuffer(GL_ARRAY_BUFFER, self.VBO)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.IBO)

        glBindVertexArray(self.quadVAO)
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 2 * sizeof(GLfloat), None)
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)
