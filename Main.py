import sys

from OpenGL.GL import *
from cyglfw3 import *

import GameConstants
from Editor import Editor
from Game import Game


def key_callback(window, key, _scancode, action, _mods):
    if key == KEY_ESCAPE and action == PRESS:
        SetWindowShouldClose(window, GL_TRUE)

    if 0 <= key < 1024:
        if action == PRESS:
            app.Keys[key] = GL_TRUE
        elif action == RELEASE:
            app.Keys[key] = GL_FALSE


def mouse_button_callback(_window, button, action, _mods):
    if action == PRESS:
        app.mouse_buttons[button] = GL_TRUE
    elif action == RELEASE:
        app.mouse_buttons[button] = GL_FALSE


SCREEN_WIDTH = GameConstants.SCREEN_WIDTH
SCREEN_HEIGHT = GameConstants.SCREEN_HEIGHT
if len(sys.argv) > 1 and sys.argv[1] == "true":
    app = Editor(SCREEN_WIDTH, SCREEN_HEIGHT)
else:
    app = Game(SCREEN_WIDTH, SCREEN_HEIGHT)


def main():
    Init()
    WindowHint(CONTEXT_VERSION_MAJOR, 3)
    WindowHint(CONTEXT_VERSION_MINOR, 3)
    WindowHint(OPENGL_PROFILE, OPENGL_CORE_PROFILE)
    WindowHint(RESIZABLE, GL_FALSE)
    WindowHint(SAMPLES, 4)

    window = CreateWindow(SCREEN_WIDTH, SCREEN_HEIGHT, "Tank Shooter", None, None)
    glViewport(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
    MakeContextCurrent(window)
    SwapInterval(1)

    SetKeyCallback(window, key_callback)
    SetMouseButtonCallback(window, mouse_button_callback)

    glLineWidth(2)
    glEnable(GL_MULTISAMPLE)

    app.load_resources()

    while app.active and not WindowShouldClose(window):
        PollEvents()

        # Process input
        app.process_input()
        # Update state
        app.update(GetCursorPos(window))

        # Clear screen
        glClearColor(1.0, 1.0, 1.0, 1.0)
        glClear(GL_COLOR_BUFFER_BIT)
        # Draw to screen
        app.render()

        SwapBuffers(window)

    Terminate()


main()
