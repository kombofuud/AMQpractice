import random
import math
import statistics
import json
import fileinput
import copy
import numpy

#Read ALL Files
'''
fileMerged = "merged.json"
fileDead = "dead.json"
fileLearned = "learnedcutlist.json"
filePrep = "preplist.json"
fileLoad = "loadingcutlist.json"
fileList = ["0cutlist.json", "10cutlist.json", "20cutlist.json", "30cutlist.json", "40cutlist.json", "50cutlist.json", "60cutlist.json", "70cutlist.json", "80cutlist.json", "90cutlist.json", "100cutlist.json", "lastcutlist.json"]
'''
fileMerged = "dummyMerged.json"
fileDead = "dummyDead.json"
fileLearned = "dummyLearnedcutlist.json"
filePrep = "dummyPreplist.json"
fileLoad = "dummyLoad.json"
fileList = ["dummy0cutlist.json", "dummy1cutlist.json"]

equivalences = "modifications.json"
newURLs = "broken.json"

#Make list of all songs
with open(fileMerged, "r", encoding="utf-8") as file:
    fullSongList = json.load(file)
songMap = {}
songCounter = []
uniqueSongCounter = []
for index, song in enumerate(fullSongList):
    songMap[song["annSongId"]] = index
    songCounter.append(0)
    uniqueSongCounter.append(0)

#Read all relevant files and count song statistics for those files
for file in fileList:
    with open(file, "r", encoding="utf-8") as file:
        localSongSet = set()
        localSongList = json.load(file)
        for index, song in enumerate(localSongList):
            songCounter[songMap[song["annSongId"]]] += 1
            if song["annSongId"] not in localSongSet:
                localSongSet.add(song["annSongId"])
                uniqueSongCounter[songMap[song["annSongId"]]] += 1
loadCounts = []
for file in [fileLoad, filePrep]:
    with open(file, "r", encoding="utf-8") as file:
        localSongList = json.load(file)
        loadCounts.append(len(localSongList))
        for index, song in enumerate(localSongList):
            songCounter[songMap[song["annSongId"]]] += 1

#update LearnedcutList and mark hard songs
learnedList = []
hardList = []
hardCounter = 0
hardSet = set()
for song in fullSongList:
    if songCounter[songMap[song["annSongId"]]] == 0:
        learnedList.append(song)
        continue
    if songCounter[songMap[song["annSongId"]]]-uniqueSongCounter[songMap[song["annSongId"]]] > 8:
        hardList.append(song)
        hardSet.add(song["annSongId"])
        hardCounter += uniqueSongCounter[songMap[song["annSongId"]]]

#Get new songs from preplist
songMean = (sum(songCounter)-sum(loadCounts)-hardCounter)/len(fileList)
targetSongMean = 530
targetPrepCount = 70
newSongList = []

if songMean < targetSongMean or len(hardList):
    newCount = max(0,math.ceil(targetSongMean-songMean))

    with open(filePrep, "r", encoding="utf-8") as file:
        prepList = json.load(file)
        newCount = min(newCount,len(prepList)
        newSongList.extend(prepList[:newCount])
        prepList = prepList[newCount:].extend(hardList)
        newPrepSongCount = targetPrepCount-len(prepList)
    fullSongList.extend(newSongList)
    for index, song in enumerate(newSongList):
        songMap[song["annSongId"]] = index+len(fullSongList)
        songCounter.append(len(fileList))
        uniqueSongCounter.append(len(fileList))

    with open(fileLoad, "r+", encoding="utf-8") as file:
        loadingList = random.shuffle(json.load(file))
        newSongList.append(loadingList[:newPrepSongCount])
        loadingList = loadingList[newCount:]
        f.truncate(0)
        f.seek(0)
        json.dump(loadingList,f,ensure_ascii=False)
        f.seek(0)
        fileData = f.read()
        fileData = fileData.replace(", {","\n,{")
        fileData = fileData.replace("}]","}\n]")
        f.seek(0)
        f.write(fileData)
        
    with open(filePrep, "w", encoding="utf-8") as file:
        f.truncate(0)
        f.seek(0)
        json.dump(newSongList,f,ensure_ascii=False)
        f.seek(0)
        fileData = f.read()
        fileData = fileData.replace(", {","\n,{")
        fileData = fileData.replace("}]","}\n]")
        f.seek(0)
        f.write(fileData)
        

#Remove hard songs and add new songs
songCounts = []
for file in fileList:
    with open(file, "r+", encoding="utf-8") as file:
        localSongList = json.load(file)
        index = 0
        while index < len(localSongList):
            if localSongList[index]["annSongId"] in hardSongSet:
                localSongList.pop(index)
                continue
            index += 1
        localSongList.extend(newSongList) 
        songCounts.extend(len(localSongList))
        random.shuffle(localSongList)
        f.truncate(0)
        f.seek(0)
        json.dump(localSongList,f,ensure_ascii=False)
        f.seek(0)
        fileData = f.read()
        fileData = fileData.replace(", {","\n,{")
        fileData = fileData.replace("}]","}\n]")
        f.seek(0)
        f.write(fileData)

#Pick List and Calculate Song Probabilities

#picking list
songMean = statistics.mean(songCounts)
songDeviation = statistics.pstdev(zScores)
zScores = []
for val in songCounts:
    zScores.append(exp((val-songMean)/songDeviation))
quizList = random.choices(fileList, weights = zScores)

#adjusting song probabilities

#Pick Songs, write _quiz, and erase _practice

#Text Output
