import curses
import asyncio
import time
import logging
import random

logging.basicConfig(filename="sample.log", level=logging.INFO)

TIC_TIMEOUT = 0.1


async def blink(canvas, row, column, symbol='*'):
    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        for _ in range(random.randint(0, 20)):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        for _ in range(random.randint(0, 3)):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        for _ in range(random.randint(0, 5)):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        for _ in range(random.randint(0, 3)):
            await asyncio.sleep(0)


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


def draw(canvas):
    curses.curs_set(False)
    canvas.nodelay(True)

    height, width = canvas.getmaxyx()
    coroutines = [blink(canvas, x, y, symbol) for x, y, symbol in generate_stars(height, width)]
    coroutines.append(fire(canvas, height/2, width/2))
    for coroutine in coroutines.copy():
        while True:
            for coroutine in coroutines:
                canvas.refresh()
                try:
                    coroutine.send(None)
                except StopIteration:
                    coroutines.remove(coroutine)
            time.sleep(TIC_TIMEOUT)
            if len(coroutines) == 0:
                break


def generate_stars(height: int, width: int, count_stars=100):
    for star in range(count_stars):
        x_cordinates = random.randint(0, height-1)
        y_cordinates = random.randint(0, width-1)
        symbol = random.choice(["+", "*", ".", ":"])
        yield x_cordinates, y_cordinates, symbol


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
