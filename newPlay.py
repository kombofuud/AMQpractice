#TODO
#Read quiz.json
    #extract list of songs from game
    #store as a list of annSongIds

#Read practice.json
    #extract songs missed and extra songs. Update accordingly. Check to see if list was scrapped.
    #first element contains a number that is incremented every time that a hit, miss, skip, occurs (but not confusion). Number counts the number of songs played in the game.
#Read pool.json
    #ensure that the right number of songs in quiz is properly accounted for. (hit, miss, skip, scrapped) when compared to number in practice.json
    #(adjust is null by default)
    #Hit - set adjust=1
    #Miss - set adjust=-1
    #skip - set adjust=0
    #confusion - handled like a miss
    #scrapped - set first element of _practice to number of adjusted songs. (This should be equivalent to the count of adjusted songs)
     
    #For songs in list, adjust both D value and instance distribution, reset adjust
    #For confusion, increment only D

#Sample only based on pool
    #Don't select random list, always select pool

#Song distribution
    #For new songs, create distribution variable containing a number of elements equivalent to songLength.
    #Number of Elements = 2+ceil((n-15)/7)
    #Initial Weight = Number of Elements

#Song Selection
    #Set Song Sample based on distribution
    #Distribution Section Weight = (offby2/2+offby1+self)/sumofWeights (not always 4 near endpoints)
    #Distribution is a sample point. Endpoints are start and end. Anything in the middle covers a range of length 100/ceil((n-15)/7).
        #At index 0<i<n-1, sample should be uniformly random between 100/ceil((n-15)/7)*(i-1) and 100/ceil((n-15)/7)*i
#Adding song update
    #Check number of sections in a song one-by-one to see if it takes mean over threshold
    #Create song distribution when adding song to pool.json

import random
import math
import statistics
import json
import fileinput
import copy
import numpy
import shutil

#Read ALL Files

'''
fileMerged = "merged.json"
filePrep = "preplist.json"
filePrevPractice = "_prevPractice.json"
fileLoad = "loadingcutlist.json"
fileList = ["0cutlist.json", "10cutlist.json", "20cutlist.json", "30cutlist.json", "40cutlist.json", "50cutlist.json", "60cutlist.json", "70cutlist.json", "80cutlist.json", "90cutlist.json", "100cutlist.json", "lastcutlist.json"]
fileAdd = "addThese.json"
targetSongMean = 530
targetPrepCount = 2
desiredQuizSize = 24
'''
fileMerged = "dummyMerged.json"
filePrep = "dummyPreplist.json"
filePrevPractice = "dummyPrevPractice.json"
fileLoad = "dummyLoad.json"
fileList = ["dummy0cutlist.json", "dummy1cutlist.json"]
fileAdd = "dummyAddThese.json"
targetSongMean = 2
targetPrepCount = 2
desiredQuizSize = 2

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
songMean = (sum(listWeights))/len(fileList)
newSongList = []

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

#add new songs to special list
    with open(fileAdd, "r+", encoding="utf-8") as file:
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
shutil.move("_practice.json", filePrevPractice)
with open("_practice.json", 'w', encoding = 'utf8') as f:
    f.write("[{}\n]")

#Text Output
print()
print(quizList)
if len(newSongList) > 0 and False:
    print()
    print("Added Songs-----------------------")
    for song in newSongList:
        print(song["animeEnglishName"]+": "+song["songName"]+" by "+song["songArtist"])
print()
print("Pool Size: "+str(songCounter))
