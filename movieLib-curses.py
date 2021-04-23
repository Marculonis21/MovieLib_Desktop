#!/usr/bin/env python3


from enum import Enum
from enum import IntEnum

import curses as C
import os
import sys
import time
import ueberzug.lib.v0 as ueberzug

PROJECT_PATH = "/home/marculonis/Desktop/Projects/Python/MovieLib_Desktop"
DISC_PATH = "/media/marculonis/My Passport/Filmy"

if(len(sys.argv) > 1):
    if not (sys.argv[1] == "-debug"):
        os.system("python3 "+PROJECT_PATH+"/movieLibScrape.py")
else:
    os.system("python3 "+PROJECT_PATH+"/movieLibScrape.py")


HEADER = [
"███╗   ███╗ ██████╗ ██╗   ██╗██╗███████╗███████╗",
"████╗ ████║██╔═══██╗██║   ██║██║██╔════╝██╔════╝",
"██╔████╔██║██║   ██║██║   ██║██║█████╗  ███████╗",
"██║╚██╔╝██║██║   ██║╚██╗ ██╔╝██║██╔══╝  ╚════██║",
"██║ ╚═╝ ██║╚██████╔╝ ╚████╔╝ ██║███████╗███████║",
"╚═╝     ╚═╝ ╚═════╝   ╚═══╝  ╚═╝╚══════╝╚══════╝",
]

NAMES_START_OFFSET = 8
NAMES_MAX_COUNT = 40
PICS_LINE = 0
ATTRIB_OFFSET = 28

class Colors(IntEnum):
    DEFAULT = 1
    SELECTED = 2
    DOWNBAR = 3
    NORMAL = 4
    SEARCH = 5
    NOTIFICATION_GOOD = 6
    NOTIFICATION_BAD = 7

class Modes(Enum):
    NORMAL = 1
    SEARCH = 2

class Sorts(Enum):
    ABC = 1
    SCORE = 2

class Movie():
    def __init__(self, path):
        name_string = path.split(";")[0]
        attr_string = path.split(";")[1]

        self.path = PROJECT_PATH+"/movieData/"+path
        self.discPath = path.split('@')[0]

        self.name = name_string[:-5]
        self.year = name_string[-4:]
        self.resolution = ""
        self.languages = [""]
        self.subtitles = [""]
        self.duration = ""
        self.score = float(attr_string[-3:])


    def searchFilter(self, sFilter):
        return (sFilter.lower() in self.name.lower())

    def Play(self):
        os.system('/usr/bin/vlc -fd "{}/{}"'.format(DISC_PATH,self.discPath))


def main():
    # new window
    win = C.initscr()

    C.start_color()
    C.use_default_colors()

    # color pairs
    C.init_pair(Colors.DEFAULT, C.COLOR_BLUE, -1)
    C.init_pair(Colors.SELECTED, C.COLOR_BLACK, C.COLOR_BLUE)
    C.init_pair(Colors.DOWNBAR, C.COLOR_BLUE, C.COLOR_BLACK)

    C.init_pair(Colors.NORMAL, C.COLOR_BLACK, C.COLOR_GREEN)
    C.init_pair(Colors.SEARCH, C.COLOR_BLACK, C.COLOR_RED)

    C.init_pair(Colors.NOTIFICATION_GOOD, C.COLOR_WHITE, C.COLOR_BLACK)
    C.init_pair(Colors.NOTIFICATION_BAD, C.COLOR_RED, C.COLOR_BLACK)

    # hiding typing and cursor
    C.noecho()
    C.curs_set(0)

    win.clear()
    win.refresh()

    MODE = Modes.NORMAL
    SORT = Sorts.ABC
    selected = 0
    firstNameIndexOffset = 0
    searchText = ""

    movies = []
    for file in os.listdir(PROJECT_PATH+"/movieData/"):
        movies.append(Movie(file))
    movies = sorted(movies, key=lambda x: x.name) # ABC sort default
    movies_drawlist = [movie for movie in movies if movie.searchFilter(searchText)]

    # animation loop
    try:
        with ueberzug.Canvas() as c:
            showImg = c.create_placement('show', x=50, y=9,
                                         scaler=ueberzug.ScalerOption.FIT_CONTAIN.value)
            showImg.path = ""
            showImg.visibility = ueberzug.Visibility.VISIBLE

            while True:
                win.erase()

                rows, cols = win.getmaxyx()
                PICS_LINE = int(cols*0.65)

                ################################################################ UI

                for i in range(len(HEADER)):
                    win.addstr(1+i, 2, HEADER[i], C.color_pair(Colors.DEFAULT))

                for i in range(NAMES_START_OFFSET, rows-2):
                    win.addstr(i, PICS_LINE, "▍", C.color_pair(Colors.DEFAULT))

                win.addstr(rows-1, 1, " "*(cols-2), C.color_pair(Colors.DOWNBAR) + C.A_DIM)
                if (MODE == Modes.NORMAL):
                    win.addstr(rows-1, 1, " NORMAL ", C.color_pair(Colors.NORMAL)+C.A_BOLD)
                    win.addstr(rows-1, 10, "{}".format(searchText), C.color_pair(Colors.DOWNBAR))
                elif (MODE == Modes.SEARCH):
                    win.addstr(rows-1, 1, " SEARCH ", C.color_pair(Colors.SEARCH)+C.A_BOLD)
                    win.addstr(rows-1, 10, searchText, C.color_pair(Colors.DOWNBAR))

                if (SORT == Sorts.ABC):
                    win.addstr(rows-1, cols-8, "  ABC  ", C.color_pair(Colors.SELECTED)+C.A_BOLD)
                elif (SORT == Sorts.SCORE):
                    win.addstr(rows-1, cols-8, " SCORE ", C.color_pair(Colors.SELECTED)+C.A_BOLD)


                if(os.path.isdir(DISC_PATH)):
                    win.addstr(rows-1, cols-10, "ﳜ", C.color_pair(Colors.NOTIFICATION_GOOD)+C.A_BOLD)
                else:
                    win.addstr(rows-1, cols-10, "ﳜ", C.color_pair(Colors.NOTIFICATION_BAD)+C.A_BOLD)
                ################################################################ NAMES


                ATTRIB_OFFSET = min(28, rows-10)
                NAMES_MAX_COUNT = rows - NAMES_START_OFFSET - 3
                firstNameIndexOffset = max(0,
                                           min((len(movies_drawlist)-1)-NAMES_MAX_COUNT,
                                               selected-NAMES_MAX_COUNT//2))

                for idx in range(firstNameIndexOffset, len(movies_drawlist)):

                    path       = movies_drawlist[idx].path
                    name       = movies_drawlist[idx].name
                    year       = movies_drawlist[idx].year
                    resolution = movies_drawlist[idx].resolution
                    languages  = movies_drawlist[idx].languages
                    subtitles  = movies_drawlist[idx].subtitles
                    duration   = movies_drawlist[idx].duration
                    score      = movies_drawlist[idx].score

                    xPos = 1
                    yPos = NAMES_START_OFFSET+idx-firstNameIndexOffset

                    if (len(name) > PICS_LINE - 10):
                        name = name[:PICS_LINE - 10] + "..."

                    if(idx-firstNameIndexOffset > NAMES_MAX_COUNT):
                        break
                    if(selected == idx):
                        win.addstr(yPos, xPos,
                                   "{:3.0f}: {}".format(idx+1, name),
                                    C.color_pair(Colors.SELECTED)+C.A_BOLD)

                        with c.lazy_drawing:
                            showImg.path = path
                            showImg.width = cols - PICS_LINE - 3
                            showImg.height = min(18, rows//2)
                            showImg.x = PICS_LINE + 2

                        win.addstr(ATTRIB_OFFSET+0, PICS_LINE + 2,
                                   "Year: {}".format(year),
                                    C.color_pair(Colors.DEFAULT))
                        win.addstr(ATTRIB_OFFSET+1, PICS_LINE + 2,
                                   "Score: {}".format(score),
                                    C.color_pair(Colors.DEFAULT))
                        win.addstr(ATTRIB_OFFSET+2, PICS_LINE + 2,
                                   "Resolution: {}".format(resolution),
                                    C.color_pair(Colors.DEFAULT))
                        win.addstr(ATTRIB_OFFSET+3, PICS_LINE + 2,
                                   "Duration: {}".format(duration),
                                    C.color_pair(Colors.DEFAULT))
                        win.addstr(ATTRIB_OFFSET+4, PICS_LINE + 2,
                                   "Languages: {}".format(*languages),
                                    C.color_pair(Colors.DEFAULT))
                        win.addstr(ATTRIB_OFFSET+5, PICS_LINE + 2,
                                   "Subtitles: {}".format(*subtitles),
                                    C.color_pair(Colors.DEFAULT))

                    else:
                        win.addstr(yPos, xPos,
                                   "{:3.0f}: {}".format(idx+1, name),
                                   C.color_pair(Colors.DEFAULT))

                ################################################################ KEYS

                key = chr(win.getch(0,0))
                if(MODE == Modes.NORMAL):
                    if(key == 'j'): #MOVE DOWN
                        selected += 1
                        if(selected == len(movies_drawlist)):
                            selected = len(movies_drawlist) - 1
                    elif(key == 'k'): #MOVE UP
                        selected -= 1
                        if(selected < 0): selected = 0
                    elif(key == '/'): #TO SEARCH MODE
                        MODE = Modes.SEARCH
                    elif(key == "G"): #TO LAST ITEM
                        selected = len(movies_drawlist) - 1
                    elif(key == "g"): #TO FIRST ITEM
                        selected = 0
                    elif(key == "S"): #CHANGE SORT
                        if(SORT == Sorts.ABC):
                            SORT = Sorts.SCORE
                            movies_drawlist = sorted(movies_drawlist, key=lambda x: x.score, reverse=True) # ABC sort default
                        else:
                            SORT = Sorts.ABC
                            movies_drawlist = sorted(movies_drawlist, key=lambda x: x.name) # ABC sort default

                    elif(ord(key) == 10): #PLAY
                        path = movies_drawlist[selected].Play()

                    elif(key == "q" or key == "Q"): #QUIT 
                        break
                    elif(key == "M" or key == "N"): #Open NAUTILUS FOR MOUNT
                        os.system("nautilus ~/")
                        win.clear()

                else:
                    if(key == '/'): #TO NORMAL MODE
                        MODE = Modes.NORMAL
                    elif(ord(key) == 10): #ENTER
                        MODE = Modes.NORMAL
                    elif(ord(key) == 127): #BACKSPACE
                        searchText = searchText[:-1]
                    elif(ord(key) == 32): #SPACE
                        searchText += " "
                    elif(ord(key) == 27): #ESCAPE
                        MODE = Modes.NORMAL
                    elif(key in "1234567890&-abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"):
                        searchText += key
                        selected = 0

                    movies_drawlist = [movie for movie in movies if movie.searchFilter(searchText)]

                    if(SORT == Sorts.ABC):
                        movies_drawlist = sorted(movies_drawlist, key=lambda x: x.score, reverse=True) # ABC sort default
                    else: movies_drawlist = sorted(movies_drawlist, key=lambda x: x.name) # ABC sort default


                win.refresh()

    except KeyboardInterrupt:
        pass
    C.endwin()

# ---------------------------------------------
main()
