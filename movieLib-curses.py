#!/usr/bin/env python3

import curses as C
import time # import keyboard
import os
import ueberzug.lib.v0 as ueberzug

from enum import IntEnum
from enum import Enum


class Colors(IntEnum):
    DEFAULT = 1
    SELECTED = 2
    DOWNBAR = 3
    NORMAL = 4
    SEARCH = 5

class Modes(Enum):
    NORMAL = 1
    SEARCH = 2

class Sorts(Enum):
    ABC = 1
    SCORE = 2

def main():
    # new window
    win = C.initscr()
    rows, cols = win.getmaxyx()

    C.start_color()
    C.use_default_colors()

    # color pairs
    C.init_pair(Colors.DEFAULT, C.COLOR_BLUE, -1)
    C.init_pair(Colors.SELECTED, C.COLOR_BLACK, C.COLOR_BLUE)
    C.init_pair(Colors.DOWNBAR, C.COLOR_BLUE, C.COLOR_BLACK)

    C.init_pair(Colors.NORMAL, C.COLOR_BLACK, C.COLOR_GREEN)
    C.init_pair(Colors.SEARCH, C.COLOR_BLACK, C.COLOR_RED)

    # hiding typing and cursor
    C.noecho()
    C.curs_set(0)

    win.clear()
    win.refresh()

    images = sorted(os.listdir("./movieData/"))
    MODE = Modes.NORMAL
    SORT = Sorts.ABC
    selected = 0
    firstOffset = 0

    # animation loop
    try:
        with ueberzug.Canvas() as c:
            showImg = c.create_placement('show', x=52, y=5,
                                         scaler=ueberzug.ScalerOption.FIT_CONTAIN.value)
            showImg.path = " "
            showImg.visibility = ueberzug.Visibility.VISIBLE
            time.sleep(1)

            while True:
                firstOffset = max(0, selected - 16)
                win.clear()

                for i in range(rows):
                    win.addstr(i, 48, "▍", C.color_pair(Colors.DEFAULT))


                win.addstr(1, 5, "ﳜ MOVIES", C.color_pair(Colors.DEFAULT))
                win.addstr(2, 2, "===============", C.color_pair(Colors.DEFAULT))
                # win.addstr(3, 2, str(selected), C.color_pair(Colors.DEFAULT))

                win.addstr(rows-1, 1, " "*(cols-2), C.color_pair(Colors.DOWNBAR) + C.A_DIM)
                if (MODE == Modes.NORMAL):
                    win.addstr(rows-1, 1, " NORMAL ", C.color_pair(Colors.NORMAL)+C.A_BOLD)
                elif (MODE == Modes.SEARCH):
                    win.addstr(rows-1, 1, " SEARCH ", C.color_pair(Colors.SEARCH)+C.A_BOLD)
                    # win.addstr(rows-1, 10, "sdafasdf", C.color_pair(Colors.DOWNBAR))

                if (SORT == Sorts.ABC):
                    win.addstr(rows-1, cols-8, "  ABC  ", C.color_pair(Colors.SELECTED)+C.A_BOLD)
                elif (SORT == Sorts.SCORE):
                    win.addstr(rows-1, cols-8, " SCORE ", C.color_pair(Colors.SELECTED)+C.A_BOLD)

                for idx in range(firstOffset, len(images)):
                    name = images[idx].split(";")[0]
                    if len(name) > 38:
                        name = name[:38] + "..."

                    if(4+idx-firstOffset > 40): break
                    if(selected == idx):
                        win.addstr(4+idx-firstOffset, 1,
                                "{:3.0f}: {}".format(idx+1, name),
                                C.color_pair(Colors.SELECTED)+C.A_BOLD)

                        with c.lazy_drawing:
                            showImg.path = "./movieData/"+images[idx]
                            showImg.width = 20
                            showImg.height = 20
                    else:
                        win.addstr(4+idx-firstOffset, 1,
                                "{:3.0f}: {}".format(idx+1, name),
                                C.color_pair(Colors.DEFAULT))


                s = chr(win.getch(0,0))
                if(s == 'j'):
                    selected += 1
                    if(selected == len(images)): selected = len(images) - 1
                    pass
                elif(s == 'k'):
                    selected -= 1
                    if(selected < 0): selected = 0
                elif(s  == '/'):
                    if(MODE == Modes.NORMAL): MODE = Modes.SEARCH
                    else: MODE = Modes.NORMAL
                elif(s == "G"):
                    selected = len(images) - 1
                elif(s == "g"):
                    selected = 0
                elif(s == "S"):
                    if(SORT == Sorts.ABC): SORT = Sorts.SCORE
                    else: SORT = Sorts.ABC

                sTime = time.time()
                while(time.time() - sTime < 1/60):
                    pass

                win.refresh()

    except KeyboardInterrupt:
        pass
    C.endwin()

# ---------------------------------------------
main()
