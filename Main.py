from OpenGL.GL import *
from cyglfw3 import *
from Game import Game
import GameConstants


def key_callback(window, key, _scancode, action, _mods):
    if key == KEY_ESCAPE and action == PRESS:
        SetWindowShouldClose(window, GL_TRUE)

    if 0 <= key < 1024:
        if action == PRESS:
            game.Keys[key] = GL_TRUE
        elif action == RELEASE:
            game.Keys[key] = GL_FALSE


def mouse_button_callback(_window, button, action, _mods):
    if button == MOUSE_BUTTON_LEFT:
        if action == PRESS:
            game.mouse_buttons[button] = GL_TRUE
        elif action == RELEASE:
            game.mouse_buttons[button] = GL_FALSE


SCREEN_WIDTH = GameConstants.SCREEN_WIDTH
SCREEN_HEIGHT = GameConstants.SCREEN_HEIGHT

game = Game(SCREEN_WIDTH, SCREEN_HEIGHT)


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

    last_frame = float(0.0)

    clear_color = [float(1) for _ in range(4)]

    game.load_resources()

    while not WindowShouldClose(window):
        current_frame = GetTime()
        delta_time = current_frame - last_frame
        last_frame = current_frame
        PollEvents()

        # Process input
        game.process_input(delta_time)
        # Update state
        game.update(delta_time, GetCursorPos(window))

        # Clear screen
        glClearColor(*clear_color)
        glClear(GL_COLOR_BUFFER_BIT)
        # Draw to screen
        game.render()

        SwapBuffers(window)

    Terminate()


main()
