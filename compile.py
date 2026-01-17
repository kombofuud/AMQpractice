import json
import sys
import math
import copy
import random
import numpy

fileQuiz = "_quiz"
filePractice = "_practice"
filePool = "pool"
filePrevPool = "prevPool"
filePrevQuiz = "prevQuiz"
filePrevPrep = "prevPrep"
filePrep = "preplist"
filePrevLoad = "prevLoading"
fileLoad = "loadingcutlist"
fileAdd = "addThese"
filePrevAdd = "prevAddThese"
gainFile = "prevgain.txt"
prevGainFile = "prevprevgain.txt"
malUpdateFile = "updateMal.txt"
prevMalUpdateFile = "prevUpdateMal.txt"
prepListMinSize = 150
'''
fileQuiz = "dummyQuiz"
filePractice = "dummyPractice"
filePool = "dummyPool"
filePrevPool = "dummyPrevPool"
'''

#read files and create dict containing quiz songs
with open(filePool+".json", 'r', encoding = 'utf8') as f:
    songPool = json.load(f)

quizIds = dict()
quizSamples = dict()
quizNumbers = dict()
with open(fileQuiz+".json", 'r', encoding = 'utf8') as f:
    quizSongs = json.load(f)
    for index, song in enumerate(quizSongs):
        quizIds[song["ID"]] = 0.0
        quizSamples[song["ID"]] = song["startPoint"]
        quizNumbers[song["ID"]] = index+1

with open(filePrep+".json", 'r', encoding = 'utf8') as f:
    prepSongs = json.load(f)
    elementNull = prepSongs.pop(0)

with open(fileLoad+".json", 'r', encoding = 'utf8') as f:
    loadingSongs = json.load(f)

#assume all songs must be accounted for unless user says otherwise. If user types a negative number, that indicates the number of skipped songs.
if len(sys.argv) > 1:
    argVal = int(sys.argv[1])
    if argVal < 0:
        argVal += len(quizSongs)
else:
    argVal = len(quizSongs)

#if quizSongs is empty, reset the pool list to before the update
if len(quizSongs) == 0 and len(songPool) > 0:
    with open(filePrevPool+".json", 'r', encoding = 'utf8') as f:
        prevSongs = json.load(f)
    with open(filePool+".json", 'r+', encoding = 'utf8') as f:
        f.truncate(0)
        f.seek(0)
        json.dump(prevSongs,f,ensure_ascii=False)
        f.seek(0)
        fileData = f.read()
        fileData = fileData.replace(", {","\n,{")
        fileData = fileData.replace("}]","}\n]")
        f.seek(0)
        f.write(fileData)
    with open(filePrevQuiz+".json", 'r', encoding = 'utf8') as f:
        prevQuizSongs = json.load(f)
    with open(fileQuiz+".json", 'r+', encoding = 'utf8') as f:
        f.truncate(0)
        f.seek(0)
        json.dump(prevQuizSongs,f,ensure_ascii=False)
        f.seek(0)
        fileData = f.read()
        fileData = fileData.replace(", {","\n,{")
        fileData = fileData.replace("}]","}\n]")
        f.seek(0)
        f.write(fileData)
    with open(filePrevPrep+".json", 'r', encoding = 'utf8') as f:
        prevPrepSongs = json.load(f)
    with open(filePrep+".json", 'r+', encoding = 'utf8') as f:
        f.truncate(0)
        f.seek(0)
        json.dump(prevPrepSongs,f,ensure_ascii=False)
        f.seek(0)
        fileData = f.read()
        fileData = fileData.replace(", {","\n,{")
        fileData = fileData.replace("}]","}\n]")
        f.seek(0)
        f.write(fileData)
    with open(filePrevLoad+".json", 'r', encoding = 'utf8') as f:
        prevLoadSongs = json.load(f)
    with open(fileLoad+".json", 'r+', encoding = 'utf8') as f:
        f.truncate(0)
        f.seek(0)
        json.dump(prevLoadSongs,f,ensure_ascii=False)
        f.seek(0)
        fileData = f.read()
        fileData = fileData.replace(", {","\n,{")
        fileData = fileData.replace("}]","}\n]")
        f.seek(0)
        f.write(fileData)
    with open(prevMalUpdateFile, 'r', encoding = 'utf8') as f:
        prevMalUpdates = f.read()
    with open(malUpdateFile, 'w', encoding = 'utf8') as f:
        f.truncate(0)
        f.seek(0)
        f.write(prevMalUpdates)
    with open(filePrevAdd+".json", 'r', encoding = 'utf8') as f:
        prevAddedSongOrder = f.read()
    with open(fileAdd+".json", 'w', encoding = 'utf8') as f:
        f.truncate(0)
        f.seek(0)
        f.write(prevAddedSongOrder)
    with open(prevGainFile, 'r', encoding = 'utf8') as f:
        prevGains = f.read()
    with open(gainFile, 'w', encoding = 'utf8') as f:
        f.truncate(0)
        f.seek(0)
        f.write(prevGains)
    print("Pool+Quiz+Prep+Load+Update+AddedOrder+fileGains Restored")
    '''with open(filePractice+".json", 'r', encoding = 'utf8') as f:
        practiceSongs = json.load(f)
    for song in practiceSongs:
        print(f"{song["SN"]} __from__ {song["EN"]}")'''
    sys.exit(0)

#Run through list of quizSongs and check for songs which are marked for an update. 1 is a correct, 2 is a miss
extraIds = set()
idIndices = dict()
extraIndices = dict()
practice = []
errorQ = 0
missedCount = 0
maxD = -100
minD = 0
prevWeightCount = 0
prevNewSongs = 0

for i, song in enumerate(songPool):
    prevWeightCount += 2/(1+math.exp(song["D"]))
    if song["D"] == 0 and type(song["D"]) is int:
        prevNewSongs += 1
    if song["ID"] in quizIds:
        idIndices[song["ID"]] = i
        if song["X"] == 1:
            quizIds[song["ID"]] = math.sqrt(1+math.log(1+math.exp(-song["D"])))
        elif song["X"] == 2:
            quizIds[song["ID"]] = -math.sqrt(1+math.log(1+math.exp(song["D"])))
            missedCount += 1
        #if quizIds[song["ID"]] <= 0 and quizIds[song["ID"]]+song["D"] < 0:
        if quizIds[song["ID"]] <= 0:
            pSong = copy.deepcopy(song)
            pSong["startPoint"] = quizSamples[pSong["ID"]]
            if pSong["startPoint"] == 0:
                pSong["sampleWeights"][0] += 1-(1+pSong["X"])%3
            elif pSong["startPoint"] == 100:
                pSong["sampleWeights"][-1] += 1-(1+pSong["X"])%3
            else:
                sectionCount = len(pSong["sampleWeights"])-2
                pSong["sampleWeights"][math.ceil(pSong["startPoint"]*sectionCount/100)] += 1-(1+pSong["X"])%3
            #songWeightStrength = 1-math.pow(0.95,pSong["D"])
            '''for i in range(len(pSong["sampleWeights"])-1):
                pSong["sampleWeights"][i+1] += song["sampleWeights"][i]/3
                pSong["sampleWeights"][i] += song["sampleWeights"][i+1]/3'''
            for i in range(len(pSong["sampleWeights"])):
                pSong["sampleWeights"][i] = math.log(1+math.pow(math.e,pSong["sampleWeights"][i]))
            pSong["startPoint"] = pSong["sampleWeights"]
            pSong["sampleWeights"] = song["sampleWeights"]
            pSong["D"] += quizIds[song["ID"]]
            pSong["X"] = 2
            practice.append(pSong)
    elif song["X"] != 0:
        errorQ = 1
        extraIds.add(song["ID"])
        extraIndices[song["ID"]] = i
    else:
        maxD = int(round(max(maxD, song["D"])))
        minD = int(round(min(minD, song["D"])))

#Ensure that the correct number of songs were accounted for
countedKeys = 0
ignoredKeys = []
for song in quizSongs:
    if songPool[idIndices[song["ID"]]]["X"] != 0:
        countedKeys += 1
    else:
        ignoredKeys.append(song["ID"])

if countedKeys < argVal:
    print("Insufficient songs updated: "+str(countedKeys)+"/"+str(argVal))
    print("Missing Keys:")
    print("_____________\n")
    for key in ignoredKeys:
        song = songPool[idIndices[key]]
        print(f"{quizNumbers[song["ID"]]}: ANNID={song["ID"]}, {song["SN"]} _from_ {song["EN"]}")
    errorQ = 1
if countedKeys > argVal:
    print("More updates than expected."+str(countedKeys)+"/"+str(argVal))
    for key,update in quizIds.items():
        if update != 0:
            song = songPool[key]
            print("ANNID="+str(song["ID"])+", "+song["SN"]+" _from_ "+song["EN"])
    errorQ = 1
if len(extraIds):
    print("Extra Keys:")
    print("___________")
    for key in extraIds:
        song = songPool[extraIndices[key]]
        print("ANNID="+str(song["ID"])+", "+song["SN"]+" _from_ "+song["EN"])
    errorQ = 1
if errorQ:
    sys.exit(1)


#save copy of pool,quiz,prep,loading,gain to prevPool,prevQuiz etc
with open(filePrevPool+".json", 'r+', encoding = 'utf8') as f:
    f.truncate(0)
    f.seek(0)
    json.dump(songPool,f,ensure_ascii=False)
    f.seek(0)
    fileData = f.read()
    fileData = fileData.replace(", {","\n,{")
    fileData = fileData.replace("}]","}\n]")
    f.seek(0)
    f.write(fileData)

with open(filePrevQuiz+".json", 'r+', encoding = 'utf8') as f:
    f.truncate(0)
    f.seek(0)
    json.dump(quizSongs,f,ensure_ascii=False)
    f.seek(0)
    fileData = f.read()
    fileData = fileData.replace(", {","\n,{")
    fileData = fileData.replace("}]","}\n]")
    f.seek(0)
    f.write(fileData)

with open(filePrevPrep+".json", 'r+', encoding = 'utf8') as f:
    f.truncate(0)
    f.seek(0)
    prepSongs.insert(0, elementNull)
    json.dump(prepSongs,f,ensure_ascii=False)
    elementNull = prepSongs.pop(0)
    f.seek(0)
    fileData = f.read()
    fileData = fileData.replace(", {","\n,{")
    fileData = fileData.replace("}]","}\n]")
    f.seek(0)
    f.write(fileData)

with open(filePrevLoad+".json", 'r+', encoding = 'utf8') as f:
    f.truncate(0)
    f.seek(0)
    json.dump(loadingSongs,f,ensure_ascii=False)
    f.seek(0)
    fileData = f.read()
    fileData = fileData.replace(", {","\n,{")
    fileData = fileData.replace("}]","}\n]")
    f.seek(0)
    f.write(fileData)

with open(malUpdateFile, 'r', encoding = 'utf8') as f:
    malUpdates = f.read()
with open(prevMalUpdateFile, 'w', encoding = 'utf8') as f:
    f.truncate(0)
    f.seek(0)
    f.write(malUpdates)

with open(fileAdd+".json", 'r', encoding = 'utf8') as f:
    addedSongOrder = f.read()
with open(filePrevAdd+".json", 'w', encoding = 'utf8') as f:
    f.truncate(0)
    f.seek(0)
    f.write(addedSongOrder)

with open(gainFile, 'r', encoding = 'utf8') as f:
    targetMean, oldWeight, prevGain = [float(line.strip()) for line in f.readlines()]
with open(prevGainFile, 'w', encoding = 'utf8') as f:
    f.truncate(0)
    f.seek(0)
    f.write(f"{targetMean}\n")
    f.write(f"{oldWeight}\n")
    f.write(f"{prevGain}\n")

#Update all keys
print("Missed Song Numbers_______")
for i, song in enumerate(quizSongs):
    if quizIds[song["ID"]] < 0.0:
        print(f"{i+1}", end = ' ')
print()

for ID, index in idIndices.items():
    songPool[index]["D"] += quizIds[ID]
    maxD = int(round(max(maxD, songPool[index]["D"])))
    minD = int(round(min(minD, songPool[index]["D"])))
    if quizSamples[ID] == 0:
        songPool[index]["sampleWeights"][0] += 1-(1+songPool[index]["X"])%3
    elif quizSamples[ID] == 100:
        songPool[index]["sampleWeights"][-1] += 1-(1+songPool[index]["X"])%3
    else:
        sectionCount = len(songPool[index]["sampleWeights"])-2
        songPool[index]["sampleWeights"][math.ceil(quizSamples[ID]*sectionCount/100)] += 1-(1+songPool[index]["X"])%3
    songPool[index]["X"] = 0

#Add new songs if appropriate
currentWeightCount = 0
songDistribution = [0]*(maxD-minD+1)
for song in songPool:
    songDistribution[int(round(song["D"]-minD))] += 1
    currentWeightCount += 2/(1+math.exp(song["D"]))
weightChange = prevWeightCount-currentWeightCount

targetGain = min(2, max(-2, (weightChange-prevGain)/(prevWeightCount-oldWeight)))
targetMean += targetGain

newSongCount = max(0,int(math.ceil((targetMean-currentWeightCount)/2)))

with open(gainFile, 'w', encoding = 'utf8') as f:
    f.truncate(0)
    f.seek(0)
    f.write(f"{targetMean}\n")
    f.write(f"{prevWeightCount}\n")
    f.write(f"{weightChange}\n")

if newSongCount > len(prepSongs):
    print("Warning: Insufficient New Songs")
    newSongCount = len(prepSongs)

songDistribution[-minD] += newSongCount
currentWeightCount += newSongCount

if len(practice)+newSongCount > 15:
    practice.sort(key = lambda x: x["D"])
    practice = practice[:15-newSongCount]

newSongs = []
if newSongCount > 0:
    newSongMalIds = set()
    newSongs = prepSongs[0:newSongCount]
    practice.extend(newSongs)
    songPool.extend(newSongs)
    prepSongs = prepSongs[newSongCount:]

    #progressiveNormal shuffling of prepsongs
    prepSongWeights = [(random.gauss(i, math.sqrt(i)), song) for i, song in enumerate(prepSongs)]
    prepSongWeights.sort(key = lambda x: x[0])
    prepSongs = [song for _, song in prepSongWeights]

    for song in newSongs:
        newSongMalIds.add(song["malId"])

    if random.randint(0,2)==0:
        random.shuffle(loadingSongs)
    elif random.randint(0,1) == 0:
        loadingSongs.sort(key = lambda x : (int(x["animeVintage"].split()[1]),{"Winter":1,"Spring":2,"Summer":3,"Fall":4}[x["animeVintage"].split()[0]],x["songDifficulty"]))
    if random.randint(0,2) == 0:
        loadingSongs.reverse()
    #replace added songs with songs from same show
    for i in range(len(loadingSongs)-1,-1,-1):
        if loadingSongs[i]["malId"] in newSongMalIds:
            newSongMalIds.remove(loadingSongs[i]["malId"])
            prepSongs.append(loadingSongs.pop(i))
            if len(newSongMalIds) == 0:
                break
    completedMalIds = set()
    for ID in newSongMalIds:
        completedMalIds.add(ID)

    #if a show had a final song, add a brand new show to replace it (assuming there aren't too many shows)
    if len(prepSongs) < prepListMinSize:
        newShowCount = prepListMinSize-len(prepSongs)
        for song in songPool:
            newSongMalIds.add(song["malId"])
        for i in range(len(loadingSongs)-1,-1,-1):
            if loadingSongs[i]["malId"] not in newSongMalIds:
                newSongMalIds.add(loadingSongs[i]["malId"])
                prepSongs.append(loadingSongs.pop(i))
                newShowCount -= 1
                if newShowCount <= 0:
                    break
        if newShowCount > 0:
            print("Warning: Insufficient Anime Diversity")

#Generate practice.json
with open(filePractice+".json", 'r+', encoding = 'utf8') as f:
    f.truncate(0)
    f.seek(0)
    json.dump(practice,f,ensure_ascii=False)
    f.seek(0)
    fileData = f.read()
    fileData = fileData.replace(", {","\n,{")
    fileData = fileData.replace("}]","}\n]")
    f.seek(0)
    f.write(fileData)

#Write updates to pool.json, prepList.json, loadingcutList.json
with open(filePool+".json", 'r+', encoding = 'utf8') as f:
    f.truncate(0)
    f.seek(0)
    json.dump(songPool,f,ensure_ascii=False)
    f.seek(0)
    fileData = f.read()
    fileData = fileData.replace(", {","\n,{")
    fileData = fileData.replace("}]","}\n]")
    f.seek(0)
    f.write(fileData)

with open(filePrep+".json", 'r+', encoding = 'utf8') as f:
    f.truncate(0)
    f.seek(0)
    prepSongs.insert(0, elementNull)
    json.dump(prepSongs,f,ensure_ascii=False)
    f.seek(0)
    fileData = f.read()
    fileData = fileData.replace(", {","\n,{")
    fileData = fileData.replace("}]","}\n]")
    f.seek(0)
    f.write(fileData)

with open(fileLoad+".json", 'r+', encoding = 'utf8') as f:
    f.truncate(0)
    f.seek(0)
    loadingSongs.sort(key = lambda x : x["songDifficulty"], reverse=True)
    json.dump(loadingSongs,f,ensure_ascii=False)
    f.seek(0)
    fileData = f.read()
    fileData = fileData.replace(", {","\n,{")
    fileData = fileData.replace("}]","}\n]")
    f.seek(0)
    f.write(fileData)

#Update list of added songs and completed shows
with open(fileAdd+".json", "r+", encoding="utf-8") as file:
    knownList = json.load(file)
    knownList.extend(newSongs)
    file.truncate(0)
    file.seek(0)
    json.dump(knownList,file,ensure_ascii=False)
    file.seek(0)
    fileData = file.read()
    fileData = fileData.replace(", {","\n,{")
    fileData = fileData.replace("}]","}\n]")
    file.seek(0)
    file.write(fileData)

if newSongCount > 0:
    with open(malUpdateFile, 'r+', encoding = 'utf8') as file:
            if file.tell() > 0:
                file.seek(file.tell()-1)
                if file.read(1) != "\n":
                    file.seek(0,2)
                    file.write("\n")
            file.seek(0,2)
            for ID in completedMalIds:
                file.write(f"{ID}\n")

#overwrite quiz to prevent accidentally forgetting to run quiz.py next time
with open(fileQuiz+".json", 'r+', encoding = 'utf8') as f:
    f.truncate(0)
    f.seek(0)
    json.dump([],f,ensure_ascii=False)

#Print sucess statement
print(f"\033[31mPractice List Compiled:\033[0m Missed = {missedCount}, PracticeSize = {len(practice)-newSongCount}+{newSongCount}, PoolSize = {len(songPool)}, LoadingSize = {len(loadingSongs)+len(prepSongs)}, Gain = {round(weightChange,3)}, CurrentWeight = {currentWeightCount} TargetWeight = {round(targetMean,3)}, TargetGain = {round(targetGain,3)}")
print("DValue distribution")
for index in range(len(songDistribution)):
    if index==-minD:
        print(f"\033[34m{songDistribution[index]}\033[0m", end = " ")
    elif (index+minD)%4==0:
        print(f"\033[31m{songDistribution[index]}\033[0m", end = " ")
    else:
        print(songDistribution[index], end = " ")
print()
for song in newSongs:
    print(f"Added ANSID={song["annSongId"]}: {song["songName"]}\n    from: {song["EN"]}")
