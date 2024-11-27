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
with open("preplist.json",'r', encoding='utf8') as f:
    data = json.load(f)
    for entry in data:
        includedSongs.add(entry["video720"])
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
globalSongTally = []
adjustedGlobalSongWeights = []

for file in lists:
    with open(str(file)+"cutlist.json", 'r', encoding = 'utf8') as f:
        data1 = json.load(f)
    traversedSongs = set()
    for song in data1:
        if song["video720"] is None or song["video720"] =="":
            song["video720"] = song["video480"]
        if song["video720"] in traversedSongs:
            globalSongTally[songListMap[song["video720"]]] += 1
            continue
        traversedSongs.add(song["video720"])
        if song["video720"] in songListMap:
            globalSongTally[songListMap[song["video720"]]] += 1
            globalSongWeights[songListMap[song["video720"]]] += 1
        else:
            songListMap[song["video720"]] = len(fullSongList)
            fullSongList.append(song)
            globalSongWeights.append(1)
            globalSongTally.append(1)
for i in range(len(globalSongWeights)):
    adjustedGlobalSongWeights.append(1)

#Weight all songs and mark hard songs for removal
hardSongSet = set()
hardSongList = []
lostCount = 0
for i in range(len(globalSongWeights)):
    if globalSongTally[i]-globalSongWeights[i] > 8:
        adjustedGlobalSongWeights[i] = 0
        hardSongSet.add(fullSongList[i]["video720"])
        hardSongList.append(fullSongList[i])
        lostCount += globalSongTally[i]

#add new songs if the current number of songs is less than a specified average.
with open("learnedcutlist.json", 'r', encoding = 'utf8') as f:
    data1 = json.load(f)
    learnedSize = len(data1)
songMultiplier = 2
globalMean = (sum(globalSongTally)-lostCount-learnedSize)/len(lists1)
minMean = 527
if globalMean < minMean:
    newCount = math.ceil(minMean-globalMean)
    with open("loadingcutlist.json", 'r', encoding = 'utf8') as f:
        newPrep = json.load(f)
    with open("preplist.json", 'r+', encoding = 'utf8') as f:
        prepData = json.load(f)

        newCount = min(newCount,len(prepData))
        newSongs = prepData[:newCount]
        for i in range(newCount):
            songListMap[newSongs[i]["video720"]] = len(fullSongList)+i
        fullSongList.extend(newSongs)
        adjustedGlobalSongWeights.extend([len(lists1)+songMultiplier]*newCount)
        globalSongTally.extend([len(lists1)]*newCount)
        globalSongWeights.extend([len(lists1)]*newCount)

        prepData = prepData[newCount:]
        newPrep = random.sample(newPrep,min(len(newPrep),newCount))
        prepData.extend(newPrep)

        f.truncate(0)
        f.seek(0)
        json.dump(prepData,f,ensure_ascii=False)
        f.seek(0)
        fileData = f.read()
        fileData = fileData.replace(", {","\n,{")
        fileData = fileData.replace("}]","}\n]")
        f.seek(0)
        f.write(fileData)
    for section in lists1:
        with open(str(section)+"cutlist.json", 'r+', encoding = 'utf8') as f:
            songList = json.load(f)
            songList.extend(newSongs)
            random.shuffle(songList)
            f.truncate(0)
            f.seek(0)
            json.dump(songList,f,ensure_ascii=False)
            f.seek(0)
            fileData = f.read()
            fileData = fileData.replace(", {","\n,{")
            fileData = fileData.replace("}]","}\n]")
            f.seek(0)
            f.write(fileData)
    print("Songs added to pool:________________________________")
    for song in newSongs:
        print(song["animeEnglishName"]+": "+song["songName"]+" by "+song["songArtist"])
    print()

#Pick the practice list and get song statistics
zScores = []
for file in lists1:
    with open(str(file)+"cutlist.json", 'r', encoding = 'utf8') as f:
        data1 = json.load(f)
        zScores.append(len(data1))
songmean = statistics.mean(zScores)
songmax = max(zScores)
songmin = min(zScores)
songtotal = sum(zScores)
songCountList = []
for score in zScores:
    songCountList.append(score)
stdev = statistics.pstdev(zScores)
for i in range(len(zScores)):
    zScores[i] = (zScores[i]-songmean)/stdev
targetWeights = []
for score in zScores:
    targetWeights.append(math.exp(score))
r = random.choices(range(len(lists1)), weights = targetWeights)[0]
'r = random.choices(range(len(lists1)))[0]'

#Create modify the song frequency based on picked list
localSongList = set()
localSongCount = 0
with open(str(lists1[r])+"cutlist.json", 'r', encoding = 'utf8') as f:
    data1 = json.load(f)
for song in data1:
    if song["video720"] is None:
        song["video720"] = song["video480"]
    adjustedGlobalSongWeights[songListMap[song["video720"]]] *= songMultiplier
    localSongList.add(song["video720"])
    localSongCount += 1

#create random song selection for the selected list
practicesonglist = []
for i in range(len(globalSongWeights)):
    if adjustedGlobalSongWeights[i] == 0:
        continue
    adjustedGlobalSongWeights[i] += max(globalSongWeights[i], globalSongTally[i]-globalSongWeights[i])
    adjustedGlobalSongWeights[i] = math.pow(2,adjustedGlobalSongWeights[i])
totalWeight = sum(adjustedGlobalSongWeights)
for i in range(len(adjustedGlobalSongWeights)):
    adjustedGlobalSongWeights[i] /= totalWeight
#songCount = int(math.sqrt(len(localSongList)))
songCount = min(30,len(localSongList))
practicesonglist = numpy.append(practicesonglist, numpy.random.choice(fullSongList, size = songCount, p = adjustedGlobalSongWeights, replace = False))

#remove hard songs from lists (if applicable)
if len(hardSongSet) > 0:
    for section in lists1:
        filteredFile = []
        with open(str(section)+"cutlist.json", 'r+', encoding = 'utf8') as f:
            unfilteredFile = json.load(f)
            for song in unfilteredFile:
                if song["video720"] not in hardSongSet:
                    filteredFile.append(song)
            f.truncate(0)
            f.seek(0)
            json.dump(filteredFile,f,ensure_ascii=False)
            f.seek(0)
            fileData = f.read()
            fileData = fileData.replace(", {","\n,{")
            fileData = fileData.replace("}]","}\n]")
            f.seek(0)
            f.write(fileData)
    with open("preplist.json", 'r+', encoding = 'utf8') as f:
        prepdata = json.load(f)
        prepdata.extend(hardSongList)
        f.truncate(0)
        f.seek(0)
        json.dump(prepdata,f,ensure_ascii=False)
        f.seek(0)
        fileData = f.read()
        fileData = fileData.replace(", {","\n,{")
        fileData = fileData.replace("}]","}\n]")
        f.seek(0)
        f.write(fileData)
    print("Songs returned to preplist:________________________________")
    for song in hardSongList:
        print(song["animeEnglishName"]+": "+song["songName"]+" by "+song["songArtist"])
    print()

    

#write to _quiz.json
with open("_quiz.json", 'w', encoding = 'utf8') as f:
    json.dump(practicesonglist.tolist(), f)

#clear practice list
with open("_practice.json", 'w', encoding = 'utf8') as f:
    f.write("[{}\n]")

#print the practice list and song statistics
print("Test "+str(lists[r])+" section\nMeanCount: "+str(round((sum(globalSongTally)-lostCount-learnedSize)/len(lists1),5))+" LocalCount: "+str(localSongCount)+" PoolSize: "+str(len(fullSongList)-learnedSize)+" SongMin: "+str(songmin)+" SongMax: "+str(songmax))

frequencyList = [0]*len(filelist)
for element in globalSongWeights:
    frequencyList[element] += 1
frequencyList[0] = learnedSize
frequencyList[1] -= learnedSize
print("songFrequencyDistribution: "+str(frequencyList))
print("songCountDistribution: "+str(songCountList))
targetWeightSum = sum(targetWeights)
for i in range(len(targetWeights)):
    targetWeights[i]/=targetWeightSum
    targetWeights[i] = round(targetWeights[i],5)
print("listWeights: "+str(targetWeights))
weightedCount = 0
for i in range(len(frequencyList)):
    weightedCount += i*frequencyList[i]
print("Mean lists per song: "+str(weightedCount/len(globalSongWeights)))
