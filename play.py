import random
import math
import json
import copy
import numpy
import sys

#Read ALL Files

fileMerged = "merged"
#filePrep = "preplist"
#fileLoad = "loadingcutlist"
filePool = "pool"
#fileAdd = "addThese"
fileQuiz = "_quiz"
#gainPerSong = 8
desiredQuizSize = 40
filePractice = "_practice"
#prepListMinSize = 100
rngFile = "addSongRandomValue.txt"
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
#check if quiz exists
with open(fileQuiz+".json", "r", encoding="utf-8") as file:
    quizList = json.load(file)
if len(quizList) > 0:
    print("Quiz Already Exists")
    sys.exit(1)

#Index all songs in pool, get their total weight and check that compile doesn't need to be run
DList = []
DMin = 9999
DMax = 8
indexMap = dict()
maxWeightCount = 0
songCounter = 0
with open(filePool+".json", "r", encoding="utf-8") as file:
    poolSongList = json.load(file)
for index, song in enumerate(poolSongList):
    if song["X"] != 0:
        print("Error: Previous quiz not compiled")
        sys.exit(1)
    if song["D"] == DMax:
        maxWeightCount += 1
    indexMap[song["ID"]] = index
    DList.append(math.exp(song["D"])*len(song["sampleWeights"]))
    DMin = min(DMin, song["D"])
    songCounter += 1

#Pick Songs and Generate Song Section

#Pick Songs
randomSongList = list(numpy.random.choice(poolSongList, size = len(DList), p = DList/numpy.sum(DList), replace = False))
randomSongList = copy.deepcopy(randomSongList)
songCount = 0
for song in randomSongList:
    songCount += 1
    if song["D"] == 8:
         maxWeightCount-= 1
    if maxWeightCount == 0:
        break
randomSongList = randomSongList[:songCount]

#For each song, pick sample point
for index, song in enumerate(randomSongList):
    distribution = copy.deepcopy(song["sampleWeights"])
    #songWeightStrength = 1-math.pow(0.95,DMax-song["D"])
    songWeightStrength = 0.5
    for i in range(len(distribution)-1):
        distribution[i+1] += song["sampleWeights"][i]/3
        distribution[i] += song["sampleWeights"][i+1]/3
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
    random.shuffle(randomSongList)
    json.dump(randomSongList, file)

#Shuffle Pool
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

#Update updateMal.json
'''
with open("updateMal.txt", 'r+', encoding = 'utf8') as file:
        fileData = file.read()
        file.seek(0,2)
        for ID in malIds:
            file.write(f"\n{ID}")
        file.seek(0)
        file.write(fileData)'''
#Reset Random Number
with open(rngFile, 'w', encoding = 'utf8') as f:
    f.write("-1")

#Output D distribution, poolSize, loadingSize
'''
print()
if len(newSongList) > 0:
    print()
    print("Added Songs-----------------------")
    for song in newSongList:
        print(song["animeEnglishName"]+": "+song["songName"]+" by "+song["songArtist"])
'''
print(f"Quiz of Size \033[31m{songCount}\033[0m created")
print()
print(f"Pool Size: {len(DList)} Min D: {DMin}")
DList = [0]*(DMax-DMin+1)
for song in poolSongList:
    if song["D"] > DMax:
        song["D"] = DMax
    DList[int(round(DMax-song["D"]+0.25))] += 1
print("DValue distribution")
for index in range(len(DList)):
    if index%4==0:
        print(f"\033[31m{DList[index]}\033[0m", end = " ")
    else:
        print(DList[index], end = " ")
print()
