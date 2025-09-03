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
gainPerSong = 8
desiredQuizSize = 30
filePractice = "_practice"
prepListMinSize = 100
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
DMin = 9999
DMax = 8
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

#read length of practice list and length of quiz
with open(filePractice+".json", "r", encoding="utf-8") as file:
    practiceList = json.load(file)
with open(fileQuiz+".json", "r", encoding="utf-8") as file:
    quizList = json.load(file)

#Get new songs if applicable
newSongList = []
newSongCount = desiredQuizSize+random.randint(0,gainPerSong-1)
for song in practiceList:
    newSongCount -= song["X"]
newSongCount = math.floor(newSongCount/gainPerSong)
malIds = set()
if newSongCount > 0 and len(quizList) == 0:
    
    #get new songList: a mix of random songs and songs in prepList. also update weightlist and indexlist to account for their addition
    prepListMalIds = set()
    elementNull = prepList.pop(0)
    for song in prepList:
        prepListMalIds.add(song["malId"])
    random.shuffle(prepList)
    while newSongCount > 0:
        newSongCount -= 1
        '''
        if len(prepList) > 0 and len(loadingList) > 0:
            if random.randint(0,1) and False:
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
            continue'''
        if len(prepList) > 0:
            newSong = prepList.pop(0)
            newSongList.append(newSong)
            malIds.add(newSong["malId"])
            totalDWeight += newSong["D"]
            DList.append(math.exp(newSong["D"]))
            DMin = min(newSong["D"], DMin)
            indexMap[newSong["ID"]] = len(poolSongList)+len(newSongList)-1
            continue
        else:
            print("Warning: Insufficient New Songs")
            break
    #Add new songs to filePrep
    for i in range(len(loadingList)-1,-1,-1):
        if loadingList[i]["malId"] in malIds:
            malIds.remove(loadingList[i]["malId"])
            prepList.append(loadingList.pop(i))
            if len(malIds) == 0:
                break
    #add new shows to filePrep if there aren't enough
    if random.randint(0,1):
        loadingList.sort(key = lambda x : x["songDifficulty"])
    else:
        random.shuffle(loadingList)
    if len(prepList) < prepListMinSize:
        for i in range(len(loadingList)-1,-1,-1):
            if loadingList[i]["malId"] not in prepListMalIds:
                prepListMalIds.add(loadingList[i]["malId"])
                prepList.append(loadingList.pop(i))
        if len(prepList) < prepListMinSize:
            print("Warning: Insufficient Anime Diversity")
        
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
    songWeightStrength = 1-math.pow(0.95,DMax-song["D"])
    for i in range(len(distribution)-1):
        distribution[i+1] += song["sampleWeights"][i]/2
        distribution[i] += song["sampleWeights"][i+1]/2
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

#Update updateMal.json
with open("updateMal.txt", 'r+', encoding = 'utf8') as file:
        fileData = file.read()
        file.seek(0,2)
        for ID in malIds:
            file.write(f"\n{ID}")
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
DList = [0]*(DMax-DMin+1)
for song in poolSongList:
    if song["D"] > DMax:
        song["D"] = DMax
    DList[DMax-song["D"]] += 1
print("DValue distribution")
for index in range(len(DList)):
    if index%4==0:
        print(f"\033[31m{DList[index]}\033[0m", end = " ")
    else:
        print(DList[index], end = " ")
print()
