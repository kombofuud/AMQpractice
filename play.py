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

#count song frequency
fullSongList = [] #doesn't include learned and loading songs
songListMap = dict()
globalSongWeights = []
adjustedGlobalSongWeights = []
zScores = []

for file in lists:
    with open(str(file)+"cutlist.json", 'r', encoding = 'utf8') as f:
        data1 = json.load(f)
    traversedSongs = set()
    zScores.append(0)
    for song in data1:
        zScores[-1] += 1
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
    adjustedGlobalSongWeights.append(1)

#Pick the practice list and get song statistics
learnedSize = zScores.pop()
songmean = statistics.mean(zScores)
songmax = max(zScores)
songmin = min(zScores)
songtotal = sum(zScores)
stdev = statistics.pstdev(zScores)
for i in range(len(zScores)):
    zScores[i] = (zScores[i]-songmean)/stdev
targetWeights = []
for score in zScores:
    targetWeights.append(math.exp(score))
r = random.choices(range(len(lists1)), weights = targetWeights)[0]

#Create modify the song frequency based on picked list
localSongList = set()
with open(str(lists1[r])+"cutlist.json", 'r', encoding = 'utf8') as f:
    data1 = json.load(f)
for song in data1:
    if song["video720"] is None:
        song["video720"] = song["video480"]
    adjustedGlobalSongWeights[songListMap[song["video720"]]] += 1
    localSongList.add(song["video720"])

#Weight all songs
for i in range(len(globalSongWeights)):
    adjustedGlobalSongWeights[i] *= globalSongWeights[i]
    adjustedGlobalSongWeights[i] = math.exp(math.sqrt(adjustedGlobalSongWeights[i])-1)
totalWeight = sum(adjustedGlobalSongWeights)
for i in range(len(adjustedGlobalSongWeights)):
    adjustedGlobalSongWeights[i] /= totalWeight

#create random song selection for the selected list
practicesonglist = []
songCount = int(math.sqrt(len(localSongList)))
practicesonglist = numpy.append(practicesonglist, numpy.random.choice(fullSongList, size = songCount, p = adjustedGlobalSongWeights, replace = False))

#write to _quiz.json
with open("_quiz.json", 'w', encoding = 'utf8') as f:
    json.dump(practicesonglist.tolist(), f)

#clear practice list
with open("_practice.json", 'w', encoding = 'utf8') as f:
    f.write("]")

#print the practice list and song statistics
print("Test "+str(lists[r])+" section\nMeanCount: "+str(int(sum(globalSongWeights)/len(lists1)))+" LocalCount: "+str(len(localSongList))+" PoolSize: "+str(len(fullSongList)-learnedSize)+" Learned: "+str(learnedSize))
