class Widget:
    def __init__(self, pos, dimensions):
        self.pos = pos
        self.dimensions = dimensions
        self.is_hover = False


class Button(Widget):
    def __init__(self, pos, dimensions, command):
        super(Button, self).__init__(pos, dimensions)
        self.command = command

    def on_click(self):
        self.command()

    def draw(self, renderer):
        renderer.draw_widget(self)