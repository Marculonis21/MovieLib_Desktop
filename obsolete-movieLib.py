#!/usr/bin/env python3

import os
import sys
import tqdm
# import time
import readline

import urllib
import urllib.request as req
from bs4 import BeautifulSoup as BS

import pyglet
from pyglet.gl import *

programPath = "/home/marculonis/Desktop/Projects/Python/MovieLib_Desktop/"
path = "/media/marculonis/My Passport/Filmy"

# args section
args = sys.argv

glEnable(GL_BLEND)
glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

window = pyglet.window.Window(800,800, "Movies", resizable = True)
scrollY = 0
debugLines = False
abcSort = True
sortCount = 0

mouseClick = False
mouseX = -1
mouseY = -1

dataFiles = os.listdir(programPath+"movieData/")
fileNames = [x.rsplit('_',1)[0] for x in dataFiles]
imageList = {}
menuIcons = {}

def webScrape(actName):
    name = actName.split(';')
    name.pop()
    sName = name[0]

    if(actName+'@pic_'+sName in fileNames):
        return

    s = sName[:len(sName)-4] + "(" + sName[len(sName)-4:] + ")"

    xxx = list(s)
    for i in range(len(xxx)):
        if(xxx[i] == ' '):
            xxx[i] = '+'
        if(xxx[i] == '&'):
            xxx[i] = 'and'

    _name = ''.join(xxx)

    #https://www.imdb.com/find?q={}&s=tt&ttype=ft

    #1PAGE
    page = req.urlopen("https://www.imdb.com/find?q={}&s=tt&ttype=ft".format(_name))
    soup = BS(page, 'html.parser')

    #Find right section ("title"/"actor")
    fSection = soup.find_all(class_='findSection')
    sel = 0
    for section in range(len(fSection)):
        checkFind = fSection[section].find(class_='findSectionHeader')
        if(checkFind.find('a')["name"] == "tt"):
            sel = section
            break
        else:
            pass

    #findResults
    fFind = fSection[sel].find(class_='findResult odd')
    final = fFind.find("a")["href"]
    
    page = req.urlopen("https://www.imdb.com/{}".format(final))
    # print(_name)
    
    # print(final)
    soup = BS(page, 'html.parser')

    poster = soup.find(class_="poster")
    img = poster.find("img")["src"]

    ###SCORE
    _score = soup.find(class_='ratingValue')
    score = _score.find("span").contents[0]

    req.urlretrieve(img, programPath+"movieData/"+actName+"@pic_"+sName+"_"+score)

def findFiles(_dir, _ext, expand = True):
    found = ""

    for f in os.listdir(_dir):
        workPath = _dir+"/"+f

        if(expand):
            if(os.path.isdir(workPath)):
                found += findFiles(workPath, _ext)

        if(f.split('.').pop() in _ext):
            found += os.path.abspath(workPath) + "\n"

    return found

def loadImages():
    global imageList

    imagePaths = os.listdir(programPath+"movieData/")

    for item in imagePaths:
        img = pyglet.image.load(programPath+"movieData/"+item)
        tex = img.get_texture()
        actW = tex.width 
        actH = tex.height
        rat = actW/actH

        #imageList[item.split('_', 1)[1]] = tex
        imageList[item] = tex

    sortImages()


    global menuIcons
    img = pyglet.image.load(programPath+"projectData/abcIco.png")
    tex = img.get_texture()
    actW = 50 
    actH = 50 
    tex.width = actW
    tex.height = actH
    menuIcons["abcIco.png"] = tex
    
    img = pyglet.image.load(programPath+"projectData/scoreIco.png")
    tex = img.get_texture()
    actW = 46
    actH = 46 
    tex.width = actW
    tex.height = actH
    menuIcons["scoreIco.png"] = tex

def sortImages(ABCSort = True, pCount=1):
    global imageList, sortReverse

    if(ABCSort):
        #ALPHABET SORT
        imageList = dict(sorted(imageList.items(), reverse=(pCount%2==0)))
    else:
        #SCORE SORT
        imageList = dict(sorted(imageList.items(), key = lambda x: x[0].split('_')[-1:], reverse=((pCount+1)%2==0)))

def drawImage(image, x, y, c):
    xx = x - image.width/2
    yy = y - image.height/2
    glColor3f(c,c,c)
    image.blit(xx,yy)
    pass

def drawLine(startX, startY, endX, endY, r=1,g=1,b=1):
    glBegin(GL_LINES)
    glColor3f(r,g,b)
    glVertex2f(int(startX), int(startY))
    glVertex2f(int(endX), int(endY))
    glEnd()

def drawRect(x,y,sizeX,sizeY, r=1,g=1,b=1):
    glBegin(GL_QUADS)
    glColor3f(r,g,b)
    glVertex2f(int(x), int(y))
    glVertex2f(int(x+sizeX), int(y))
    glVertex2f(int(x+sizeX), int(y+sizeY))
    glVertex2f(int(x), int(y+sizeY))
    glEnd()

def drawText(text, x, y, anX='center',anY='center', r=1,g=1,b=1,a=1, size=15, shadow=False, shadowS=4, lWidth=300, hAlign="left"):
    label = pyglet.text.Label(str(text),
                              font_size=size,
                              anchor_x=anX,
                              anchor_y=anY,
                              align = hAlign,
                              multiline=True,
                              width = lWidth)

    label.x = x
    label.y = y

    label.color = (int(r*255),int(g*255),int(b*255), int(a*255))

    if(shadow):
        _label = pyglet.text.Label(str(text),
                                   font_size=size,
                                   anchor_x=anX,
                                   anchor_y=anY,
                                   align = hAlign,
                                   multiline=True,
                                   width = lWidth)

        _label.x = x+shadowS
        _label.y = y-shadowS

        _label.color = (0,0,0, int(a*255))

        _label.draw()

    label.draw()

def winButton(img, text, x, y, sizeX=0, sizeY=0, hover=False, clicked=False, value='vlc', mName=""):
    global mouseClick
    if(sizeX != 0):
        img.width = sizeX
        sizeY = sizeX*1.47
        img.height = sizeY
    elif(sizeY != 0):
        img.height = sizeY
        sizeX = sizeY/1.47
        img.width = sizeX
    else:
        sizeX = img.width
        sizeY = img.height

    if(hover):
        drawImage(img, x, y, 0.5)
    else:
        drawImage(img, x, y, 0.9)

    global abcSort, sortCount
    if(value=='abcsort'):
        if(abcSort):
            drawImage(img, x, y, 0.9)
        else:
            drawImage(img, x, y, 0.4)
    elif(value=='scoresort'):
        if not(abcSort):
            drawImage(img, x, y, 0.9)
        else:
            drawImage(img, x, y, 0.4)

    if(clicked): 
        drawImage(img, x, y, 1)
        mouseClick = False

        if(value=='abcsort'):
            if(abcSort):
                sortCount += 1
            else:
                sortCount = 1

            abcSort = True 
            sortImages(True,sortCount)

        elif(value=='scoresort'):
            if not (abcSort):
                sortCount += 1
            else:
                sortCount = 1

            abcSort = False
            sortImages(False,sortCount)

        elif(value=='vlc'):
            #CVLC = vlc without interface
            #X VLC is better

            window.minimize()
            os.system('/snap/bin/vlc -fd "{}/{}"'.format(path,mName.split('@')[0]))

    if(text != ""):
        if(hover):
            drawText(text, x+sizeX/2, y-sizeY/2, r=0.8,g=0.8,b=0.8)
        else:
            drawText(text, x+sizeX/2, y-sizeY/2, r=1,g=1,b=1)


def tick(t):

    pass

@window.event
def on_mouse_motion(x, y, dx, dy):
    global mouseX, mouseY
    mouseX = x
    mouseY = y

    #print(x,y)

@window.event
def on_mouse_press(x,y,button,mod):
    global mouseClick
    mouseClick = True

@window.event
def on_key_press(key,mod):
    if(key == 113 and mod == 17):
        global debugLines
        if(debugLines):
            debugLines = False
        else:
            debugLines = True

@window.event
def on_mouse_scroll(x, y, scroll_x, scroll_y):
    global scrollY
    scrollY += -50*scroll_y
    if (scrollY < 0):
        scrollY = 0

@window.event
def on_draw():
    global scrollY,debugLfines,mouseX,mouseY,mouseClick,sortCount

    glClearColor(0.3,0.3,0.3,1)
    glClear(GL_COLOR_BUFFER_BIT)
    pyglet.gl.glEnable(pyglet.gl.GL_BLEND)
    pyglet.gl.glBlendFunc(pyglet.gl.GL_SRC_ALPHA, pyglet.gl.GL_ONE_MINUS_SRC_ALPHA)
    glLoadIdentity()

    drawRect(0, scrollY+window.height, window.width, -75, 0.25,0.25,0.25)
    drawRect(0, scrollY+window.height-75, window.width, -4, 0.1,0.1,0.1)

    drawText("Movies", 20, scrollY + window.height-35, anX='left',anY='center', r=0.9,g=0.9,b=0.9, size=45, shadow=True)

    #DEBUGING UPDOWN lines
    if(debugLines):
        drawLine(0,window.height/6,window.width,window.height/6, 1,0,0)
        drawLine(0,window.height/10,window.width,window.height/10, 1,0,0)
        drawLine(0,window.height/6*5,window.width,window.height/6*5, 1,0,0)
        drawLine(0,window.height/10*9,window.width,window.height/10*9, 1,0,0)

    #UP DOWN MOVEMENT
    if(mouseY<window.height/10):
        scrollY+=7
    elif(mouseY<window.height/6):
        scrollY+=3

    if(mouseY>window.height/10*9):
        if(scrollY >= 7):
            scrollY-= 7
    elif(mouseY>window.height/6*5):
        if(scrollY >= 3):
            scrollY-=3

    #MENU ICONS DRAWING
    menuIc = {0:"-40|-40|abcsort|abcIco.png", 1:"-100|-40|scoresort|scoreIco.png"}
    for i in range(len(menuIc)):
        x = window.width+int(menuIc[i].split('|')[0])
        y = window.height+int(menuIc[i].split('|')[1])+scrollY
        sizeX=46
        sizeY=46
        hover = ((mouseX <= x + sizeX/2 and mouseX >= x - sizeX/2) and (mouseY <= y + sizeY/2 and mouseY >= y - sizeY/2))
        clicked = (hover and mouseClick)
        winButton(menuIcons[menuIc[i].split('|')[3]],
                  "",
                  x,
                  y,
                  sizeX,
                  sizeY,
                  hover=hover,
                  clicked=(hover and mouseClick),
                  value=menuIc[i].split('|')[2])

    #MOVIE ICONS DRAWING
    xLoop = 0
    yLoop = 0
    for item in imageList.keys():
        x = window.width/5*(xLoop+1)
        y = scrollY+window.height-200 - (230*yLoop)
        sizeX = window.width/6
        sizeY = sizeX*1.47
        hover = ((mouseX <= x + sizeX/2 and mouseX >= x - sizeX/2) and (mouseY <= y + sizeY/2 and mouseY >= y - sizeY/2))
        clicked = (hover and mouseClick)
        winButton(imageList[item],
                  "",
                  x,
                  y,
                  sizeX,
                  hover=hover,
                  clicked=(hover and mouseClick),
                  value='vlc', mName=item)

        xLoop += 1
        if(xLoop > 3):
            xLoop = 0
            yLoop += 1


#Look through PATH and get all the movies with ending
try:
    _files = findFiles(path, ["mkv","avi","mp4"], False)
except FileNotFoundError:
    print("PATH ERROR: {} -- possibly not found".format(path))
    quit()

files = _files.split('\n')
files.sort()
nFiles = [x.split('/').pop() for x in files]
nFiles.remove(nFiles[0])

#Scrape web with for pictures
for item in tqdm.tqdm(range(len(nFiles))):
    while True:
        try:
            webScrape(nFiles[item])
            break
        except IndexError:
            # print("NAME ERROR: {} -->> SKIPPED".format(nFiles[item]))
            print("NAME ERROR: {}\n".format(nFiles[item]))

            readline.set_startup_hook(lambda: readline.insert_text(nFiles[item]))
            nName = input("New name: ")
            readline.set_startup_hook()
            os.system("/bin/mv '{}/{}' '{}/{}'".format(path,nFiles[item],path,nName))
            nFiles[item] = nName

        except urllib.error.URLError:
            print("NET ERROR: possibly networking issue\n{} -->> SKIPPED".format(nFiles[item]))
            break
        except KeyboardInterrupt:
            print("KEYBOARD INTERRUPT")
            sys.exit(0)
        except:
            print("UNKNOWN ERROR: {} -->> SKIPPED".format(nFiles[item]))
            break

#Load all images as textures before start
loadImages()

#START pyglet app and timer
pyglet.clock.schedule_interval(tick, 1/60)

pyglet.app.run()
