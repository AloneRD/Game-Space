import curses
import asyncio
import time
import logging
import random
import glob

from itertools import cycle
from physics import update_speed
from explosion import explode
from curses_tools import draw_frame, read_controls, get_frame_size
from obstacles import Obstacle
from game_scenario import get_garbage_delay_tics, PHRASES

TIC_TIMEOUT = 0.1
OBSTACLES = []
OBSTACLES_IN_FIRE = []
YEAR = 1956


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


async def fire(canvas, start_row, start_column, rows_speed=-0.9, columns_speed=0):
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
        for obstacle in OBSTACLES:
            if obstacle.has_collision(row, column):
                OBSTACLES_IN_FIRE.append(obstacle)
                return

        canvas.addstr(round(row), round(column), symbol)
        await asyncio.sleep(0)
        canvas.addstr(round(row), round(column), ' ')
        row += rows_speed
        column += columns_speed


async def animate_spaceship(canvas, animation_spaceship, frame_game_over, height, width, row, column):
    row_speed = column_speed = 0
    for frame in cycle(animation_spaceship):
        frame_height, frame_width = get_frame_size(frame)

        rows_direction, columns_direction, space_pressed = read_controls(canvas)

        row_speed, column_speed = update_speed(
            row_speed,
            column_speed,
            rows_direction,
            columns_direction,
        )
        row_number = min(
            row + row_speed,
            height - frame_height - 1,
        )
        column_number = min(
            column + column_speed,
            width - frame_width - 1,
        )

        row = max(row_number, 1)
        column = max(column_number, 1)

        draw_frame(canvas, row, column, frame)
        await sleep(0.1)
        draw_frame(canvas, row, column, frame, negative=True)

        if space_pressed and YEAR >= 2020:
            coroutines.append(fire(canvas, row, column+2))
        for obstacle in OBSTACLES:
            if obstacle.has_collision(row, column):
                await show_gameover(canvas, frame_game_over)


async def count_years():
    global YEAR
    while True:
        YEAR += 1

        await sleep(1.5)


async def draw_year(canvas, row, colum):
    while True:
        try:
            draw_frame(canvas, row, colum, f'{YEAR} - {PHRASES[YEAR]}')
        except KeyError:
            draw_frame(canvas, row, colum, f'{YEAR}'+('#'*100), negative=True)
            draw_frame(canvas, row, colum, f'{YEAR}')
        await asyncio.sleep(0)


async def fly_garbage(canvas, column, garbage_frame, speed=0.5):
    global OBSTACLES, YEAR
    """Animate garbage, flying from top to bottom. Сolumn position will stay same, as specified on start."""
    rows_number, columns_number = canvas.getmaxyx()

    rows_size, colums_size = get_frame_size(garbage_frame)
    column = max(column, 0)
    column = min(column, columns_number - 1)
    row = 0
    obstacle = Obstacle(row, column, rows_size, colums_size)
    OBSTACLES.append(obstacle)
    while row < rows_number:
        draw_frame(canvas, row, column, garbage_frame)
        await asyncio.sleep(0)
        draw_frame(canvas, row, column, garbage_frame, negative=True)
        row += speed
        obstacle.row += speed

        if obstacle in OBSTACLES_IN_FIRE:
            OBSTACLES.remove(obstacle)
            await explode(canvas, row+3, column+3)
            OBSTACLES_IN_FIRE.remove(obstacle)
            return
    OBSTACLES.remove(obstacle)


async def fill_orbit_with_garbage(canvas, width, frames_gabages):
    while True:
        column = random.randint(0, width)
        speed = random.uniform(0, 1)

        await asyncio.sleep(0)
        garbage_delay_tics = get_garbage_delay_tics(YEAR)
        if not garbage_delay_tics:
            continue
        coroutines.append(
            fly_garbage(
                canvas,
                column=column,
                garbage_frame=random.choice(frames_gabages),
                speed=speed
            )
        )
        await sleep(garbage_delay_tics)


async def show_gameover(canvas, game_over_frame):
    height, width = canvas.getmaxyx()
    while True:
        draw_frame(canvas, height//4, width//4, game_over_frame)
        await asyncio.sleep(0)


def draw(canvas):
    global coroutines
    curses.curs_set(False)
    canvas.nodelay(True)

    height, width = canvas.getmaxyx()

    frames_animations_spaceship = glob.glob('animations//rocket_frame_*.txt')
    frames_gabages = get_garbage_frames()

    with open('animations//game_over.txt', 'r') as frame:
        frame_game_over = frame.read()

    animation_spaceship = []
    for frame_animation in frames_animations_spaceship:
        with open(frame_animation, 'r') as frame:
            rocket_frame = frame.read()
            animation_spaceship.extend([rocket_frame, rocket_frame])

    coroutines = [blink(canvas, x, y, symbol,  random.randint(0, 3))
                  for x, y, symbol in generate_stars(height, width)]

    coroutines.append(
        animate_spaceship(
            canvas,
            animation_spaceship,
            frame_game_over,
            height,
            width,
            row=height/2,
            column=width/2-2
            )
        )
    coroutines.append(fill_orbit_with_garbage(canvas, width, frames_gabages))
    coroutines.append(count_years())
    coroutines.append(draw_year(canvas, 2, 2))

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


def get_garbage_frames() -> list:
    garbages_frames = []
    garbages_frames_paths = glob.glob('animations//gabage_*.txt')
    for garbage_frame_path in garbages_frames_paths:
        with open(garbage_frame_path) as garbage_frame_file:
            garbage_frame = garbage_frame_file.read()
            garbages_frames.append(garbage_frame)

    return garbages_frames


if __name__ == '__main__':
    obstacles = []
    logging.basicConfig(filename="sample.log", level=logging.INFO)
    try:
        curses.update_lines_cols()
        curses.wrapper(draw)
    except Exception as e:
        logging.info(e)
