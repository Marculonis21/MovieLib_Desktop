#!/usr/bin/env python3

import curses as C
from enum import Enum
from enum import IntEnum
from http.client import ImproperConnectionState
import os
from os.path import isdir
import random
import sys
import copy
import time

import ueberzug.lib.v0 as ueberzug

PROJECT_PATH = "/home/marculonis/Desktop/Projects/Python/MovieLib_Desktop"
DISC_PATH = "/media/marculonis/My Passport/Filmy"

local_movies = [x for x in os.listdir(PROJECT_PATH+"/localMovies/")]

if(len(sys.argv) > 1):
    if (sys.argv[1] == "--reset"):
        os.system("rm -rf "+PROJECT_PATH+"/movieData/*")

os.system("python3 "+PROJECT_PATH+"/movieLibOMDB.py")

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
    def __init__(self, path, episode=False):
        self.path = PROJECT_PATH+"/movieData/"+path

        self.discPath = path.split('@')[0]
        # attr_string = path.split(";")[1]
        attr_string = path.split('@')[1:]

        if episode:
            keys = ['Title','Season','Episode','Year','Rating', 'Audio','Subt','Duration','Resolution']
        else:
            keys = ['Title','Year','Rating','Audio','Subt','Duration','Resolution']

        attributes = dict(zip(keys, attr_string))

        self.name        = attributes['Title']
        if('_' in self.name): 
            self.name = self.name.replace('_', ':')

        self.year        = attributes['Year']
        self.score       = float(attributes['Rating'])
        self.languages   = attributes['Audio'].split(", ")
        self.subtitles   = attributes['Subt'].split(", ")
        self.duration    = attributes['Duration']
        self.resolution  = attributes['Resolution']

        # overwrite for series files
        if episode:
            parts = path.split('/')[:2] + [attributes['Season']] + [path.split('/',3)[2].split('@')[0]]
            self.discPath = '/'.join(parts)

            self.season = int(attributes['Season'])
            self.episode = int(attributes['Episode'])

            self.name = "[S{:02d}E{:02d}] ".format(self.season, self.episode) + self.name

        # locally stored movies and episodes
        self.isLocal = self.discPath.split('/')[-1] in local_movies
        if self.isLocal: self.localPath = PROJECT_PATH+"/localMovies/"+self.discPath.split('/')[-1]

        if(len(self.languages) > 4):
            self.languages = self.languages[:4]
            self.languages.append("(...)")

        if(len(self.subtitles) > 4):
            self.subtitles = self.subtitles[:4]
            self.subtitles.append("...")

    def toggleLocal(self):
        if self.isLocal:
            self.isLocal = False
            os.system('rm "{}"'.format(self.localPath))
            self.localPath = None
        else:
            self.isLocal = True
            self.localPath = PROJECT_PATH+"/localMovies/"+self.discPath.split('/')[-1]
            os.system('cp "{}/{}" "{}"'.format(DISC_PATH,self.discPath, self.localPath))

    def searchFilter(self, sFilter):
        return (sFilter.lower() in self.name.lower())

    def Play(self):
        if self.isLocal:
            os.system('/usr/bin/vlc -fd "{}"'.format(self.localPath))
        else:
            os.system('/usr/bin/vlc -fd "{}/{}"'.format(DISC_PATH,self.discPath))

class Folder():
    def __init__(self, serie_header):
        series_path = PROJECT_PATH+"/movieData/Series/"+serie_header
        if not os.path.isdir(series_path): return

        seasons = []

        for item in os.listdir(series_path):
            seasons.append(item)

        self.path = series_path

        self.name = serie_header[:-5]
        # if('_' in self.name):
        #     self.name = self.name.replace('_', ':')
        # self.year = serie_header[-4:]

        self.folderMovies = []

        self.attr_file = ""
        for file in os.listdir(self.path):
            if file.split('@')[0] == serie_header:
                self.attr_file = file
            else:
                self.folderMovies.append(Movie("Series/{}/{}".format(serie_header, file), episode=True))

        self.path = self.path+"/"+self.attr_file # PATH IS USED FOR IMG

        attr_string = self.attr_file.split('@')

        keys = ['Head','Title','Year','Rating','Seasons']
        attributes = dict(zip(keys, attr_string))

        self.score = float(attributes['Rating'])
        self.year    = attributes['Year']
        self.seasons = int(attributes['Seasons'])

        self.languages  = ""
        self.subtitles  = ""
        self.duration   = ""
        self.resolution = ""
        self.languages  = ""
        self.subtitles  = ""

    def searchFilter(self, sFilter):
        return (sFilter.lower() in self.name.lower())

    def Open(self):
        return self.folderMovies

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

    # # hiding typing and cursor
    C.noecho()
    C.curs_set(0)

    win.clear()
    win.refresh()
    win.border(0)
    win.timeout(1000)

    MODE = Modes.NORMAL
    SORT = Sorts.ABC
    selected = 0
    folderLevel = 0
    firstNameIndexOffset = 0
    searchText = ""
    HEADER = random.choice(HEADERS)
    NAMES_START_OFFSET = len(HEADER)+2

    MAIN_ITEMS = []
    for file in os.listdir(PROJECT_PATH+"/movieData/"):
        if not(os.path.isdir(PROJECT_PATH+"/movieData/"+file)):
            MAIN_ITEMS.append(Movie(file))

    for folder in os.listdir(PROJECT_PATH+"/movieData/Series"):
        MAIN_ITEMS.append(Folder(folder))

    CURRENT_ITEMS = copy.deepcopy(MAIN_ITEMS)
    CURRENT_ITEMS = sorted(CURRENT_ITEMS, key=lambda x: x.name) # ABC sort default

    current_drawlist = [item for item in CURRENT_ITEMS if item.searchFilter(searchText)]

    ICONS = {"VLINE":"▍",
             "DISK":"ﳜ",
             "DOWNLOADED":"",
             "FOLDER":""}

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

                if(rows < 35):
                    NAMES_START_OFFSET = 1
                else:
                    for i in range(len(HEADER)):
                        win.addstr(1+i, 2, HEADER[i], C.color_pair(Colors.DEFAULT))
                    NAMES_START_OFFSET = len(HEADER)+2

                for i in range(NAMES_START_OFFSET, rows-2):
                    win.addstr(i, PICS_LINE, ICONS["VLINE"], C.color_pair(Colors.DEFAULT))

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
                    win.addstr(rows-1, cols-10, ICONS["DISK"], C.color_pair(Colors.NOTIFICATION_GOOD)+C.A_BOLD)
                else:
                    win.addstr(rows-1, cols-10, ICONS["DISK"], C.color_pair(Colors.NOTIFICATION_BAD)+C.A_BOLD)
                ################################################################ NAMES


                NAMES_MAX_COUNT = rows - NAMES_START_OFFSET - 3
                firstNameIndexOffset = max(0,
                                           min((len(current_drawlist)-1)-NAMES_MAX_COUNT,
                                               selected-NAMES_MAX_COUNT//2))

                for idx in range(firstNameIndexOffset, len(current_drawlist)):

                    path       = current_drawlist[idx].path
                    name       = current_drawlist[idx].name
                    year       = current_drawlist[idx].year
                    resolution = current_drawlist[idx].resolution
                    languages  = current_drawlist[idx].languages
                    subtitles  = current_drawlist[idx].subtitles
                    duration   = current_drawlist[idx].duration
                    score      = current_drawlist[idx].score

                    isLocal = False
                    if(type(current_drawlist[idx]) == Movie):
                        isLocal = current_drawlist[idx].isLocal

                    xPos = 1
                    yPos = NAMES_START_OFFSET+idx-firstNameIndexOffset

                    if (len(name) > PICS_LINE - 10):
                        name = name[:PICS_LINE - 10] + "..."

                    if(idx-firstNameIndexOffset > NAMES_MAX_COUNT):
                        break

                    if(selected == idx):
                        text = ""
                        if(type(current_drawlist[idx]) == Folder):
                            text = " {} : {}".format(ICONS["FOLDER"],name)
                        else:
                            if isLocal:
                                text = " {} : {}".format(ICONS["DOWNLOADED"], name)
                            else:
                                text = "{:3.0f}: {}".format(idx+1, name)

                        win.addstr(yPos, xPos,
                                   text,
                                   C.color_pair(Colors.SELECTED)+C.A_BOLD)

                        with c.lazy_drawing:
                            showImg.path = path
                            showImg.width = cols - PICS_LINE - 3
                            showImg.height = min(18, rows//2-3)
                            showImg.x = PICS_LINE + 2
                            showImg.y = NAMES_START_OFFSET

                        ATTRIB_OFFSET = min(NAMES_START_OFFSET+showImg.height+1, rows-10)
                        win.addstr(ATTRIB_OFFSET+0, PICS_LINE + 2,
                                   "Year: {}".format(year),
                                    C.color_pair(Colors.DEFAULT))
                        win.addstr(ATTRIB_OFFSET+1, PICS_LINE + 2,
                                   "Score: {}".format(score),
                                    C.color_pair(Colors.DEFAULT))
                        if not (type(current_drawlist[idx]) == Folder):
                            win.addstr(ATTRIB_OFFSET+2, PICS_LINE + 2,
                                    "Resolution: {}".format(resolution),
                                        C.color_pair(Colors.DEFAULT))
                            win.addstr(ATTRIB_OFFSET+3, PICS_LINE + 2,
                                    "Duration: {}".format(duration),
                                        C.color_pair(Colors.DEFAULT))
                        
                            yOffset = 0
                            win.addstr(ATTRIB_OFFSET+4, PICS_LINE + 2,
                                    "Languages:",
                                    C.color_pair(Colors.DEFAULT))
                            for lang in range(len(languages)):
                                if(ATTRIB_OFFSET+4+lang >= rows - 2):
                                    break
                                win.addstr(ATTRIB_OFFSET+4+lang, PICS_LINE + 13,
                                        "{}".format(languages[lang]),
                                        C.color_pair(Colors.DEFAULT))
                                yOffset += 1

                            win.addstr(ATTRIB_OFFSET+4+yOffset, PICS_LINE + 2,
                                    "Subtitles:",
                                    C.color_pair(Colors.DEFAULT))
                            for sub in range(len(subtitles)):
                                if(ATTRIB_OFFSET+4+yOffset+sub >= rows - 2):
                                    break
                                win.addstr(ATTRIB_OFFSET+4+yOffset+sub, PICS_LINE + 13,
                                        "{}".format(subtitles[sub]),
                                        C.color_pair(Colors.DEFAULT))
                        else:
                            win.addstr(ATTRIB_OFFSET+2, PICS_LINE + 2,
                                    "Season count: {}".format(current_drawlist[idx].seasons),
                                        C.color_pair(Colors.DEFAULT))

                    else:
                        text = ""
                        if(type(current_drawlist[idx]) == Folder):
                            text = " {} : {}".format(ICONS["FOLDER"], name)

                        else:
                            if isLocal:
                                text = " {} : {}".format(ICONS["DOWNLOADED"], name)
                            else:
                                text = "{:3.0f}: {}".format(idx+1, name)

                        win.addstr(yPos, xPos,
                                   text,
                                   C.color_pair(Colors.DEFAULT))

                        if '[' in text: #]
                            win.addstr(yPos, xPos,
                                       text[:3],
                                       C.color_pair(Colors.DEFAULT))
                            win.addstr(text[3:13],
                                       C.color_pair(Colors.DEFAULT)+C.A_DIM)
                            win.addstr(text[13:],
                                       C.color_pair(Colors.DEFAULT))


                win.refresh()

                ################################################################ KEYS

                key = win.getch(0,0)
                if(key == -1): continue
                else: key = chr(key)

                if(MODE == Modes.NORMAL):
                    if(key == 'j'): #MOVE DOWN
                        selected += 1
                        if(selected == len(current_drawlist)):
                            selected = len(current_drawlist) - 1
                    elif(key == 'k'): #MOVE UP
                        selected -= 1
                        if(selected < 0): selected = 0
                    elif(key == '/'): #TO SEARCH MODE
                        MODE = Modes.SEARCH
                    elif(key == "G"): #TO LAST ITEM
                        selected = len(current_drawlist) - 1
                    elif(key == "g"): #TO FIRST ITEM
                        selected = 0
                    elif(key == "S"): #CHANGE SORT
                        if(SORT == Sorts.ABC):
                            SORT = Sorts.SCORE
                            current_drawlist = sorted(current_drawlist, key=lambda x: x.score, reverse=True) # ABC sort default
                        else:
                            SORT = Sorts.ABC
                            current_drawlist = sorted(current_drawlist, key=lambda x: x.name) # ABC sort default

                    elif(ord(key) == 10): #ENTER #PLAY/#OPEN
                        if(type(current_drawlist[selected]) == Movie and 
                          (os.path.isdir(DISC_PATH) or current_drawlist[selected].isLocal)):
                            current_drawlist[selected].Play()
                        elif(type(current_drawlist[selected]) == Folder):
                            folderLevel += 1
                            CURRENT_ITEMS = current_drawlist[selected].Open()
                            CURRENT_ITEMS = sorted(CURRENT_ITEMS, key=lambda x: x.name) # ABC sort default
                            searchText = ""
                            selected = 0
                            current_drawlist = [item for item in CURRENT_ITEMS if item.searchFilter(searchText)]

                    elif(key == "P"):
                        if(type(current_drawlist[selected]) == Movie):
                            current_drawlist[selected].toggleLocal()

                    elif(key == "q" or key == "Q"): #QUIT 
                        if(folderLevel > 0): # IN FOLDER 
                            folderLevel -= 1
                            CURRENT_ITEMS = copy.deepcopy(MAIN_ITEMS)
                            CURRENT_ITEMS = sorted(CURRENT_ITEMS, key=lambda x: x.name) # ABC sort default
                            searchText = ""
                            selected = 0
                            current_drawlist = [item for item in CURRENT_ITEMS if item.searchFilter(searchText)]
                        else:
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
                    elif(key in "1234567890&-:abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"):
                        searchText += key
                        selected = 0

                    current_drawlist = [movie for movie in CURRENT_ITEMS if movie.searchFilter(searchText)]

                    if(SORT == Sorts.ABC):
                        current_drawlist = sorted(current_drawlist, key=lambda x: x.name) # ABC sort default
                    else:
                        current_drawlist = sorted(current_drawlist, key=lambda x: x.score, reverse=True) # ABC sort default

    except KeyboardInterrupt:
        pass
    C.endwin()

HEADERS = [[
"███╗   ███╗ ██████╗ ██╗   ██╗██╗███████╗███████╗",
"████╗ ████║██╔═══██╗██║   ██║██║██╔════╝██╔════╝",
"██╔████╔██║██║   ██║██║   ██║██║█████╗  ███████╗",
"██║╚██╔╝██║██║   ██║╚██╗ ██╔╝██║██╔══╝  ╚════██║",
"██║ ╚═╝ ██║╚██████╔╝ ╚████╔╝ ██║███████╗███████║",
"╚═╝     ╚═╝ ╚═════╝   ╚═══╝  ╚═╝╚══════╝╚══════╝"],[
" ___ ___   ___   __ __  ____    ___  _____",
"|   |   | /   \\ |  |  ||    |  /  _]/ ___/",
"| _   _ ||     ||  |  | |  |  /  [_(   \\_ ",
"|  \\_/  ||  O  ||  |  | |  | |    _]\\__  |",
"|   |   ||     ||  :  | |  | |   [_ /  \\ |",
"|   |   ||     | \\   /  |  | |     |\\    |",
"|___|___| \\___/   \\_/  |____||_____| \\___|"],[
" _______  _______          _________ _______  _______ ",
"(       )(  ___  )|\\     /|\\__   __/(  ____ \\(  ____ \\",
"| () () || (   ) || )   ( |   ) (   | (    \\/| (    \\/",
"| || || || |   | || |   | |   | |   | (__    | (_____ ",
"| |(_)| || |   | |( (   ) )   | |   |  __)   (_____  )",
"| |   | || |   | | \\ \\_/ /    | |   | (            ) |",
"| )   ( || (___) |  \\   /  ___) (___| (____/\\/\\____) |",
"|/     \\|(_______)   \\_/   \\_______/(_______/\\_______)"],[

" ███▄ ▄███▓ ▒█████   ██▒   █▓ ██▓▓█████   ██████ ",
"▓██▒▀█▀ ██▒▒██▒  ██▒▓██░   █▒▓██▒▓█   ▀ ▒██    ▒ ",
"▓██    ▓██░▒██░  ██▒ ▓██  █▒░▒██▒▒███   ░ ▓██▄   ",
"▒██    ▒██ ▒██   ██░  ▒██ █░░░██░▒▓█  ▄   ▒   ██▒",
"▒██▒   ░██▒░ ████▓▒░   ▒▀█░  ░██░░▒████▒▒██████▒▒",
"░ ▒░   ░  ░░ ▒░▒░▒░    ░ ▐░  ░▓  ░░ ▒░ ░▒ ▒▓▒ ▒ ░",
"░  ░      ░  ░ ▒ ▒░    ░ ░░   ▒ ░ ░ ░  ░░ ░▒  ░ ░",
"░      ░   ░ ░ ░ ▒       ░░   ▒ ░   ░   ░  ░  ░  ",
"       ░       ░ ░        ░   ░     ░  ░      ░  ",
"                         ░                       "],[
"::::    ::::   ::::::::  :::     ::: ::::::::::: :::::::::: :::::::: ",
"+:+:+: :+:+:+ :+:    :+: :+:     :+:     :+:     :+:       :+:    :+:",
"+:+ +:+:+ +:+ +:+    +:+ +:+     +:+     +:+     +:+       +:+       ",
"+#+  +:+  +#+ +#+    +:+ +#+     +:+     +#+     +#++:++#  +#++:++#++",
"+#+       +#+ +#+    +#+  +#+   +#+      +#+     +#+              +#+",
"#+#       #+# #+#    #+#   #+#+#+#       #+#     #+#       #+#    #+#",
"###       ###  ########      ###     ########### ########## ######## "],[
"                                    ,,                 ",
"`7MMM.     ,MMF'                    db                 ",
"  MMMb    dPMM                                         ",
"  M YM   ,M MM  ,pW\"Wq.`7M'   `MF'`7MM  .gP\"Ya  ,pP\"Ybd",
"  M  Mb  M' MM 6W'   `Wb VA   ,V    MM ,M'   Yb 8I   `\"",
"  M  YM.P'  MM 8M     M8  VA ,V     MM 8M\"\"\"\"\"\" `YMMMa.",
"  M  `YM'   MM YA.   ,A9   VVV      MM YM.    , L.   I8",
".JML. `'  .JMML.`Ybmd9'     W     .JMML.`Mbmmd' M9mmmP'"],[
"ooo        ooooo                        o8o                    ",
"`88.       .888'                        `\"'                    ",
" 888b     d'888   .ooooo.  oooo    ooo oooo   .ooooo.   .oooo.o",
" 8 Y88. .P  888  d88' `88b  `88.  .8'  `888  d88' `88b d88(  \"8",
" 8  `888'   888  888   888   `88..8'    888  888ooo888 `\"Y88b. ",
" 8    Y     888  888   888    `888'     888  888    .o o.  )88b",
"o8o        o888o `Y8bod8P'     `8'     o888o `Y8bod8P' 8""888P'"],[
"    e   e                         ,e,              ",
"   d8b d8b     e88 88e  Y8b Y888P  \"   ,e e,   dP\"Y",
"  e Y8b Y8b   d888 888b  Y8b Y8P  888 d88 88b C88b ",
" d8b Y8b Y8b  Y888 888P   Y8b \"   888 888   ,  Y88D",
"d888b Y8b Y8b  \"88 88\"     Y8P    888  \"YeeP\" d,dP "]]

# ---------------------------------------------
main()
