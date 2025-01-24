import random
import math
import statistics
import json
import fileinput
import copy
import numpy

#Read ALL Files

fileMerged = "merged.json"
filePrep = "preplist.json"
fileLoad = "loadingcutlist.json"
fileList = ["0cutlist.json", "10cutlist.json", "20cutlist.json", "30cutlist.json", "40cutlist.json", "50cutlist.json", "60cutlist.json", "70cutlist.json", "80cutlist.json", "90cutlist.json", "100cutlist.json", "lastcutlist.json"]
targetSongMean = 530
targetPrepCount = 2
desiredQuizSize = 30
'''
fileMerged = "dummyMerged.json"
filePrep = "dummyPreplist.json"
fileLoad = "dummyLoad.json"
fileList = ["dummy0cutlist.json", "dummy1cutlist.json"]
targetSongMean = 2
targetPrepCount = 2
desiredQuizSize = 2
'''

#Get list of songs in pool
songWeightMap = {}
listWeights = [0]
songCounter = 0
with open(fileList[0], "r", encoding="utf-8") as file:
    poolSongList = json.load(file)
    for song in poolSongList:
        songWeightMap[song["annSongId"]] = song["D"]
        #songPlaceMap[song["annSongId"]] = songCounter
        listWeights[0] += song["D"]
        songCounter += 1

#Read all relevant files and get the song weight total for those files:
for file in fileList[1:]:
    with open(file, "r", encoding="utf-8") as file:
        localSongList = json.load(file)
        listWeights.append(0)
        for song in localSongList:
            songWeightMap[song["annSongId"]] += song["D"]
            listWeights[-1] += song["D"]

#Get new songs from preplist
songMean = (sum(listWeights))/songCounter

if songMean < targetSongMean:
    newCount = max(0,math.ceil(targetSongMean-songMean))

#pick new preplist songs
    with open(filePrep, "r", encoding="utf-8") as file:
        prepList = json.load(file)
        newCount = min(newCount,len(prepList))
        newSongList = prepList[:newCount]
        prepList = prepList[newCount:]
        songMean += newCount
        newPrepSongCount = max(0,targetPrepCount-len(prepList))
    poolSongList.extend(newSongList)
    for song in newSongList:
        songWeightMap[song["annSongId"]] = len(fileList)
        songCounter += 1

#add new songs to preplist if needed
    with open(fileLoad, "r+", encoding="utf-8") as file:
        loadingList = json.load(file)
        random.shuffle(loadingList)
        prepList.extend(loadingList[:newPrepSongCount])
        loadingList = loadingList[newPrepSongCount:]
        file.truncate(0)
        file.seek(0)
        json.dump(loadingList,file,ensure_ascii=False)
        file.seek(0)
        fileData = file.read()
        fileData = fileData.replace(", {","\n,{")
        fileData = fileData.replace("}]","}\n]")
        file.seek(0)
        file.write(fileData)

    with open(filePrep, "r+", encoding="utf-8") as file:
        file.truncate(0)
        file.seek(0)
        json.dump(prepList,file,ensure_ascii=False)
        file.seek(0)
        fileData = file.read()
        fileData = fileData.replace(", {","\n,{")
        fileData = fileData.replace("}]","}\n]")
        file.seek(0)
        file.write(fileData)

#add new songs to practice lists
    for file in fileList:
        with open(file, "r+", encoding="utf-8") as file:
            localSongList = json.load(file)
            localSongList.extend(newSongList)
            random.shuffle(localSongList)
            file.truncate(0)
            file.seek(0)
            json.dump(localSongList,file,ensure_ascii=False)
            file.seek(0)
            fileData = file.read()
            fileData = fileData.replace(", {","\n,{")
            fileData = fileData.replace("}]","}\n]")
            file.seek(0)
            file.write(fileData)

#Pick List and Calculate Song Probabilities

#picking list
songDeviation = statistics.pstdev(listWeights)
zScores = []
for val in listWeights:
    zScores.append(math.exp((val-songMean)/songDeviation))
quizList = random.choices(fileList, weights = zScores)[0]

#adjusting song probabilities
weightList = []
with open(quizList, "r", encoding="utf-8") as file:
    file.seek(0)
    localSongList = json.load(file)
    for song in localSongList:
        songWeightMap[song["annSongId"]] += song["D"]
    for song in poolSongList:
        weightList.append(math.exp(songWeightMap[song["annSongId"]]))
weightListSum = sum(weightList)
weightList = [weight/weightListSum for weight in weightList]

#Pick Songs, write _quiz, and erase _practice
songCount = min(desiredQuizSize,len(poolSongList))
randomSongList = list(numpy.random.choice(poolSongList, size = songCount, p = weightList, replace = False))

with open("_quiz.json", 'w', encoding = 'utf8') as f:
    json.dump(randomSongList, f)
with open("_practice.json", 'w', encoding = 'utf8') as f:
    f.write("[{}\n]")

#Text Output
print()
print(quizList)
print()
if len(newSongList):
    print("Added Songs-----------------------")
    for song in newSongList:
        print(song["animeEnglishName"]+": "+song["songName"]+" by "+song["songArtist"])
print()
print("Pool Size: "+str(songCounter))
