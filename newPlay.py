#TODO
#Read pool.json (replacing reading all files)
    #ensure all "X" == 0

#Sample songs from pool
    #Don't select random list, always select pool

#Song Selection
    #Set Song Sample based on distribution
    #Distribution Section Weight = (offby2/2+offby1+self)/sumofWeights (not always 4 near endpoints)
    #Distribution is a sample point. Endpoints are start and end. Anything in the middle covers a range of length 100/ceil((n-15)/7).
        #At index 0<i<n-1, sample should be uniformly random between 100/ceil((n-15)/7)*(i-1) and 100/ceil((n-15)/7)*i

#Adding song update
    #Check number of sections in a song one-by-one to see if it takes mean over threshold (initial weight = 12)
    #Create song distribution when adding song to pool.json
    #Always randomize pool

#print information: poolSize, loadingsize, songdistribution

import random
import math
import statistics
import json
import fileinput
import copy
import numpy
import shutil
import sys

#Read ALL Files

'''
fileMerged = "merged"
filePrep = "preplist"
filePrevPractice = "_prevPractice"
fileLoad = "loadingcutlist"
filePool = "pool"
fileAdd = "addThese"
targetDSum = 530
desiredQuizSize = 30
'''
fileMerged = "dummyMerged"
filePrep = "dummyPreplist"
filePrevPractice = "dummyPrevPractice"
fileLoad = "dummyLoad"
filePool = "dummyPool"
fileAdd = "dummyAddThese"
targetDSum = 96
desiredQuizSize = 4

#Index all songs in pool, get their total weight and check that compile doesn't need to be run
DList = []
indexMap = dict()
totalDWeight = 0
songCounter = 0
with open(filePool+".json", "r", encoding="utf-8") as file:
    poolSongList = json.load(file)
    for index, song in enumerate(poolSongList):
        if song["X"] != 0:
            print("Error: Previous quiz not compiled")
            sys.exit(1)
        totalDWeight += song["D"]
        indexMap[song["ID"]] = index
        DList.append(song["D"])
        songCounter += 1

#Get new songs if applicable
newSongList = []
if totalDWeight < targetDSum:

    #get new songList: a mix of random songs and songs in prepList. also update weightlist and indexlist to account for their addition
    with open(filePrep+".json", "r", encoding="utf-8") as file:
        prepList = json.load(file)
        buffer = prepList.pop(0)
    with open(fileLoad+".json", "r", encoding="utf-8") as file:
        loadingList = json.load(file)
    random.shuffle(loadingList)
    while totalDWeight < targetDSum:
        if len(prepList) > 0 and len(loadingList) > 0:
            if random.randInt(0,1):
                newSong = loadingList.pop(0)
            else:
                newSong = prepList.pop(0)
            newSongList.append(newSong)
            totalDWeight += newSong["D"]
            DList.append(newSong["D"])
            indexMap[newSong["ID"]] = len(poolSongList)+len(newSongList)-1
            continue
        elif len(loadingList) > 0:
            newSong = loadingList.pop(0)
            newSongList.append(newSong)
            totalDWeight += newSong["D"]
            DList.append(newSong["D"])
            indexMap[newSong["ID"]] = len(poolSongList)+len(newSongList)-1
            continue
        elif len(prepList) > 0:
            newSong = prepList.pop(0)
            newSongList.append(newSong)
            totalDWeight += newSong["D"]
            DList.append(newSong["D"])
            indexMap[newSong["ID"]] = len(poolSongList)+len(newSongList)-1
            continue
        else:
            print("Insufficient new songs:")
            break
            

    #rewrite fileLoad/prep without the added songs
    with open(fileLoad+".json", "r+", encoding="utf-8") as file:
        file.truncate(0)
        file.seek(0)
        json.dump(loadingList,file,ensure_ascii=False)
        file.seek(0)
        fileData = file.read()
        fileData = fileData.replace(", {","\n,{")
        fileData = fileData.replace("}]","}\n]")
        file.seek(0)
        file.write(fileData)

    with open(filePrep+".json", "r+", encoding="utf-8") as file:
        file.truncate(0)
        file.seek(0)
        prepList.insert(0, buffer)
        json.dump(prepList,file,ensure_ascii=False)
        file.seek(0)
        fileData = file.read()
        fileData = fileData.replace(", {","\n,{")
        fileData = fileData.replace("}]","}\n]")
        file.seek(0)
        file.write(fileData)

    #add record added songs in record (contains the order in which songs were added since a certain point)
    with open(fileAdd+".json", "r+", encoding="utf-8") as file:
        knownList = json.load(file)
        knownList.extend(newSongList)
        file.truncate(0)
        file.seek(0)
        json.dump(knownList,file,ensure_ascii=False)
        file.seek(0)
        fileData = file.read()
        fileData = fileData.replace(", {","\n,{")
        fileData = fileData.replace("}]","}\n]")
        file.seek(0)
        file.write(fileData)
poolSongList.extend(newSongList)


#Pick List and Calculate Song Probabilities

#Pick Songs
songCount = min(desiredQuizSize,len(poolSongList))
randomSongList = list(numpy.random.choice(poolSongList, size = songCount, p = DList, replace = False))

#For each song, pick sample point


#Write quiz list
with open("_quiz.json", 'w', encoding = 'utf8') as f:
    json.dump(randomSongList, f)

#Write new songs to pool and shuffle

#Output D distribution, poolSize, loadingSize
print()
'''
if len(newSongList) > 0:
    print()
    print("Added Songs-----------------------")
    for song in newSongList:
        print(song["animeEnglishName"]+": "+song["songName"]+" by "+song["songArtist"])
'''
print()
print("Pool Size: "+str(songCounter))
