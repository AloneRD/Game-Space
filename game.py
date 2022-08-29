import curses
import asyncio
import time
import logging
import random
import os
import glob

from itertools import cycle

from curses_tools import draw_frame, read_controls, get_frame_size

TIC_TIMEOUT = 0.1


async def sleep(seconds):
    for _ in range(int(seconds * 10)):
        await asyncio.sleep(0)


async def blink(canvas, row, column, symbol, flash_offset):
    while True:
        if flash_offset == 0:
            canvas.addstr(row, column, symbol, curses.A_DIM)
            await sleep(2)
            flash_offset += 1
        if flash_offset == 1:
            canvas.addstr(row, column, symbol)
            await sleep(0.3)
            flash_offset += 1
        if flash_offset == 2:
            canvas.addstr(row, column, symbol, curses.A_BOLD)
            await sleep(0.5)
            flash_offset += 1
        if flash_offset == 3:
            canvas.addstr(row, column, symbol)
            await sleep(0.3)
            flash_offset == 0


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


async def animate_spaceship(canvas, animation_spaceship, height, width, row, column):
    for frame in cycle(animation_spaceship):
        row_frame, column_frame = get_frame_size(frame)
        rows_direction, columns_direction, space_pressed = read_controls(canvas)

        if rows_direction == -1 and height-row < height:
            row += rows_direction
        if rows_direction == 1 and row+row_frame < height:
            row += rows_direction
        if columns_direction == -1 and width - column < width:
            column += columns_direction
        if columns_direction == 1 and column_frame + column < width:
            column += columns_direction

        draw_frame(canvas, row, column, frame)
        await sleep(0.1)
        draw_frame(canvas, row, column, frame, negative=True)


async def fly_garbage(canvas, column, garbage_frame, speed=0.5):
    """Animate garbage, flying from top to bottom. Сolumn position will stay same, as specified on start."""
    rows_number, columns_number = canvas.getmaxyx()

    column = max(column, 0)
    column = min(column, columns_number - 1)

    row = 0

    while row < rows_number:
        draw_frame(canvas, row, column, garbage_frame)
        await asyncio.sleep(0)
        draw_frame(canvas, row, column, garbage_frame, negative=True)
        row += speed


def draw(canvas):
    curses.curs_set(False)
    canvas.nodelay(True)

    height, width = canvas.getmaxyx()

    frames_animations_spaceship = glob.glob('animations//rocket_frame_*.txt')
    frames_animations_garbage = glob.glob('animations//gabage_*.txt')
    generate_garbage(frames_animations_garbage)
    animation_spaceship = []
    for frame_animation in frames_animations_spaceship:
        with open(frame_animation, 'r') as frame:
            rocket_frame = frame.read()
            animation_spaceship.extend([rocket_frame, rocket_frame])

    coroutines = [blink(canvas, x, y, symbol,  random.randint(0, 3))
                  for x, y, symbol in generate_stars(height, width)]
    coroutines.append(fire(canvas, height/2, width/2))
    coroutines.append(
        fly_garbage(
            canvas,
            column=10,
            garbage_frame=generate_garbage(frames_animations_garbage)
        )
    )
    coroutines.append(
        animate_spaceship(
            canvas,
            animation_spaceship,
            height,
            width,
            row=height/2,
            column=width/2-2
            )
        )

    while True:
        for coroutine in coroutines.copy():
            try:
                coroutine.send(None)
            except StopIteration:
                coroutines.remove(coroutine)
        canvas.refresh()
        time.sleep(TIC_TIMEOUT)


def generate_stars(height: int, width: int, count_stars=100):
    for star in range(count_stars):
        x_cordinates = random.randint(0, height-1)
        y_cordinates = random.randint(0, width-1)
        symbol = random.choice("+*.:")
        yield x_cordinates, y_cordinates, symbol


def generate_garbage(frames: list) -> str:
    with open(random.choice(frames)) as frame:
        gabage_frame = frame.read()
        return gabage_frame

if __name__ == '__main__':
    logging.basicConfig(filename="sample.log", level=logging.INFO)

    curses.update_lines_cols()
    curses.wrapper(draw)
