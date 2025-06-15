import json
import sys
import math
import copy

fileQuiz = "_quiz"
filePractice = "_practice"
filePool = "pool"
filePrevPool = "prevPool"
'''
fileQuiz = "dummyQuiz"
filePractice = "dummyPractice"
filePool = "dummyPool"
filePrevPool = "dummyPrevPool"
'''

#read files and create dict containing quiz songs and create practice list
with open(filePool+".json", 'r', encoding = 'utf8') as f:
    songPool = json.load(f)

quizIds = dict()
quizSamples = dict()
with open(fileQuiz+".json", 'r', encoding = 'utf8') as f:
    quizSongs = json.load(f)
    for song in quizSongs:
        quizIds[song["ID"]] = 0
        quizSamples[song["ID"]] = song["startPoint"]

#assume all songs must be accounted for unless user says otherwise. If user types a negative number, that indicates the number of skipped songs.
if len(sys.argv) > 1:
    argVal = int(sys.argv[1])
    if argVal < 0:
        argVal += len(quizSongs)
else:
    argVal = len(quizSongs)

#if argument is 0, reset the pool list to before the update
if argVal == 0 and len(quizSongs) > 0:
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
    print("Pool Restored")
    sys.exit(0)

#Run through list of quizSongs and check for songs which are marked for an update. 1 is a correct, 2 is a miss
extraIds = set()
idIndices = dict()
extraIndices = dict()
practice = []
errorQ = 0
for i, song in enumerate(songPool):
    if song["X"] != 0 or song["ID"] in quizIds:
        #alter amount added to songId. 1 -> -1, 2 -> ???
        if song["ID"] in quizIds:
            idIndices[song["ID"]] = i
            if song["X"] == 1:
                quizIds[song["ID"]] = -1
            elif song["X"] == 2:
                quizIds[song["ID"]] = 3-int(song["D"]/6) #increase penalty the more you know the song
                pSong = copy.deepcopy(song)
                sectionCount = len(pSong["sampleWeights"])-2
                pSong["sampleWeights"][math.ceil(quizSamples[pSong["ID"]]*sectionCount/100*1.0000001)] += quizIds[pSong["ID"]]
                if song["D"] < 7:
                    pSong["startPoint"] = quizSamples[song["ID"]]
                else:
                    pSong["startPoint"] = song["sampleWeights"]
                practice.append(pSong)
            elif song["X"] != 0:
                print(f"QuizSong Status Val Undefined: ANNID={song["ID"]}, {song["SN"]} _from_ {song["EN"]}")
                errorQ = 1
        else:
            #print(f"\033[31mExtra Song\033[0m was Incremented: ANNID={song["ID"]}, {song["SN"]} _from_ {song["EN"]}")
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
    print("_____________")
    for key in ignoredKeys:
        song = songPool[idIndices[key]]
        print("ANNID="+str(song["ID"])+", "+song["SN"]+" _from_ "+song["EN"])
    print("\nExtra Keys:")
    print("___________")
    for key in extraIds:
        song = songPool[extraIndices[key]]
        print("ANNID="+str(song["ID"])+", "+song["SN"]+" _from_ "+song["EN"])
    errorQ = 1
if countedKeys > argVal:
    print("More updates than expected."+str(countedKeys)+"/"+str(argVal))
    for key,update in quizIds.items():
        if update != 0:
            song = songPool[key]
            print("ANNID="+str(song["ID"])+", "+song["SN"]+" _from_ "+song["EN"])
    errorQ = 1
if errorQ:
    sys.exit(1)

#save copy of pool to prevPool.json
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

#Update all keys and generate practice json
for ID, index in idIndices.items():
    if songPool[index]["D"] >= 18 and quizIds[ID] >= 0:
        songPool[index]["X"] = 0
        continue
    songPool[index]["D"] += quizIds[ID] 
    if quizSamples[ID] == 0:
        songPool[index]["sampleWeights"][0] += 1-(1+songPool[index]["X"])%3
    elif quizSamples[ID] == 100:
        songPool[index]["sampleWeights"][-1] += 1-(1+songPool[index]["X"])%3
    else:
        sectionCount = len(songPool[index]["sampleWeights"])-2
        songPool[index]["sampleWeights"][math.ceil(quizSamples[ID]*sectionCount/100)] += 1-(1+songPool[index]["X"])%3
    songPool[index]["X"] = 0
for ID, index in extraIndices.items():
    songPool[index]["D"] = max(songPool[index]["D"], int(countedTotalWeight/countedKeys))
    songPool[index]["X"] = 0

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


#Print sucess statement
print("Practice List Compiled: Len = "+str(len(practice)))
