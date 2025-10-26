import json
import sys
import math
import copy
import random

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
rngFile = "addSongRandomValue.txt"
malUpdateFile = "updateMal.txt"
prevMalUpdateFile = "prevUpdateMal.txt"
dMax = 8
prepListMinSize = 100
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
with open(fileQuiz+".json", 'r', encoding = 'utf8') as f:
    quizSongs = json.load(f)
    for song in quizSongs:
        quizIds[song["ID"]] = 0
        quizSamples[song["ID"]] = song["startPoint"]

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
if len(quizSongs) == 0:
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
    print("Pool+Quiz+Prep+Load+Update+AddedOrder Restored")
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
diff8Q = 0
missedCount = 0
for i, song in enumerate(songPool):
    if song["ID"] in quizIds or song["D"] == dMax:
        if song["ID"] in quizIds:
            idIndices[song["ID"]] = i
            if song["X"] == 1:
                quizIds[song["ID"]] = -1
            elif song["X"] == 2:
                quizIds[song["ID"]] = 1.5
                missedCount += 1
        if song["ID"] not in quizIds or quizIds[song["ID"]]+song["D"] >= dMax:
            diff8Q += 1
            pSong = copy.deepcopy(song)
            sectionCount = len(pSong["sampleWeights"])
            #songWeightStrength = 1-math.pow(0.95,dMax-pSong["D"])
            songWeightStrength = 0.5
            for i in range(len(pSong["sampleWeights"])-1):
                pSong["sampleWeights"][i+1] += song["sampleWeights"][i]/2
                pSong["sampleWeights"][i] += song["sampleWeights"][i+1]/2
            for i in range(len(pSong["sampleWeights"])):
                pSong["sampleWeights"][i] = math.pow(len(pSong["sampleWeights"]),pSong["sampleWeights"][i]*songWeightStrength)
            pSong["startPoint"] = pSong["sampleWeights"]
            pSong["sampleWeights"] = song["sampleWeights"]
            pSong["D"] = 8
            pSong["X"] = 2
            practice.append(pSong)
    elif song["X"] != 0:
        errorQ = 1
        extraIds.add(song["ID"])
        extraIndices[song["ID"]] = i

#Ensure that the correct number of songs were accounted for
countedKeys = 0
countedTotalWeight = 0
ignoredKeys = set()
for song in quizSongs:
    if songPool[idIndices[song["ID"]]]["X"] != 0:
        countedKeys += 1
        countedTotalWeight += song["D"]
    else:
        ignoredKeys.add(song["ID"])

if countedKeys < argVal:
    print("Insufficient songs updated: "+str(countedKeys)+"/"+str(argVal))
    print("Missing Keys:")
    print("_____________\n")
    for key in ignoredKeys:
        song = songPool[idIndices[key]]
        print("ANNID="+str(song["ID"])+", "+song["SN"]+" _from_ "+song["EN"])
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


#save copy of pool,quiz,prep,loading to prevPool,prevQuiz etc
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

#Update all keys
print("Missed Songs_______")
for ID, index in idIndices.items():
    if quizIds[ID] > 0:
        print(f"{songPool[index]["SN"]} __from__ {songPool[index]["EN"]}")
    if songPool[index]["D"] == dMax and quizIds[ID] > 0:
        songPool[index]["D"] = dMax
        songPool[index]["X"] = 0
        continue
    songPool[index]["D"] += quizIds[ID]
    songPool[index]["D"] = min(songPool[index]["D"],dMax)
    if quizSamples[ID] == 0:
        songPool[index]["sampleWeights"][0] += 1-(1+songPool[index]["X"])%3
    elif quizSamples[ID] == 100:
        songPool[index]["sampleWeights"][-1] += 1-(1+songPool[index]["X"])%3
    else:
        sectionCount = len(songPool[index]["sampleWeights"])-2
        songPool[index]["sampleWeights"][math.ceil(quizSamples[ID]*sectionCount/100)] += 1-(1+songPool[index]["X"])%3
    songPool[index]["X"] = 0

#Add new songs if appropriate
with open(rngFile, 'r', encoding = 'utf8') as f:
    randomValue = float(f.read().strip())
if randomValue < 0:
    randomValue = random.random()
    with open(rngFile, 'w', encoding = 'utf8') as f:
        f.write(str(randomValue))

newSongCount = max(10-diff8Q,0)
newSongs = []
if newSongCount > len(prepSongs):
    print("Warning: Insufficient New Songs")
    newSongCount = len(prepSongs)

if newSongCount > 0:
    newSongMalIds = set()
    newSongs = prepSongs[0:newSongCount]
    practice.extend(newSongs)
    songPool.extend(newSongs)
    prepSongs = prepSongs[newSongCount:]
    random.shuffle(prepSongs)
    for song in newSongs:
        newSongMalIds.add(song["malId"])

    if random.randint(0,2)==0:
        random.shuffle(loadingSongs)
    elif random.randint(0,1) == 0:
        loadingSongs.sort(key = lambda x : (int(x["animeVintage"].split()[1]),{"Winter":1,"Spring":2,"Summer":3,"Fall":4}[x["animeVintage"].split()[0]],x["songDifficulty"]))
    if random.randint(0,1) == 0:
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
        newShowCount = 100-len(prepSongs)
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
    loadingSongs.sort(key = lambda x : x["songDifficulty"])
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
            file.seek(0,2)
            for ID in completedMalIds:
                file.write(f"\n{ID}")

#overwrite quiz to prevent accidentally forgetting to run quiz.py next time
with open(fileQuiz+".json", 'r+', encoding = 'utf8') as f:
    f.truncate(0)
    f.seek(0)
    json.dump([],f,ensure_ascii=False)

#Print sucess statement
print("\033[31mPractice List Compiled:\033[0m Missed = "+str(missedCount)+", PracticeSize = "+str(len(practice)-newSongCount)+"+"+str(newSongCount)+", PoolSize = "+str(len(songPool))+", LoadingSize = "+str(len(loadingSongs)+len(prepSongs)))
for song in newSongs:
    print(f"Added ANSID={song["annSongId"]}: {song["songName"]}\n    from: {song["EN"]}")
