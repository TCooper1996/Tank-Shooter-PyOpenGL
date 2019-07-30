import pyrr
from OpenGL.GL import *

from Entity import Combatant
from GameConstants import *
from Polygon import Polygon, EntityType


class Renderer:
    def __init__(self, shader):
        self.shader = shader
        self.quadVAO = -1
        self.VBO = -1
        self.IBO = -1
        self.cannonIBO = -1
        self.quadIBO = -1
        self.init_render_data()
        self.mouse_position = (None, None)

    def draw_editor_controls(self):
        glBindVertexArray(self.quadVAO)
        glBindBuffer(GL_ARRAY_BUFFER, self.VBO)
        # The contents of the list below represent the box that holds the controls
        vertex_float_list = [0, 0, 0, SCREEN_MARGIN, SCREEN_MARGIN, SCREEN_MARGIN, SCREEN_MARGIN, 0]

        glBufferData(GL_ARRAY_BUFFER, np.array(vertex_float_list, dtype=np.float32), GL_DYNAMIC_DRAW)

        glDrawArrays(GL_LINE_LOOP, 0, len(vertex_float_list))

    def draw_grid(self):
        glBindVertexArray(self.quadVAO)
        vertex_float_list = []
        for x in range(SCREEN_WIDTH//50):
            vertex_float_list += [x*50, 0, x*50, SCREEN_HEIGHT]
        for y in range(SCREEN_HEIGHT//50):
            vertex_float_list += [0, y*50, SCREEN_WIDTH, y*50]
        glBindBuffer(GL_ARRAY_BUFFER, self.VBO)
        array = np.array(vertex_float_list, dtype=np.float32)
        glBufferData(GL_ARRAY_BUFFER, array, GL_DYNAMIC_DRAW)

        self.shader.set_vector("spriteColor", (0.8, 0.8, 0.8))
        glDrawArrays(GL_LINES, 0, len(vertex_float_list))

    def draw_widget(self, widget):
        x, y = widget.pos
        w, h = widget.dimensions
        vertex_float_list = [x, y, x, y + h, x + w, y + h, x + w, y]
        glBindVertexArray(self.quadVAO)
        glBindBuffer(GL_ARRAY_BUFFER, self.VBO)
        glBufferData(GL_ARRAY_BUFFER, np.array(vertex_float_list, dtype=np.float32), GL_DYNAMIC_DRAW)

        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.quadIBO)

        glDrawElements(GL_LINES, 8, GL_UNSIGNED_INT, None)

    def draw_map(self, map_dict, current_level: (int, int), is_mini=False):
        # Prepend the list of levels with the tuple of the current level.
        # The first draw call draws the blue background behind every room, but we want the current room to instead
        # be drawn a distinctive color. To avoid creating a new vertex_array or iterating over the list of tuples
        # to find the vertices of our current room, we simply prepend it to our outline_float_array, that way we always
        # know it is a index 0. After we draw the background, we can repeat the same draw call, using the same
        # vertex and index buffer, but limiting the indices to be drawn to 6, that way only the first 6 vertices
        # (which represent the current room) are drawn with the red color.
        levels = [current_level] + list(map_dict.keys())
        # Outline float array describes the vertices that make up the black outline of thee minimap
        outline_float_array = []
        # background float array describes the vertices that color the backgrounds using triangles
        background_float_array = []
        background_index_array = []
        tile_width = MINI_TILE if is_mini else TILE_WIDTH
        tile_height = MINI_TILE if is_mini else TILE_HEIGHT
        x_offset = SCREEN_WIDTH * 0.925 if is_mini else SCREEN_WIDTH / 2
        y_offset = SCREEN_HEIGHT * 0.88 if is_mini else SCREEN_HEIGHT / 2
        for level in levels:
            room = map_dict[level]
            x = level[0] * tile_width + x_offset
            y = level[1] * tile_height + y_offset
            w = tile_width
            h = tile_height
            background_float_array += [x, y, x, y + h, x + w, y + h, x + w, y]
            # If a room is connected to the right, top, left, bottom of the current room, don't draw an edge.
            # If not, draw an edge.
            if not room.get_exit(0):
                outline_float_array += [x + w, y, x + w, y + h]
            if not room.get_exit(1):
                outline_float_array += [x, y + h, x + w, y + h]
            if not room.get_exit(2):
                outline_float_array += [x, y + h, x, y]
            if not room.get_exit(3):
                outline_float_array += [x, y, x + w, y]
            #if level == current_level:
            #    outline_float_array += [x, y, x + w, y + h, x, y + h, x + w, y]
        glBindVertexArray(self.quadVAO)
        glBindBuffer(GL_ARRAY_BUFFER, self.VBO)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.IBO)
        # Create the vertex array for the background
        for i in range(len(levels)):
            background_index_array += [i*4, i*4 + 1, i*4 + 2, i*4 + 2, i*4 + 3, i*4]
        self.shader.set_vector("spriteColor", (0.7, 0.7, 0.8))
        glBufferData(GL_ARRAY_BUFFER, np.array(background_float_array, dtype=np.float32), GL_DYNAMIC_DRAW)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, np.array(background_index_array, dtype=np.uint32), GL_DYNAMIC_DRAW)
        glDrawElements(GL_TRIANGLES, len(background_index_array), GL_UNSIGNED_INT, None)
        self.shader.set_vector("spriteColor", (0.9, 0.4, 0.4))

        glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_INT, None)

        # Draw outline
        self.shader.set_vector("spriteColor", (0.0, 0.0, 0.0))
        glBufferData(GL_ARRAY_BUFFER, np.array(outline_float_array, dtype=np.float32), GL_DYNAMIC_DRAW)
        glDrawArrays(GL_LINES, 0, len(outline_float_array))


    def draw_cannon(self, pos, cannon_angle):
        cannon_float_array = np.array([
            pos[0], pos[1],  # Center
            pos[0] + np.cos(cannon_angle) * 35,  # Cannon endpoint x
            pos[1] + np.sin(cannon_angle) * 35  # Cannon endpoint y
        ], dtype=np.float32)

        glBindVertexArray(self.quadVAO)
        # Configure cannon VBO
        glBindBuffer(GL_ARRAY_BUFFER, self.VBO)
        glBufferData(GL_ARRAY_BUFFER, cannon_float_array, GL_DYNAMIC_DRAW)

        # Configure cannon IBO
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.cannonIBO)

        glDrawElements(GL_LINES, 2, GL_UNSIGNED_INT, None)

    def draw_polygon(self, polygon: Polygon):
        vertex_float_array = polygon.get_render_vertices()
        direction_line = np.array([polygon.pos[0], polygon.pos[1], polygon.pos[0] + np.cos(polygon.rotation)*25,
                          polygon.pos[1] + np.sin(polygon.rotation) * 25], dtype=np.float32)

        glBindVertexArray(self.quadVAO)
        # Configure VBO
        glBindBuffer(GL_ARRAY_BUFFER, self.VBO)
        glBufferData(GL_ARRAY_BUFFER, vertex_float_array, GL_DYNAMIC_DRAW)

        self.shader.set_vector("spriteColor", polygon.color)

        glDrawArrays(GL_LINE_LOOP, 0, len(vertex_float_array)//2)
        if polygon.entity_type == EntityType.Tank:
            glBufferData(GL_ARRAY_BUFFER, direction_line, GL_DYNAMIC_DRAW)
            glDrawArrays(GL_LINES, 0, 2)



        # Draw health bar for combatants
        if isinstance(polygon, Combatant):
            # The hardcoded values below are meant to be relative to the object being draw.
            vertex_float_array = HEALTH_BAR_COORDINATES.copy()
            # Proportionally scale length of health bar by health
            vertex_float_array[4] *= polygon.health / polygon.max_health
            vertex_float_array[6] *= polygon.health / polygon.max_health
            # Increase all x values by objects x, and also subtract 30, so that the centers match up
            for i in range(0, 8, 2):
                vertex_float_array[i] += polygon.pos[0] - 30
            # Same for y values, but without the -30
            for j in range(1, 8, 2):
                vertex_float_array[j] += polygon.pos[1]
            vertex_float_array = np.array(vertex_float_array, dtype=np.float32)

            glBufferData(GL_ARRAY_BUFFER, vertex_float_array, GL_DYNAMIC_DRAW)
            glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.quadIBO)
            glDrawElements(GL_LINES, 8, GL_UNSIGNED_INT, None)

    def init_render_data(self):
        self.quadVAO = glGenVertexArrays(1)
        self.VBO = glGenBuffers(1)
        self.IBO = glGenBuffers(1)
        self.quadIBO = glGenBuffers(1)
        self.cannonIBO = glGenBuffers(1)

        glBindVertexArray(self.quadVAO)
        glBindBuffer(GL_ARRAY_BUFFER, self.VBO)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.cannonIBO)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, np.array([0, 1], dtype=np.uint32), GL_STATIC_DRAW)

        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.quadIBO)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, np.array([0, 1, 1, 2, 2, 3, 3, 0], dtype=np.uint32), GL_STATIC_DRAW)

        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 2 * sizeof(GLfloat), None)

        # Transformation is unused; identity matrix
        final_model = pyrr.matrix44.create_identity(np.float32)
        self.shader.set_matrix("model", final_model)

        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)
