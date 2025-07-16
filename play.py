import random
import math
import json
import copy
import numpy
import sys

#Read ALL Files

fileMerged = "merged"
filePrep = "preplist"
fileLoad = "loadingcutlist"
filePool = "pool"
fileAdd = "addThese"
fileQuiz = "_quiz"
targetDSum = 6400
desiredQuizSize = 30
'''
fileMerged = "dummyMerged"
filePrep = "dummyPreplist"
fileLoad = "dummyLoad"
filePool = "dummyPool"
fileAdd = "dummyAddThese"
fileQuiz = "dummyQuiz"
targetDSum = 96
desiredQuizSize = 4
'''

#Index all songs in pool, get their total weight and check that compile doesn't need to be run
DList = []
DMin = 18
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
    DList.append(math.exp(song["D"]))
    DMin = min(DMin, song["D"])
    songCounter += 1

#read prep and loadingLists
with open(filePrep+".json", "r", encoding="utf-8") as file:
    prepList = json.load(file)
with open(fileLoad+".json", "r", encoding="utf-8") as file:
    loadingList = json.load(file)

#Get new songs if applicable
newSongList = []
if totalDWeight < targetDSum:
    
    #get new songList: a mix of random songs and songs in prepList. also update weightlist and indexlist to account for their addition
    random.shuffle(loadingList)
    elementNull = prepList.pop(0)
    while totalDWeight < targetDSum:
        if len(prepList) > 0 and len(loadingList) > 0:
            if random.randint(0,1):
                newSong = loadingList.pop(0)
            else:
                newSong = prepList.pop(0)
            newSongList.append(newSong)
            totalDWeight += newSong["D"]
            DList.append(math.exp(newSong["D"]))
            DMin = min(newSong["D"], DMin)
            indexMap[newSong["ID"]] = len(poolSongList)+len(newSongList)-1
            continue
        elif len(loadingList) > 0:
            newSong = loadingList.pop(0)
            newSongList.append(newSong)
            totalDWeight += newSong["D"]
            DList.append(math.exp(newSong["D"]))
            DMin = min(newSong["D"], DMin)
            indexMap[newSong["ID"]] = len(poolSongList)+len(newSongList)-1
            continue
        elif len(prepList) > 0:
            newSong = prepList.pop(0)
            newSongList.append(newSong)
            totalDWeight += newSong["D"]
            DList.append(math.exp(newSong["D"]))
            DMin = min(newSong["D"], DMin)
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
        prepList.insert(0, elementNull)
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

#Pick Songs and Generate Song Section

#Pick Songs
songCount = min(desiredQuizSize,len(poolSongList))
randomSongList = list(numpy.random.choice(poolSongList, size = songCount, p = DList/numpy.sum(DList), replace = False))
randomSongList = copy.deepcopy(randomSongList)

#For each song, pick sample point
for index, song in enumerate(randomSongList):
    distribution = copy.deepcopy(song["sampleWeights"])
    songWeightStrength = 1-math.pow(0.95,18-song["D"])
    for i in range(len(distribution)):
        distribution[i] = math.pow(len(distribution),distribution[i]*songWeightStrength)
    section = random.choices(range(len(distribution)), weights=distribution, k=1)[0]
    if section == 0:
        samplePoint = 0
    elif section == len(distribution)-1:
        samplePoint = 100
    else:
        samplePoint = 100/(len(distribution)-2)*(section+random.random()-1)
    if samplePoint < 0 or samplePoint > 100:
        print("Error: Sample point out of range. S="+str(samplePoint))
    randomSongList[index]["startPoint"] = samplePoint

#Write quiz list
with open(fileQuiz+".json", 'w', encoding = 'utf8') as file:
    json.dump(randomSongList, file)

#Write new songs to pool and shuffle
with open(filePool+".json", 'r+', encoding = 'utf8') as file:
        file.truncate(0)
        file.seek(0)
        random.shuffle(poolSongList)
        json.dump(poolSongList,file,ensure_ascii=False)
        file.seek(0)
        fileData = file.read()
        fileData = fileData.replace(", {","\n,{")
        fileData = fileData.replace("}]","}\n]")
        file.seek(0)
        file.write(fileData)

#Output D distribution, poolSize, loadingSize
'''
print()
if len(newSongList) > 0:
    print()
    print("Added Songs-----------------------")
    for song in newSongList:
        print(song["animeEnglishName"]+": "+song["songName"]+" by "+song["songArtist"])
'''
print()
print(f"Pool Size: {len(poolSongList)} LoadingSize: {len(loadingList)+len(prepList)-1} TotalD: {totalDWeight} Min D: {DMin}")
DList = [0]*(19-DMin)
for song in poolSongList:
    if song["D"] > 18:
        song["D"] = 18
    DList[18-song["D"]] += 1
print("DValue distribution")
for index in range(len(DList)):
    if index%6==0:
        print(f"\033[31m{DList[index]}\033[0m", end = " ")
    else:
        print(DList[index], end = " ")
print()
