import curses
import asyncio

TIC_TIMEOUT = 0.1


async def blink(canvas, row, column, symbol='*'):
    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        canvas.refresh()
        for i in range(20):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        for i in range(3):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        for i in range(5):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        for i in range(3):
            await asyncio.sleep(0)


def draw(canvas):
    canvas.border()
    curses.curs_set(False)
    coroutines = []
    for i in range(5):
        coroutines.append(blink(canvas, 5, 20+(i*2)))
    while True:
        for coroutine in coroutines:
            coroutine.send(None)
            canvas.refresh()


    #  while True:
    #     canvas.addstr(row,colum,"*",curses.A_DIM)
    #     time.sleep(2)
    #     canvas.refresh()
    #     canvas.addstr(row,colum,"*")
    #     time.sleep(0.3)
    #     canvas.refresh()
    #     canvas.addstr(row,colum,"*",curses.A_BOLD)
    #     time.sleep(0.5)
    #     canvas.refresh()
    #     canvas.addstr(row,colum,"*")
    #     time.sleep(0.3)
    #     canvas.refresh()


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
