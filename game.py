import curses
import time

def draw(canvas):
    row, colum = (5, 20)
    canvas.addstr(row,colum,"Hello world!")
    canvas.refresh()
    time.sleep(1)


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
