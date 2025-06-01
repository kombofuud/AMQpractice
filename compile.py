import json
import sys
import math

fileQuiz = "_quiz"
filePractice = "_practice"
filePool = "pool"
'''
fileQuiz = "dummyQuiz"
filePractice = "dummyPractice"
filePool = "dummyPool"
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
                song["startPoint"] = quizSamples[song["ID"]]
                practice.append(song)
            elif song["X"] != 0:
                print(f"QuizSong Status Val Undefined: ANNID={song["ID"]}, {song["SN"]} _from_ {song["EN"]}")
                errorQ = 1
        elif song["X"] != 2:
            print(f"Extra Song was Incremented: ANNID={song["ID"]}, {song["SN"]} _from_ {song["EN"]}")
            errorQ = 1
        else:
            extraIds.add(song["ID"])
            extraIndices[song["ID"]] = i

#Ensure that the correct number of songs were accounted for
countedKeys = 0
countedTotalWeight = 0
ignoredKeys = set()
for song in quizSongs:
    if quizIds[song["ID"]] != 0:
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
if errorQ:
    sys.exit(1)

#Update all keys and generate practice json
for ID, index in idIndices.items():
    songPool[index]["D"] += quizIds[ID] 
    if quizSamples[ID] == 0:
        songPool[index]["sampleWeights"][0] += 1-(1+songPool[index]["X"])%3
    if quizSamples[ID] == 100:
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
