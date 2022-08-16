from asyncio.log import logger
import curses
import asyncio
import time
import logging
import random

from itertools import cycle

from curses_tools import draw_frame

logging.basicConfig(filename="sample.log", level=logging.INFO)

TIC_TIMEOUT = 0.1


async def count_delay(seconds):
    for _ in range(int(seconds * 10)):
        await asyncio.sleep(0)


async def blink(canvas, row, column, symbol='*'):
    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        await count_delay(2)

        canvas.addstr(row, column, symbol)
        await count_delay(0.3)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        await count_delay(0.5)

        canvas.addstr(row, column, symbol)
        await count_delay(0.3)


async def fire(canvas, start_row, start_column, rows_speed=-0.6, columns_speed=0):
    """Display animation of gun shot, direction and speed can be specified."""

    row, column = start_row, start_column

    canvas.addstr(round(row), round(column), '*')
    await asyncio.sleep(0)

    canvas.addstr(round(row), round(column), 'O')
    await asyncio.sleep(0)
    canvas.addstr(round(row), round(column), ' ')

    row += rows_speed
    column += columns_speed

    symbol = '-' if columns_speed else '|'

    rows, columns = canvas.getmaxyx()
    max_row, max_column = rows - 1, columns - 1

    curses.beep()

    while 0 < row < max_row and 0 < column < max_column:
        canvas.addstr(round(row), round(column), symbol)
        await asyncio.sleep(0)
        canvas.addstr(round(row), round(column), ' ')
        row += rows_speed
        column += columns_speed


async def animate_spaceship(canvas, start_row, start_column, animation_spaceship):
    for frame in cycle(animation_spaceship):
        draw_frame(canvas, start_row, start_column, frame)
        await count_delay(0.3)
        draw_frame(canvas, start_row, start_column, frame, negative=True)


def draw(canvas):
    curses.curs_set(False)
    canvas.nodelay(True)

    height, width = canvas.getmaxyx()

    with open('animations\\rocket_frame_1.txt', 'r') as frame_1, open('animations\\rocket_frame_2.txt', 'r') as frame_2:
        animation_spaceship = [frame_1.read(), frame_2.read()]

    coroutines = [blink(canvas, x, y, symbol) for x, y, symbol in generate_stars(height, width)]
    coroutines.append(fire(canvas, height/2, width/2))
    coroutines.append(animate_spaceship(canvas, height/2, width/2-2, animation_spaceship))

    while True:
        for coroutine in coroutines.copy():
            try:
                coroutine.send(None)
                canvas.refresh()
            except StopIteration:
                coroutines.remove(coroutine)
        time.sleep(TIC_TIMEOUT)


def generate_stars(height: int, width: int, count_stars=100):
    for star in range(count_stars):
        x_cordinates = random.randint(0, height-1)
        y_cordinates = random.randint(0, width-1)
        symbol = random.choice(["+", "*", ".", ":"])
        yield x_cordinates, y_cordinates, symbol


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
