from OpenGL.GL import *
import Shader


class ResourceManager:
    Shaders = {}
    @staticmethod
    def load_shader(v_shader_file, f_shader_file, s_name):
        ResourceManager.Shaders[s_name] = ResourceManager.load_shader_from_file(v_shader_file, f_shader_file)
        return ResourceManager.Shaders[s_name]

    @staticmethod
    def get_shader(s_name):
        return ResourceManager.Shaders[s_name]

    @staticmethod
    def clear():
        for s in ResourceManager.Shaders:
            glDeleteProgram(s.second.ID)

    @staticmethod
    def load_shader_from_file(v_shader_file, f_shader_file):
        try:
            with open(v_shader_file, 'r')as file:
                vertex_code = file.read()
            with open(f_shader_file, 'r')as file:
                fragment_code = file.read()
        except FileNotFoundError:
            print("ERROR: Failed to read vertex/fragment shader")

        shader = Shader.Shader()
        shader.compile(vertex_code, fragment_code)
        return shader
