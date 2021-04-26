#!/usr/bin/env python3

import os
import sys
import subprocess
import tqdm
import readline

import urllib
import urllib.request as req
from bs4 import BeautifulSoup as BS

programPath = "/home/marculonis/Desktop/Projects/Python/MovieLib_Desktop"
diskPath = "/media/marculonis/My Passport/Filmy"
imagePaths = os.listdir(programPath+"/movieData/")

dataFiles = os.listdir(programPath+"/movieData/")
knownFiles = [x.split('@',1)[0] for x in dataFiles]

def getMovieData(fileName):
    maxStringLenght = 60
    audio = ""
    subt = ""
    duration = ""
    winWidth = ""
    winHeight = ""

    result = subprocess.run(['mediainfo', '-f', diskPath+"/"+fileName, '|', 'grep', 'List'], stdout=subprocess.PIPE).stdout.decode('utf-8')
    for line in result.split("\n"):
        if(audio != "" and 
           subt != "" and 
           duration != "" and 
           winHeight != "" and 
           winWidth != "" ):
            break

        if(audio == "" and "Audio_Language_List" in line):
            value = line.split(': ')[1]
            if("/" in value):
                value = value.replace(" / ", ", ")
            if(len(value) > maxStringLenght): 
                value = value[:maxStringLenght] + "..."
            audio = value


        elif(subt == "" and "Text_Language_List" in line):
            value = line.split(': ')[1]
            if("/" in value):
                value = value.replace(" / ", ", ")
            if(len(value) > maxStringLenght): 
                value = value[:maxStringLenght] + "..."
            subt = value


        elif(duration == "" and "Duration" in line):
            value = line.split(': ')[1]
            if(":" in value):
                h,m,s = value[:8].split(":")
                h,m,s = int(h),int(m),int(s)
                if(s > 30): 
                    m+=1
                if(m >= 60): 
                    m-=60
                    h+=1

                duration = "{} h {} min".format(h,m)

        elif(winWidth == "" and "Width" in line):
            value = line.split(': ')[1]
            winWidth = value
        elif(winHeight == "" and "Height" in line):
            value = line.split(': ')[1]
            winHeight = value

    return audio, subt, duration, winWidth, winHeight

def webScrape(fileName):
    #If already processed - skip
    if(fileName in knownFiles):
        return

    #THE ONE THING YOU DON'T WANT TO SEE
    if("@" in fileName):
        raise IndexError

    #Get name from movie file and change to url string
    sName = fileName.split(';')[0] 
    
    sName = sName[:len(sName)-4] + "(" + sName[len(sName)-4:] + ")"

    urlVersion = list(sName)
    for i in range(len(urlVersion)):
        if(urlVersion[i] == ' '):
            urlVersion[i] = '+'
        if(urlVersion[i] == '&'):
            urlVersion[i] = 'and'

    urlName = ''.join(urlVersion)

    #https://www.imdb.com/find?q={}&s=tt&ttype=ft

    #1PAGE
    page = req.urlopen("https://www.imdb.com/find?q={}&s=tt&ttype=ft".format(urlName))
    soup = BS(page, 'html.parser')

    #Find right section ("title")
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

    ###POSTER
    poster = soup.find(class_="poster")
    img = poster.find("img")["src"]

    ###SCORE
    _score = soup.find(class_='ratingValue')
    score = _score.find("span").contents[0]

    audio, subt, duration, width, height = getMovieData(fileName)
    
    #FILEFORMAT_
    #<movieDataProjectPath>/<full orig name>@<score>@<audio>@<subt>@<duration>@<width>x<height>@.mlf
    path = "{}/movieData/{}@{}@{}@{}@{}@{}x{}@.mlf".format(programPath,
                                                           fileName,
                                                           score,
                                                           audio,
                                                           subt,
                                                           duration,
                                                           width,
                                                           height)

    req.urlretrieve(img, path)

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
            print("NAME ERROR: {}\n".format(nFiles[item]))

            readline.set_startup_hook(lambda: readline.insert_text(nFiles[item]))
            nName = input("New name: ")
            readline.set_startup_hook()
            os.system("/bin/mv '{}/{}' '{}/{}'".format(diskPath,nFiles[item],diskPath,nName))
            nFiles[item] = nName

        except urllib.error.URLError:
            print("NET ERROR: possibly networking issue\n{} -->> SKIPPED".format(nFiles[item]))
            break
        except KeyboardInterrupt:
            print("KEYBOARD INTERRUPT")
            sys.exit(0)
        # except:
        #     print("UNKNOWN ERROR: {} -->> SKIPPED".format(nFiles[item]))
        #     break
