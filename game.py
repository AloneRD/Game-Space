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


def draw(canvas):
    curses.curs_set(False)
    canvas.nodelay(True)

    height, width = canvas.getmaxyx()
    coroutines = [blink(canvas, x, y, symbol) for x, y, symbol in generate_stars(height, width)]
    while True:
        for coroutine in coroutines:
            canvas.refresh()
            coroutine.send(None)
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
