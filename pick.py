import random
import math
import statistics
import json
import fileinput
import copy
import numpy

#updating learnedcutlist.json
filelist = [0,10,20,30,40,50,60,70,80,90,100,"last","loading"]
includedSongs = set()

# read songs from files and add them to a set (also count number of unique songs)
uniqueSongCount = 0
for filename in filelist:
    with open(str(filename)+"cutlist.json",'r', encoding='utf8') as f:
        data = json.load(f)
        for entry in data:
            includedSongs.add(entry["video720"])
            if filename == "loading":
                uniqueSongCount += 1
uniqueSongCount = len(includedSongs)-uniqueSongCount

#read list of all songs
with open("merged.json",'r', encoding = 'utf8') as f:
    allSongs = json.load(f)

#put learnedcut songs in a list
learnedcutSongs = []
for entry in allSongs:
    if entry["video720"] not in includedSongs:
        learnedcutSongs.append(entry)

#write data to json file
with open("learnedcutlist.json", 'w', encoding = 'utf8') as f:
    json.dump(learnedcutSongs, f)

#correct formatting
with open("learnedcutlist.json", 'r', encoding = 'utf8') as f:
    filedata = f.read()
filedata = filedata.replace(", {","\n,{")
filedata = filedata.replace("}]","}\n]")
with open("learnedcutlist.json", 'w', encoding = 'utf8') as f:
    f.write(filedata)

#getting statistics about the lists
lists = [0,10,20,30,40,50,60,70,80,90,100,'last','learned']
lists1 = [0,10,20,30,40,50,60,70,80,90,100,'last']
weightl = []
rweightl = []
index = -1
for file in lists:
  with open((str(file)+"cutlist.json"),'r', encoding = 'utf-8') as f:
    weightl.append(1)
    rweightl.append(len(f.readlines())-1)
  f.close()
zScores = copy.deepcopy(rweightl)
zScores.pop()
songmean = statistics.mean(zScores)
songmax = max(zScores)
songmin = min(zScores)
songtotal = sum(zScores)
stdev = statistics.pstdev(zScores)
learnedSize = rweightl[-1]
for i in range(len(zScores)):
    zScores[i] = (zScores[i]-songmean)/stdev

#selecting the target list
rweightl[-1] = min(songmean, rweightl[-1])
targetWeights = []
for score in zScores:
    targetWeights.append(math.exp(score))

r = random.choices(range(len(lists1)), weights = targetWeights)[0]

#create list of songs and their weights
fullSongList = [] #doesn't include learned and loading songs
songListMap = dict()
globalSongWeights = []
adjustedGlobalSongWeights = []

for file in lists1:
    with open(str(file)+"cutlist.json", 'r', encoding = 'utf8') as f:
        data1 = json.load(f)
    traversedSongs = set()
    for song in data1:
        if song["video720"] in traversedSongs:
            continue
        if song["video720"] is None:
            song["video720"] = song["video480"]
        traversedSongs.add(song["video720"])
        if song["video720"] in songListMap:
            globalSongWeights[songListMap[song["video720"]]] += 1
        else:
            songListMap[song["video720"]] = len(fullSongList)
            fullSongList.append(song)
            globalSongWeights.append(1)
for i in range(len(globalSongWeights)):
    adjustedGlobalSongWeights.append(pow(2,globalSongWeights[i]))
temp = sum(adjustedGlobalSongWeights)
for i in range(len(adjustedGlobalSongWeights)):
    adjustedGlobalSongWeights[i] /= temp


localSongList = []
localSongListMap = dict()
localSongWeights = []

with open(str(lists1[r])+"cutlist.json", 'r', encoding = 'utf8') as f:
    data1 = json.load(f)
for song in data1:
    if song["video720"] is None:
        song["video720"] = song["video480"]
    if song["video720"] in localSongListMap:
        localSongWeights[localSongListMap[song["video720"]]] *= 2
    else:
        localSongListMap[song["video720"]] = len(localSongList)
        localSongList.append(song)
        localSongWeights.append(1)
temp = sum(localSongWeights)
for i in range(len(localSongWeights)):
    localSongWeights[i] /= temp

#create random song selection from selected list
practicesonglist = []
songCount = int(math.sqrt(len(localSongList)))

learnedSongCount = int(((songCount-1)/20)+1)
learnedSongCount = min(learnedSongCount, learnedSize)
with open("learnedcutlist.json", 'r', encoding = 'utf8') as f:
    data1 = json.load(f)
practicesonglist = numpy.random.choice(learnedcutSongs, size = learnedSongCount, replace = False)

quizSongCount = int(((songCount-1)*3/5)+1)
quizSongCount = min(quizSongCount, len(fullSongList))
practicesonglist = numpy.append(practicesonglist, numpy.random.choice(fullSongList, size = quizSongCount, p = adjustedGlobalSongWeights, replace = False))

practiceSongCount = int(((songCount-1)*2/5)+1)
pickedSongs = set()
for song in practicesonglist:
    if song["video720"] is None:
        song["video720"] = song["video480"]
    pickedSongs.add(song["video720"])
practiceSongSelector = numpy.random.choice(localSongList, size = len(localSongList), p = localSongWeights, replace = False)
iterator = 0
practiceRunningTotal = 0
while iterator < len(practiceSongSelector) and practiceRunningTotal < practiceSongCount:
    if practiceSongSelector[iterator]["video720"] is None:
        practiceSongSelector[iterator]["video720"] = practiceSongSelector[iterator]["video480"]
    if practiceSongSelector[iterator]["video720"] not in pickedSongs:
        practicesonglist = numpy.append(practicesonglist, [practiceSongSelector[iterator]])
        practiceRunningTotal += 1
    iterator += 1

#write to _quiz.json
with open("_quiz.json", 'w', encoding = 'utf8') as f:
    json.dump(practicesonglist.tolist(), f)
#clear practice list
with open("_practice.json", 'w', encoding = 'utf8') as f:
    f.write("]")
#print out the randomized practice stataistics
print("Test the "+str(lists[r])+" section which has "+str(rweightl[r]+1)+" songs.\nMean: "+str(int(sum(globalSongWeights)/len(lists1)))+" Locally_Unique: "+str(len(localSongList))+" Total: "+str(songtotal)+" Unique: "+str(uniqueSongCount)+" Learned: "+str(learnedSize))
