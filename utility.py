#!/usr/bin/env python

import os
import readline


def findKnownFiles(data_dir):
    PATH_movie_data = data_dir
    PATH_movie_data_series = data_dir+"Series/"

    if not (os.path.isdir(PATH_movie_data)):
        os.system("mkdir "+PATH_movie_data)
        os.system("mkdir "+PATH_movie_data_series)

    if not (os.path.isdir(PATH_movie_data_series)):
        os.system("mkdir "+PATH_movie_data_series)
        
    known_data_files = [x.split('@',1)[0] for x in os.listdir(PATH_movie_data) if '@' in x]

    for serie in os.listdir(PATH_movie_data_series):
        _path = PATH_movie_data_series+serie
        if(os.path.isdir(_path)):
            dir_files = os.listdir(_path)
            for file in dir_files:
                known_data_files.append(file.split('@',1)[0]);
                known_data_files.append(file.split('@',2)[1]);



    return list(set(known_data_files))

def findFiles(dir, group=[], expand=True):
    extensions = ["mkv", "avi", "mp4"]

    files = []

    for f in os.listdir(dir):
        workPath = dir+"/"+f

        if(expand):
            if(os.path.isdir(workPath)):
                next_group = group + [f]
                files.append(findFiles(workPath, next_group, True))

        if(f.split('.').pop() in extensions):
            files.append([group, f] if len(group) > 0 else [f])

    return files

def checkName(fileName, series=False):
    #THE ONE THING YOU DON'T WANT TO SEE
    if("@" in fileName):
        raise EOFError

    if not(";" in fileName):
        raise EOFError

    if (series) and not (fileName[0] == 'E'):
        raise EOFError

def rename(diskPath, fileName, series="", season=1):
    print("NAME ERROR: {}\n".format(fileName))

    try:
        readline.set_startup_hook(lambda: readline.insert_text(fileName))
        newName = input("New name: ")
        readline.set_startup_hook()
        if(series == ""):
            os.system("/bin/mv \"{}/{}\" \"{}/{}\"".format(diskPath,fileName,diskPath,newName))
        else:
            os.system("/bin/mv \"{}/Series/{}/{}/{}\" \"{}/Series/{}/{}/{}\"".format(diskPath,series,season,fileName,
                                                                                     diskPath,series,season,newName))

    except KeyboardInterrupt:
        print("\nName edit interrupted -->> SKIPPED")
        return None

    return newName

def tranformName(fileName, series=False):
    name = year = episode = ""

    #Get name from movie file and change to url string
    name = fileName.split(';')[0]

    if not series:
        year = name[-4:]
        name = name[:-5]
    else:
        episode = int(name[1:4])
        name = name[4:]

    name = list(name)
    for i in range(len(name)):
        if (name[i] == ' '):
            name[i] = '+'
        if(name[i] == '_'):
            name[i] = ':'

    name = ''.join(name)

    if not series:
        return name, year
    else:
        return name, episode
