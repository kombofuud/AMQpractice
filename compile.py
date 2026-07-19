import json
import sys
import math
import copy
import random
import numpy
import shutil

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
    shutil.copyfile(filePrevPool+".json", filePool+".json")
    shutil.copyfile(filePrevQuiz+".json", fileQuiz+".json")
    shutil.copyfile(filePrevPrep+".json", filePrep+".json")
    shutil.copyfile(filePrevLoad+".json", fileLoad+".json")
    shutil.copyfile(prevMalUpdateFile, malUpdateFile)
    shutil.copyfile(filePrevAdd+".json", fileAdd+".json")
    shutil.copyfile(prevGainFile, gainFile)
    print("Pool+Quiz+Prep+Load+Update+AddedOrder+fileGains Restored")
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
    prevWeightCount += 1/(1+(2**song["D"]-1)/(100+2**song["D"])*2**(song["D"]+1))
    song["SN"] = f"`{song["songName"]}`"
    if song["D"] == 0 and type(song["D"]) is int:
        prevNewSongs += 1
    if song["ID"] in quizIds:
        idIndices[song["ID"]] = i
        if song["X"] == 1:
            quizIds[song["ID"]] = 1.0
        elif song["X"] == 2:
            quizIds[song["ID"]] = -1.125
            missedCount += 1
        if quizIds[song["ID"]] + song["D"] <= 0:
        #if quizIds[song["ID"]] <= 0 and quizIds[song["ID"]]+song["D"] < 0:
            pSong = copy.deepcopy(song)
            pSong["startPoint"] = quizSamples[pSong["ID"]]
            if pSong["startPoint"] == 0:
                pSong["sampleWeights"][0] += (1+pSong["X"])%3-1
            elif pSong["startPoint"] == 100:
                pSong["sampleWeights"][-1] += (1+pSong["X"])%3-1
            else:
                sectionCount = len(pSong["sampleWeights"])-2
                pSong["sampleWeights"][math.ceil(pSong["startPoint"]*sectionCount/100)] += (1+pSong["X"])%3-1
            #songWeightStrength = 1-math.pow(0.95,pSong["D"])
            '''for i in range(len(pSong["sampleWeights"])-1):
                pSong["sampleWeights"][i+1] += song["sampleWeights"][i]/3
                pSong["sampleWeights"][i] += song["sampleWeights"][i+1]/3'''
            for i in range(len(pSong["sampleWeights"])):
                pSong["sampleWeights"][i] = math.pow(math.e,-pSong["sampleWeights"][i])
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
        maxD = int(math.ceil(max(maxD, song["D"])))
        minD = int(math.ceil(min(minD, song["D"])))

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
shutil.copyfile(filePool+".json", filePrevPool+".json")
shutil.copyfile(fileQuiz+".json", filePrevQuiz+".json")
shutil.copyfile(filePrep+".json", filePrevPrep+".json")
shutil.copyfile(fileLoad+".json", filePrevLoad+".json")
shutil.copyfile(malUpdateFile, prevMalUpdateFile)
shutil.copyfile(fileAdd+".json", filePrevAdd+".json")
shutil.copyfile(gainFile, prevGainFile)

#Print list of missed songs
print("Missed Song Numbers_______")
for i, song in enumerate(quizSongs):
#   if quizIds[song["ID"]] < 0.0:
    if songPool[idIndices[song["ID"]]]["X"] == 2:
        print(f"{i+1}", end = ' ')
print()

#Subtract 1 from all the countdowns
for song in songPool:
    if song["ID"] not in quizIds:
        countdown = song["CountDown"]
        countdown = ((countdown << 3 ) | (countdown >> 29)) & 0xFFFFFFFF
        countdown ^= song["annSongId"]
        countdown &= 0xFFFFFFFF
        countdown -= 1
        countdown ^= song["annSongId"]
        countdown &= 0xFFFFFFFF
        countdown = ((countdown >> 3) | (countdown << 29)) & 0xFFFFFFFF
        song["CountDown"] = countdown

#Update all keys
for ID, index in idIndices.items():
    songPool[index]["D"] += quizIds[ID]
    maxD = int(math.ceil(max(maxD, songPool[index]["D"])))
    minD = int(math.ceil(min(minD, songPool[index]["D"])))
    if quizSamples[ID] == 0:
        songPool[index]["sampleWeights"][0] += (1+songPool[index]["X"])%3-1
        songPool[index]["sampleWeights"][0] = max(0,songPool[index]["sampleWeights"][0])
    elif quizSamples[ID] == 100:
        songPool[index]["sampleWeights"][-1] += (1+songPool[index]["X"])%3-1
        songPool[index]["sampleWeights"][-1] = max(0,songPool[index]["sampleWeights"][-1])
    else:
        sectionCount = len(songPool[index]["sampleWeights"])-2
        songPool[index]["sampleWeights"][math.ceil(quizSamples[ID]*sectionCount/100)] += (1+songPool[index]["X"])%3-1
        songPool[index]["sampleWeights"][math.ceil(quizSamples[ID]*sectionCount/100)] = max(0,songPool[index]["sampleWeights"][math.ceil(quizSamples[ID]*sectionCount/100)])
    countdown = int(random.random()+((2**songPool[index]["D"]-1)/(100+2**songPool[index]["D"]))*(2**songPool[index]["D"]))+random.binomialvariate(int(random.random()+((2**songPool[index]["D"]-1)/(100+2**songPool[index]["D"]))*(2**(songPool[index]["D"]+1))),0.5)
    if quizIds[ID] == 0:
        countdown //= 4
    countdown ^= songPool[index]["annSongId"]
    countdown &= 0xFFFFFFFF
    countdown = (countdown >> 3) | (countdown << 29)
    songPool[index]["CountDown"] = countdown & 0xFFFFFFFF
    songPool[index]["X"] = 0

#Add new songs if appropriate
currentWeightCount = 0
phantomWeightCount = 0
songDistribution = [0]*(maxD-minD+1)
for song in songPool:
    songDistribution[int(math.ceil(song["D"]-minD))] += 1
    phantomWeightCount += 1/(1+(2**song["D"]-1)/(100+2**song["D"])*2**(song["D"]+1))
    song["D"] = max(song["D"], 0.0)
    currentWeightCount += 1/(1+(2**song["D"]-1)/(100+2**song["D"])*2**(song["D"]+1))

with open(gainFile, 'r', encoding = 'utf8') as f:
    targetMean, oldWeight, prevGain = [float(line.strip()) for line in f.readlines()]
weightChange = prevWeightCount-currentWeightCount

#targetGain = min(2, max(-2, (weightChange-prevGain)/(prevWeightCount-oldWeight)/20))
targetGain = 0
targetMean += targetGain

newSongCount = max(0,int(math.floor(41-currentWeightCount)))

with open(gainFile, 'w', encoding = 'utf8') as f:
    f.truncate(0)
    f.seek(0)
    f.write(f"{targetMean}\n")
    f.write(f"{currentWeightCount+newSongCount if newSongCount > 0 else min(currentWeightCount, oldWeight)}\n")
    f.write(f"{weightChange}\n")

if newSongCount > len(prepSongs):
    print("Warning: Insufficient New Songs")
    newSongCount = len(prepSongs)

songDistribution[-minD] += newSongCount
currentWeightCount += newSongCount

#practice.sort(key = lambda x: x["D"])
random.shuffle(practice)
'''if len(practice)+newSongCount > 10:
    practice = practice[:10-newSongCount]'''

newSongs = []
if newSongCount > 0:
    newSongMalIds = set()
    newSongs = prepSongs[0:newSongCount]
    for song in newSongs:
        countdown = song["annSongId"] & 0xFFFFFFFF
        song["CountDown"] = ((countdown >> 3) | (countdown << 29)) & 0xFFFFFFFF
    practice = newSongs+practice
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
print(f"\033[31mPractice List Compiled:\033[0m Missed = {missedCount}, PracticeSize = {len(practice)-newSongCount}+{newSongCount}, PoolSize = {len(songPool)}, LoadingSize = {len(loadingSongs)+len(prepSongs)}, Gain = {round(weightChange,3)}, CurrentWeight = {round(currentWeightCount,5)}")
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
