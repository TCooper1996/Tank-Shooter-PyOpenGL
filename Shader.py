from OpenGL.GL import *


class Shader:
    def __init__(self):
        self.ID = -1

    def use(self):
        glUseProgram(self.ID)
        return self

    def compile(self, vertex_source, fragment_source):
        # Compile Vertex Shader
        s_vertex = glCreateShader(GL_VERTEX_SHADER)
        glShaderSource(s_vertex, vertex_source)
        glCompileShader(s_vertex, "VERTEX")
        # Compile Fragment Shader
        s_fragment = glCreateShader(GL_FRAGMENT_SHADER)
        glShaderSource(s_fragment, fragment_source)
        glCompileShader(s_fragment, "FRAGMENT")
        # Shader program
        self.ID = glCreateProgram()
        glAttachShader(self.ID, s_vertex)
        glAttachShader(self.ID, s_fragment)
        glLinkProgram(self.ID)
        self.check_compile_errors(self.ID, "PROGRAM")
        glDeleteShader(s_vertex)
        glDeleteShader(s_fragment)

    def set_vector(self, s_name, value):
        glUniform3f(glGetUniformLocation(self.ID, s_name), value[0], value[1], value[2])

    def set_matrix(self, s_name, matrix):
        glUniformMatrix4fv(glGetUniformLocation(self.ID, s_name), 1, GL_FALSE, matrix)

    def set_integer(self, s_name, value):
        glUniform1i(glGetUniformLocation(self.ID, s_name), value)

    @staticmethod
    def check_compile_errors(shader, shader_type):
        info_log = ""
        if shader_type != "PROGRAM":
            success = glGetShaderiv(shader, GL_COMPILE_STATUS, None)
            if not success:
                glGetShaderInfoLog(shader, 1024, None, info_log)
                print("ERROR: Compile-time error:\n\tType: {0}\n\t{1}".format(shader_type, info_log))

        else:
            success = glGetProgramiv(shader, GL_LINK_STATUS, None)
            if not success:
                glGetProgramInfoLog(shader, 1024, None, info_log)
                print("ERROR: Link-time error:\n\tType: {0}\n\t{1}".format(shader_type, info_log))
