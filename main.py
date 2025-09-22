from kivy.config import Config

# Force ANGLE backend (DirectX) for better Windows compatibility without advanced OpenGL
Config.set('graphics', 'angle', 'true')
Config.set('graphics', 'multisamples', '0')
Config.set('graphics', 'window', 'sdl2')

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.properties import ListProperty, NumericProperty
from kivy.core.window import Window
from random import randint

# Set window size
Window.size = (400, 400)

class SnakeGame(Widget):
    snake = ListProperty([])
    snake_dir = ListProperty([20, 0])  # Start moving right, grid size 20x20
    food_pos = ListProperty([0, 0])
    step_size = NumericProperty(20)
    score = NumericProperty(0)
    game_over = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.reset_game()
        # Schedule game update every 0.15 seconds
        Clock.schedule_interval(self.update, 0.15)
        # Listen for keyboard events
        Window.bind(on_key_down=self.on_key_down)

    def reset_game(self):
        self.snake = [[100, 100], [80, 100], [60, 100]]  # initial snake segments
        self.snake_dir = [20, 0]
        self.spawn_food()
        self.score = 0
        self.game_over = False

    def spawn_food(self):
        max_x = (Window.width // self.step_size) - 1
        max_y = (Window.height // self.step_size) - 1
        while True:
            x = randint(0, max_x) * self.step_size
            y = randint(0, max_y) * self.step_size
            if [x, y] not in self.snake:
                self.food_pos = [x, y]
                break

    def on_key_down(self, window, key, scancode, codepoint, modifier):
        # Prevent reversing direction
        if key == 273:  # up arrow
            if self.snake_dir != [0, -self.step_size]:
                self.snake_dir = [0, self.step_size]
        elif key == 274:  # down arrow
            if self.snake_dir != [0, self.step_size]:
                self.snake_dir = [0, -self.step_size]
        elif key == 276:  # left arrow
            if self.snake_dir != [self.step_size, 0]:
                self.snake_dir = [-self.step_size, 0]
        elif key == 275:  # right arrow
            if self.snake_dir != [-self.step_size, 0]:
                self.snake_dir = [self.step_size, 0]

    def update(self, dt):
        if self.game_over:
            return

        # Calculate new head position
        new_head = [self.snake[0][0] + self.snake_dir[0], self.snake[0][1] + self.snake_dir[1]]

        # Check for wall collisions
        if (new_head[0] < 0 or new_head[0] >= Window.width or
            new_head[1] < 0 or new_head[1] >= Window.height):
            self.end_game()
            return

        # Check for self collisions
        if new_head in self.snake:
            self.end_game()
            return

        # Move snake forward
        self.snake = [new_head] + self.snake[:-1]

        # Check if food eaten
        if new_head == self.food_pos:
            self.snake.append(self.snake[-1])  # grow snake by repeating tail
            self.spawn_food()
            self.score += 1

        self.canvas.clear()
        self.draw_game()

    def draw_game(self):
        from kivy.graphics import Color, Rectangle

        with self.canvas:
            # Draw background
            Color(0, 0, 0, 1)
            Rectangle(pos=(0, 0), size=Window.size)

            # Draw snake
            Color(0, 1, 0, 1)
            for segment in self.snake:
                Rectangle(pos=segment, size=(self.step_size, self.step_size))

            # Draw food
            Color(1, 0, 0, 1)
            Rectangle(pos=self.food_pos, size=(self.step_size, self.step_size))

            # Draw score text
            Color(1, 1, 1, 1)
            from kivy.core.text import Label as CoreLabel
            label = CoreLabel(text=f"Score: {self.score}", font_size=20)
            label.refresh()
            texture = label.texture
            Rectangle(texture=texture, pos=(10, Window.height - 30), size=texture.size)

    def end_game(self):
        self.game_over = True
        self.canvas.clear()
        from kivy.graphics import Color, Rectangle
        with self.canvas:
            Color(0, 0, 0, 1)
            Rectangle(pos=(0, 0), size=Window.size)
            Color(1, 0, 0, 1)
            from kivy.core.text import Label as CoreLabel
            label = CoreLabel(text=f"Game Over! Score: {self.score}\nPress R to Restart", font_size=24)
            label.refresh()
            texture = label.texture
            Rectangle(texture=texture,
                      pos=(Window.width/2 - texture.size[0]/2, Window.height/2 - texture.size[1]/2),
                      size=texture.size)

        # Bind R key to restart
        Window.unbind(on_key_down=self.on_key_down)
        Window.bind(on_key_down=self.on_key_down_restart)

    def on_key_down_restart(self, window, key, scancode, codepoint, modifier):
        if key == ord('r') or key == ord('R'):
            Window.unbind(on_key_down=self.on_key_down_restart)
            Window.bind(on_key_down=self.on_key_down)
            self.reset_game()
            self.canvas.clear()
            self.draw_game()

class SnakeApp(App):
    def build(self):
        game = SnakeGame()
        game.draw_game()
        return game

if __name__ == '__main__':
    SnakeApp().run()
