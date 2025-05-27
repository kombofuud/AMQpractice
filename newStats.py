#songs in pool
#songs in prep/loading
#average song progress
#instance frequencies
#rewrites learnedlist

#add ability to query a specific id or specific "learned level"
#adapt to read pool rather than fileList

import json
import sys

if len(sys.argv) > 1:
    argVal = int(sys.argv[1][1])
else:
    argVal = None

'''
filePool = "filePool"
filePrep = "preplist.json"
fileLoad = "loadingcutlist.json"
fileQuiz = "_quiz"
filePractice = "practice"
'''
filePool = "dummyPool"
fileLoad = "dummyLoad"
filePrep = "dummyPreplist"
fileQuiz = "dummyQuiz"
filePractice = "dummyPractice"

#getting list sizes
with open(filePool+".json", 'r', encoding = 'utf8') as f:
    localList = json.load(f)
poolSize = len(localList)

with open(fileLoad, 'r', encoding = 'utf8') as f:
    localList = json.load(f)
loadingSize = len(localList)

with open(filePrep, 'r', encoding = 'utf8') as f:
    localList = json.load(f)
loadingSize += len(localList)

#get list statistics
listDistribution = []
progressCounter = {}
learnedList = []
songMean = {}
weightMax = -99
weightMin = 99
instanceCount = {}
instanceMax = -99
instanceMin = 99
for file in fileList:
    with open(file, 'r', encoding = 'utf8') as f:
        localList = json.load(f)
        listDistribution.append(0)
        for song in localList:
            listDistribution[-1] += song["D"]
            if song["annSongId"] not in progressCounter:
                progressCounter[song["annSongId"]] = (song["D"] <= 0)
            elif song["D"] <= 0:
                progressCounter[song["annSongId"]] += 1
                if progressCounter[song["annSongId"]] == len(fileList):
                    learnedList.append(song)
            if song["annSongId"] not in songMean:
                songMean[song["annSongId"]] = song["D"]
            else:
                songMean[song["annSongId"]] += song["D"]
                if file == fileList[-1]:
                    weightMax = max(weightMax, songMean[song["annSongId"]])
                    weightMin = min(weightMin, songMean[song["annSongId"]])
            if song["D"] not in instanceCount:
                instanceCount[song["D"]] = 1
                instanceMax = max(song["D"],instanceMax)
                instanceMin = min(song["D"],instanceMin)
            else:
                instanceCount[song["D"]] += 1
learnedList = sorted(learnedList, key = lambda song: song["annSongId"])
with open(fileLearned, 'r+', encoding = 'utf8') as f:
    f.truncate(0)
    f.seek(0)
    json.dump(learnedList,f,ensure_ascii=False)
    f.seek(0)
    fileData = f.read()
    fileData = fileData.replace(", {","\n,{")
    fileData = fileData.replace("}]","}\n]")
    f.seek(0)
    f.write(fileData)
    
#get frequency of various statistics
progressFrequency = [0]*(len(fileList)+1)
weightCounter = [0]*(weightMax-weightMin+1)
#instanceCounter = [0]*(instanceMax-instanceMin+1)
for key in progressCounter.keys():
    progressFrequency[progressCounter[key]] += 1
    weightCounter[songMean[key]-weightMin] += 1
#    instanceCounter[instanceCount[key]-instanceMin] += 1
progressFrequency.reverse()

#print statistics
print("\nPool Size: "+str(poolSize)+" LoadingSize: "+str(loadingSize)+" MeanSize: "+str(round(sum(listDistribution)/len(fileList),2)))
print()
print(" 0    10   20   30   40   50   60   70   80   90   100  Last")
print(listDistribution)
print()
print("SongProgress:\n" + str(weightCounter))
print()
print("MinSongWeight: "+str(weightMin)+" MaxSongWeight: "+str(weightMax)+" InstanceMinWeight: "+str(instanceMin)+" InstanceMaxWeight: "+str(instanceMax))
