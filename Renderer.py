import pyrr
from OpenGL.GL import *

from Entity import Entity, Combatant
from GameConstants import *


class Renderer:
    def __init__(self, shader):
        self.shapeBuffers = []
        self.shader = shader
        self.quadVAO = -1
        self.VBO = -1
        self.IBO = -1
        self.cannonIBO = -1
        self.init_render_data()
        self.mouse_position = (-1, -1)

    def draw_cannon(self, pos, cannon_angle):
        cannon_float_array = np.array([
            pos[0], pos[1],  # Center
            pos[0] + np.cos(cannon_angle) * 35,  # Cannon endpoint x
            pos[1] + np.sin(cannon_angle) * 35  # Cannon endpoint y
        ], dtype=np.float32)

        # Configure cannon VBO
        glBindBuffer(GL_ARRAY_BUFFER, self.VBO)
        glBufferData(GL_ARRAY_BUFFER, cannon_float_array, GL_DYNAMIC_DRAW)

        # Configure cannon IBO
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.cannonIBO)

        glBindVertexArray(self.quadVAO)
        glDrawElements(GL_LINES, 2, GL_UNSIGNED_INT, None)

    def draw_polygon(self, polygon: Entity):
        vertex_float_array = polygon.get_vertices()
        index_array = polygon.get_indices()

        # Configure VBO
        glBindBuffer(GL_ARRAY_BUFFER, self.VBO)
        glBufferData(GL_ARRAY_BUFFER, vertex_float_array, GL_DYNAMIC_DRAW)

        # Configure IBO
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.IBO)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, index_array, GL_DYNAMIC_DRAW)

        self.shader.set_vector("spriteColor", polygon.color)

        glBindVertexArray(self.quadVAO)
        glDrawElements(GL_LINES, len(index_array), GL_UNSIGNED_INT, None)
        glBindVertexArray(0)

        # Draw health bar for combatants
        if isinstance(polygon, Combatant):
            # The hardcoded values below are meant to be relative to the object being draw.
            vertex_float_array = HEALTH_BAR_COORDINATES.copy()
            # Increase all x values by objects x
            for i in range(0, 8, 2):
                vertex_float_array[i] += polygon.pos[0]
            # Same for y values
            for i in range(1, 8, 2):
                vertex_float_array[i] += polygon.pos[1]
            vertex_float_array = np.array(vertex_float_array, dtype=np.float32)
            index_array = np.array([0, 1, 1, 2, 2, 3, 3, 0], dtype=np.uint32)

            glBufferData(GL_ARRAY_BUFFER, vertex_float_array, GL_DYNAMIC_DRAW)
            glBufferData(GL_ELEMENT_ARRAY_BUFFER, index_array, GL_DYNAMIC_DRAW)
            glBindVertexArray(self.quadVAO)
            glDrawElements(GL_LINES, len(index_array), GL_UNSIGNED_INT, None)

    def init_render_data(self):
        self.quadVAO = glGenVertexArrays(1)
        self.VBO = glGenBuffers(1)
        self.IBO = glGenBuffers(1)
        self.cannonIBO = glGenBuffers(1)

        glBindBuffer(GL_ARRAY_BUFFER, self.VBO)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.cannonIBO)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, np.array([0, 1]), GL_STATIC_DRAW)

        glBindVertexArray(self.quadVAO)
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 2 * sizeof(GLfloat), None)

        # Transformation is unused; identity matrix
        final_model = pyrr.matrix44.create_identity(np.float32)
        self.shader.set_matrix("model", final_model)  # False parameter is a guess

        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)
