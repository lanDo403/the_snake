"""Классическая игра «Змейка» на Pygame."""

import sys
from random import choice

import pygame as pg

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE
START_POSITION = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

TURNS = {
    pg.K_UP: (UP, DOWN),
    pg.K_DOWN: (DOWN, UP),
    pg.K_LEFT: (LEFT, RIGHT),
    pg.K_RIGHT: (RIGHT, LEFT),
}

# Цвет фона - черный:
BOARD_BACKGROUND_COLOR = (0, 0, 0)

# Цвет границы ячейки
BORDER_COLOR = (93, 216, 228)

# Цвет яблока
APPLE_COLOR = (255, 0, 0)

# Цвет змейки
SNAKE_COLOR = (0, 255, 0)

# Скорость движения змейки:
SPEED = 20

# Настройка игрового окна:
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pg.display.set_caption('Змейка')

# Настройка времени:
clock = pg.time.Clock()


class GameObject:
    """Базовый класс объектов игрового поля."""

    def __init__(self, position=START_POSITION, body_color=None):
        """Задать начальную позицию и цвет объекта."""
        self.position = position
        self.body_color = body_color

    def draw(self):
        """Определить отрисовку в дочернем классе."""
        raise NotImplementedError(
            f'Метод draw не переопределён в классе {type(self).__name__}'
        )

    def draw_cell(self, position, body_color, border_color=BORDER_COLOR):
        """Нарисовать клетку с заданными цветами заливки и границы."""
        rect = pg.Rect(position, (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, body_color, rect)
        pg.draw.rect(screen, border_color, rect, 1)


class Apple(GameObject):
    """Яблоко, которое увеличивает длину змейки."""

    def __init__(self, body_color=APPLE_COLOR, occupied_positions=()):
        """Создать яблоко заданного цвета в свободной клетке."""
        super().__init__(body_color=body_color)
        self.randomize_position(occupied_positions)

    def randomize_position(self, occupied_positions=()):
        """Выбрать свободную клетку или скрыть яблоко на полном поле."""
        free_positions = []
        for column in range(GRID_WIDTH):
            for row in range(GRID_HEIGHT):
                position = (column * GRID_SIZE, row * GRID_SIZE)
                if position not in occupied_positions:
                    free_positions.append(position)
        self.position = choice(free_positions) if free_positions else None

    def draw(self):
        """Нарисовать яблоко с границей клетки."""
        if self.position is not None:
            self.draw_cell(self.position, self.body_color)


class Snake(GameObject):
    """Змейка, которая движется по клеткам игрового поля."""

    def __init__(self, body_color=SNAKE_COLOR):
        """Создать змейку заданного цвета длиной в один сегмент."""
        super().__init__(body_color=body_color)
        self.reset()

    def update_direction(self):
        """Применить направление, выбранное стрелками."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def move(self, apple_position=None):
        """Передвинуть голову и сохранить хвост при съедании яблока."""
        x, y = self.get_head_position()
        dx, dy = self.direction
        new_x = (x + dx * GRID_SIZE) % SCREEN_WIDTH
        new_y = (y + dy * GRID_SIZE) % SCREEN_HEIGHT
        new_position = (new_x, new_y)
        if new_position == apple_position:
            self.length += 1
        self.positions.insert(0, new_position)
        self.last = None
        if len(self.positions) > self.length:
            self.last = self.positions.pop()

    def draw(self):
        """Стереть старый хвост и нарисовать новую голову змейки."""
        if self.last is not None:
            self.draw_cell(
                self.last, BOARD_BACKGROUND_COLOR, BOARD_BACKGROUND_COLOR
            )
        self.draw_cell(self.get_head_position(), self.body_color)

    def get_head_position(self):
        """Вернуть координаты головы змейки."""
        return self.positions[0]

    def reset(self):
        """Вернуть змейку в начальное состояние."""
        self.length = 1
        self.positions = [self.position]
        self.direction = RIGHT
        self.next_direction = None
        self.last = None


def handle_keys(game_object):
    """Обработать стрелки и закрытие игрового окна."""
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()
        elif event.type == pg.KEYDOWN and event.key in TURNS:
            new_direction, opposite = TURNS[event.key]
            if game_object.direction != opposite:
                game_object.next_direction = new_direction


def main():
    """Запустить игру и обновлять поле до закрытия окна."""
    pg.init()
    snake = Snake()
    apple = Apple(occupied_positions=snake.positions)
    screen.fill(BOARD_BACKGROUND_COLOR)

    while True:
        clock.tick(SPEED)
        handle_keys(snake)
        snake.update_direction()
        snake.move(apple.position)

        if snake.get_head_position() == apple.position:
            apple.randomize_position(snake.positions)

        elif snake.get_head_position() in snake.positions[4:]:
            snake.reset()
            screen.fill(BOARD_BACKGROUND_COLOR)
            if apple.position is None or apple.position in snake.positions:
                apple.randomize_position(snake.positions)

        snake.draw()
        apple.draw()
        pg.display.update()


if __name__ == '__main__':
    main()
