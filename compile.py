#TODO
#read quiz
#read play
#ensure that the right number of things from quiz got updated
#update things that need to be updated
#write missed songs to play.py

import json
import sys

'''
fileQuiz = "_quiz"
filePractice = "_practice"
filePool = "filePool"
'''
fileQuiz = "dummyQuiz"
filePractice = "dummyPractice"
filePool = "dummyPool"

#read files and create dict containing quiz songs and create practice list
with open(filePool+".json", 'r', encoding = 'utf8') as f:
    songPool = json.load(f)

quizIds = dict()
practice = []
with open(fileQuiz+".json", 'r', encoding = 'utf8') as f:
    quizSongs = json.load(f)
    for song in quizSongs:
        quizIds[song["ID"]] = 0
        if song["X"] == 2:
            practice.append(song)

#assume all songs must be accounted for unless user says otherwise. If user types a negative number, that indicates the number of skipped songs.
if len(sys.argv) > 1:
    argVal = int(sys.argv[1][1])
    if argVal < 0:
        argVal += len(quiz)
else:
    argVal = len(quiz)

#Run through list of quizSongs and check for songs which are marked for an update. 1 is a correct, 2 is a miss
extraIds = set()
idIndices = dict()
extraIndices = dict()
errorQ = 0
for i, song in enumerate(songPool):
    if song["X"] != 0:
        if song["ID"] in quizIds:
            quizIds[song["ID"]] = song["X"]
            idIndices[song["ID"]] = i
        elif song["X"] != 2:
            print("Extra Song was Incremented: ANNID="+song["ID"]+", "+song["SN"]+ " _from_ "+song["EN"])
            errorQ = 1
        else:
            extraIds.add(song["ID"])
            extraIndices[song["ID"]] = i
if errorQ:
    sys.exit(1)

#Ensure that the correct number of songs were accounted for
countedKeys = 0
countedTotalWeight = 0
ignoredKeys = set()
for song in quizSongs:
    if quizIds[song["ID"] != 0:
        countedKeys += 1
        countedTotalWeight += song["D"]
    else:
        ignoredKeys.add(song["ID"])

if countedKeys != argVal:
    print("Updated SongCount Error")
    print("Missing Keys:")
    print("_____________")
    for key in ignoredKeys:
        song = quizIds[idIndices[key]]
        print("ANNID="+song["ID"]+", "+song["SN"]+" _from_ "+song["EN"])
    print("\nExtra Keys:")
    print("___________")
    for key in extraIds:
        song = quizIds[extraIndices[key]]
        print("ANNID="+song["ID"]+", "+song["SN"]+" _from_ "+song["EN"])
    sys.exit(1)

#Update all keys and generate practice json
for ID, index in idIndices.items():
    songPool[index]["D"] += 3-2*quizIds[ID] #maps 1,2 to 1,-1
    if quizIds[ID] == 2:
for ID, index in extraIndices:
    quizSongs[index]["D"] = max(quizSongs[index]["D"], int(countedTotalWeight/countedKeys))

with open(fileQuiz+".json", 'r+', encoding = 'utf8') as f:
    f.truncate(0)
    f.seek(0)
    json.dump(quizSongs,f,ensure_ascii=False)
    f.seek(0)
    fileData = f.read()
    fileData = fileData.replace(", {","\n,{")
    fileData = fileData.replace("}]","}\n]")
    f.seek(0)
    f.write(fileData)

#Print sucess statement
print("Practice List Compiled without Issue")
