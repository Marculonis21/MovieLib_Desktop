#!/usr/bin/env python3

import os
import readline  # type: ignore
import subprocess
import sys
import urllib
import urllib.request as req
import logging

from bs4 import BeautifulSoup as BS
import tqdm

programPath = "/home/marculonis/Desktop/Projects/Python/MovieLib_Desktop"
diskPath = "/media/marculonis/My Passport/Filmy"
logging.basicConfig(filename=programPath+'/lastRun.log', filemode='w', format='%(levelname)s - %(message)s')

if not(os.path.isdir(programPath+"/movieData")):
    os.system("mkdir "+programPath+"/movieData")

dataFiles = os.listdir(programPath+"/movieData/")
knownFiles = [x.split('@',1)[0] for x in dataFiles if '@' in x]

dirFiles = os.listdir(programPath+"/movieData/Series/")
for DIR in dirFiles:
    if(os.path.isdir(programPath+"/movieData/Series/"+DIR)):
        dirFiles = os.listdir(programPath+"/movieData/Series/"+DIR)
        for df in dirFiles:
            knownFiles.append(df.split('@',1)[0]);

def getMovieData(fileName, series=False, seriesName=""):
    maxStringLenght = 60
    audio = ""
    subt = ""
    duration = ""
    winWidth = ""
    winHeight = ""

    dirText = ""
    if(series):
        dirText = diskPath+"/Series/"+seriesName+"/"+fileName
    else:
        dirText = diskPath+"/"+fileName

    result = subprocess.run(['mediainfo', '-f', dirText, '|', 'grep', 'List'], stdout=subprocess.PIPE).stdout.decode('utf-8')
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

def tranformName(fileName, series=False, folderName=False):
    #Get name from movie file and change to url string
    if not(folderName):
        name = fileName.split(';')[0]

        if(series):
            name = name[name.find(']')+2:]

    else:
        name = fileName

    name = name[:len(name)-4] + "(" + name[len(name)-4:] + ")"

    urlVersion = list(name)
    for i in range(len(urlVersion)):
        if(urlVersion[i] == ' '):
            urlVersion[i] = '+'
        if(urlVersion[i] == '&'):
            urlVersion[i] = '%26'
        if(urlVersion[i] == '_'):
            urlVersion[i] = ':'

    urlName = ''.join(urlVersion)
    return urlName

def getWebData(urlName, series):
    searchString = ""
    if(series):
        searchString = "https://www.imdb.com/find?q={}&s=tt".format(urlName)
    else:
        searchString = "https://www.imdb.com/find?q={}&s=tt&exact=true".format(urlName)

    page = req.urlopen(searchString)
    soup = BS(page, 'html.parser')

    #Find right section ("title")
    fList = soup.find(class_='findList')
    fFind = fList.find(class_='findResult odd')
    final = fFind.find("a")["href"]

    page = req.urlopen("https://www.imdb.com{}".format(final))
    soup = BS(page, 'html.parser')

    ###POSTER
    galeryURL = soup.find(class_='ipc-lockup-overlay ipc-focusable')["href"]
    galeryPage = req.urlopen("https://www.imdb.com{}".format(galeryURL))
    galeryPageSoup = BS(galeryPage, 'html.parser')

    main = galeryPageSoup.find('main')
    mediaViewer = main.find("div",attrs={"data-testid":"media-viewer"})
    internalImgLocation = mediaViewer.find("div", class_='MediaViewerImagestyles__PortraitContainer-sc-1qk433p-2 iUyzNI')
    if(internalImgLocation == None):
        internalImgLocation = mediaViewer.find("div", class_='MediaViewerImagestyles__LandscapeContainer-sc-1qk433p-3 kXRNYt')

    img = internalImgLocation.find("img")["src"]

    ###SCORE
    _score = soup.find("span",class_='AggregateRatingButton__RatingScore-sc-1ll29m0-1 iTLWoV')
    if(_score != None):
        score = _score.contents[0]
    else:
        score = ""

    return img, score


def webScrape(fileName, series=False, seriesName=""):
    #If already processed - skip
    if(fileName in knownFiles):
        return
    if(series and fileName==seriesName):
        if(fileName+";" in knownFiles):
            return


    #THE ONE THING YOU DON'T WANT TO SEE
    if("@" in fileName):
        raise EOFError

    if not(";" in fileName):
        if(series and fileName == seriesName):
            pass
        else:
            raise EOFError

    if (series) and not (fileName[0] == '['):
        if(fileName != seriesName):
            raise EOFError

    urlName = tranformName(fileName, series, fileName==seriesName)

    try:
        img = ""
        score = ""
        audio = ""
        subt = ""
        duration = ""
        width = ""
        height = ""

        img, score = getWebData(urlName, series)
        if(fileName != seriesName):
            audio, subt, duration, width, height = getMovieData(fileName, series, seriesName)

        #FILEFORMAT:
        #<movieDataProjectPath>/(series-name)/<full orig name>@<score>@<audio>@<subt>@<duration>@<width>x<height>@.mlf
        if(series):
            if not(os.path.isdir("{}/movieData/Series".format(programPath,seriesName))):
                os.system("mkdir \"{}/movieData/Series/")
            if not(os.path.isdir("{}/movieData/Series/{}".format(programPath,seriesName))):
                os.system("mkdir \"{}/movieData/Series/{}\"".format(programPath,seriesName))
            if(fileName==seriesName):
                fileName+=";"

            path = "{}/movieData/Series/{}/{}@{}@{}@{}@{}@{}x{}@.mlf".format(programPath,
                                                                             seriesName,
                                                                             fileName,
                                                                             score,
                                                                             audio,
                                                                             subt,
                                                                             duration,
                                                                             width,
                                                                             height)

        else:
            path = "{}/movieData/{}@{}@{}@{}@{}@{}x{}@.mlf".format(programPath,
                                                                   fileName,
                                                                   score,
                                                                   audio,
                                                                   subt,
                                                                   duration,
                                                                   width,
                                                                   height)

        req.urlretrieve(img, path)

    except KeyboardInterrupt:
        raise KeyboardInterrupt
    except AttributeError:
        raise AttributeError

def findFiles(_dir, _ext, expand=True):
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
    movies = findFiles(diskPath, ["mkv","avi","mp4"], False)
    series = findFiles(diskPath+"/Series", ["mkv","avi","mp4"], True)
except FileNotFoundError:
    print("PATH ERROR: {} -- possibly not found".format(diskPath))
    quit()

movieFiles = movies.split('\n')
movieFiles.sort()
allMovieFiles = [x.split('/').pop() for x in movieFiles]
allMovieFiles.remove(allMovieFiles[0])
allFiles = allMovieFiles

seriesFiles = series.split('\n')
seriesFiles.sort()
allSeriesFiles = [x.split('/')[-2:] for x in seriesFiles]
allSeriesFiles.remove(allSeriesFiles[0])

preSeriesNames = series.split('\n')
preSeriesNames.sort()
preSeriesNames.remove(preSeriesNames[0])
parsedSN = []
for s in preSeriesNames:
    sn = s.split("Series/")[1].split('/')[0]
    if not(sn in parsedSN):
        parsedSN.append(sn)

for s in allSeriesFiles:
    allFiles.append(s)

for s in parsedSN:
    allFiles.append([s,s])

series = ""
name = ""
#Scrape web with for pictures
for item in tqdm.tqdm(range(len(allFiles))):
    while True:
        try:
            file = allFiles[item]
            if(len(file) != 2): # movies
                name = file 
                series = ""
                webScrape(name)
            else: # series
                name = file[1]
                series = file[0]
                webScrape(name,True,series)

            break
        except EOFError:
            print("NAME ERROR: {}\n".format(name))

            try:
                readline.set_startup_hook(lambda: readline.insert_text(name))
                newName = input("New name: ")
                readline.set_startup_hook()
                if(series == ""):
                    os.system("/bin/mv '{}/{}' '{}/{}'".format(diskPath,name,diskPath,newName))
                    allFiles[item] = newName
                else:
                    os.system("/bin/mv '{}/Series/{}/{}' '{}/Series/{}/{}'".format(diskPath,series,name,diskPath,series,newName))
                    allFiles[item][1] = newName

            except KeyboardInterrupt:
                print("\nName edit interrupted -->> SKIPPED")
                break;

        except urllib.error.URLError:
            print("NET ERROR: possibly networking issue\n{} -->> SKIPPED".format(allFiles[item]))
            logging.warning("NET - SKIPPED - {}".format(allFiles[item]))
            break
        except KeyboardInterrupt:
            print("KEYBOARD INTERRUPT")
            sys.exit(0)
        except AttributeError:
            print("NOT FOUND ERROR: {} -->> SKIPPED".format(allFiles[item]))
            logging.error("NOT FOUND - {}".format(allFiles[item]))
            break
        except:
            print("UNKNOWN ERROR: {} -->> SKIPPED".format(allFiles[item]))
            logging.warning("UNKNOWN - {}".format(allFiles[item]))
            break
