#!/usr/bin/env python

import utility

import urllib.request as req
import requests
import subprocess
import os
import tqdm

programPath = "/home/marculonis/Desktop/Projects/Python/MovieLib_Desktop"
diskPath = "/media/marculonis/My Passport/Filmy/"

known_data_files = utility.findKnownFiles(programPath+"/movieData/")
# print(known_data_files)

PATH_movie_data = programPath+"/movieData/"
PATH_movie_data_series = PATH_movie_data+"Series/"

def omdb_response(response, file):
    if response['Response'] == 'False':
        print("ERROR - {} --> {}".format(response['Error'], file))
        return False

    return True

def omdb_movieData(name, year, file):
    response = requests.get(REQUEST_MOVIE.format(name, year)).json()

    if omdb_response(response, file):
        return response

def omdb_seriesData(name, year, file):
    response = requests.get(REQUEST_SERIE.format(name, year)).json()

    if omdb_response(response, file):
        return response

def omdb_episodeData(name, season, episode, file):
    response = requests.get(REQUEST_EPISODE.format(name, season, episode)).json()

    if omdb_response(response, file):
        return response

def retrieve_img(data, path, file):
    try:
        req.urlretrieve(data['Poster'], path)
    except FileNotFoundError:
        print("URLRETRIEVE FAIL - {}".format(file))

def getMediaData(fileName, series=False, seriesName="", season=1):
    maxStringLenght = 50
    audio = ""
    subt = ""
    duration = ""
    winWidth = ""
    winHeight = ""

    dirText = ""
    if(series):
        dirText = diskPath+"Series/"+seriesName+"/"+str(season)+"/"+fileName
    else:
        dirText = diskPath+fileName

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


try:
    movies = utility.findFiles(diskPath, expand=False)
    series = utility.findFiles(diskPath+"Series", [], expand=True)
except FileNotFoundError:
    print("PATH ERROR: {} -- possibly not found".format(diskPath))
    quit()
REQUEST_MOVIE   = "http://www.omdbapi.com/?apikey=420bc901&t={}&y={}&type=movie"
REQUEST_SERIE   = "http://www.omdbapi.com/?apikey=420bc901&t={}&y={}&type=series"
REQUEST_EPISODE = "http://www.omdbapi.com/?apikey=420bc901&t={}&Season={}&Episode={}&type=episode"
# path = "{}/movieData/{}@{}@{}@{}@{}@{}x{}@.mlf".format(programPath,
#                                                         fileName,
#                                                         score,
#                                                         audio,
#                                                         subt,
#                                                         duration,
#                                                         width,
#                                                         height)

# for i in tqdm.tqdm(range(1)):
for i in tqdm.tqdm(range(len(movies))):
    movie_path = movies[i][0]

    # skip known
    if (movie_path in known_data_files): continue

    skipped = False
    while True:
        try:
            utility.checkName(movie_path)
            break
        except EOFError as e:
            out = utility.rename(diskPath, movie_path)
            if out == None:
                print("SKIPPED")
                skipped = True
                break
            else:
                movie_path = out

    if skipped: continue

    audio, subt, duration, width, height = getMediaData(movie_path)
    movie_name, year = utility.tranformName(movie_path)
    data = omdb_movieData(movie_name, year, movie_path)

    if data == None: continue

    TITLE = data['Title']
    YEAR = data['Year']
    RATING = data['imdbRating']

    path = PATH_movie_data+"{}@{}@{}@{}@{}@{}@{}@{}x{}@.mlf".format(movie_path,
                                                                    TITLE,
                                                                    YEAR,
                                                                    RATING,
                                                                    audio,
                                                                    subt,
                                                                    duration,
                                                                    width,
                                                                    height)
    retrieve_img(data, path, movie_path)

for i in tqdm.tqdm(range(len(series))):
# for i in tqdm.tqdm(range(1)):
    group = series[i]

    # INDEX IN INDEX IN INDEX IN INDEX
    serie_header = group[0][0][0][0]
    PATH_serie_data = PATH_movie_data_series+serie_header

    if not (os.path.isdir(PATH_serie_data)):
        os.makedirs(PATH_serie_data)

    serie_name = serie_header[:-5]
    serie_year = serie_header[-4:]

    data = None
    if not (serie_header in known_data_files):
        data = omdb_seriesData(serie_name, serie_year, serie_header)

    if data != None:
        TITLE = data['Title']
        YEAR = data['Year']
        RATING = data['imdbRating']
        SEASONS = data['totalSeasons']


        path = PATH_serie_data+"/{}@{}@{}@{}@{}@.mlf".format(serie_header,
                                                             TITLE,
                                                             YEAR,
                                                             RATING,
                                                             SEASONS)

        retrieve_img(data, path, serie_header)

    for season_group in group:
        for (_,season), file in season_group:
            if (file in known_data_files): continue

            skipped = False
            while True:
                try:
                    utility.checkName(file, series=True)
                    break
                except EOFError as e:
                    out = utility.rename(diskPath, file, serie_header, season)
                    if out == None:
                        print("SKIPPED")
                        skipped = True
                        break
                    else:
                        file = out

            if skipped: continue

            name, episode = utility.tranformName(file, series=True)

            audio, subt, duration, width, height = getMediaData(file, series=True, seriesName=serie_header, season=season)
            data = omdb_episodeData(serie_name, season, episode, file)

            if data == None: continue

            TITLE = data['Title']
            YEAR = data['Year']
            RATING = data['imdbRating']
            SEASON = data['Season']
            EPISODE = data['Episode']

            path = PATH_serie_data+"/{}@{}@{}@{}@{}@{}@{}@{}@{}@{}x{}@.mlf".format(file,
                                                                                   TITLE,
                                                                                   SEASON,
                                                                                   EPISODE,
                                                                                   YEAR,
                                                                                   RATING,
                                                                                   audio,
                                                                                   subt,
                                                                                   duration,
                                                                                   width,
                                                                                   height)
            retrieve_img(data, path, file)
