#!/usr/bin/env python3

import os
import sys
import tqdm
import readline

import urllib
import urllib.request as req
from bs4 import BeautifulSoup as BS

programPath = "/home/marculonis/Desktop/Projects/Python/MovieLib_Desktop"
diskPath = "/media/marculonis/My Passport/Filmy"
imagePaths = os.listdir(programPath+"/movieData/")

dataFiles = os.listdir(programPath+"/movieData/")
fileNames = [x.rsplit('_',1)[0] for x in dataFiles]

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
    soup = BS(page, 'html.parser')

    poster = soup.find(class_="poster")
    img = poster.find("img")["src"]

    ###SCORE
    _score = soup.find(class_='ratingValue')
    score = _score.find("span").contents[0]

    req.urlretrieve(img, programPath+"/movieData/"+actName+"@pic_"+sName+"_"+score)

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

#Look through PATH and get all the movies with ending
try:
    _files = findFiles(diskPath, ["mkv","avi","mp4"], False)
except FileNotFoundError:
    print("PATH ERROR: {} -- possibly not found".format(diskPath))
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
            os.system("/bin/mv '{}/{}' '{}/{}'".format(diskPath,nFiles[item],diskPath,nName))
            nFiles[item] = nName

        except urllib.error.URLError:
            print("NET ERROR: possibly networking issue\n{} -->> SKIPPED".format(nFiles[item]))
            break
        except:
            print("UNKNOWN ERROR: {} -->> SKIPPED".format(nFiles[item]))
            break
