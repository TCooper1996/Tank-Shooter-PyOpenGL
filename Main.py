from OpenGL.GL import *
from cyglfw3 import *
from Game import Game


def key_callback(window, key, _, action, _2):
    if key == KEY_ESCAPE and action == PRESS:
        SetWindowShouldClose(window, GL_TRUE)

    if 0 <= key < 1024:
        if action == PRESS:
            game.Keys[key] = GL_TRUE
        elif action == RELEASE:
            game.Keys[key] = GL_FALSE


SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600


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

    SetKeyCallback(window, key_callback)

    glLineWidth(2)
    glEnable(GL_MULTISAMPLE)

    last_frame = float(0.0)

    clear_color = [float(1) for _ in range(4)]

    game.Init()

    while not WindowShouldClose(window):
        current_frame = GetTime()
        delta_time = current_frame - last_frame
        last_frame = current_frame
        PollEvents()

        # Process input
        game.ProcessInput(delta_time)
        # Update state

        # Clear screen
        glClearColor(*clear_color)
        glClear(GL_COLOR_BUFFER_BIT)
        # Draw to screen
        game.render()

        SwapBuffers(window)

    Terminate()


main()
