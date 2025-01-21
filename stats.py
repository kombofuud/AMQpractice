#songs in pool
#songs in prep/loading
#give mean per list
#average song progress
#instance frequencies

import json

fileList = ["0cutlist.json", "10cutlist.json", "20cutlist.json", "30cutlist.json", "40cutlist.json", "50cutlist.json", "60cutlist.json", "70cutlist.json", "80cutlist.json", "90cutlist.json", "100cutlist.json", "lastcutlist.json"]
filePrep = "preplist.json"
fileLoad = "loadingcutlist.json"

#getting list sizes
with open(fileList[0], 'r', encoding = 'utf8') as f:
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
progressCounter = map()
songMean = map()
instanceCount = map()
instanceMax = -100
instanceMin = 100
for file in fileList:
    with open(file, 'r', encoding = 'utf8') as f:
        localList = json.load(f)
        listDistribution.append([0])
        for song in localList:
            listDistribution[-1] += song["D"]
            if song["annSongId"] not in progressCounter:
                progressCounter[song["annSongId"]] = (song["D"] <= 0)
            elif song["D"] <= 0:
                progressCounter[song["annSongId"]] += 1
            if song["annSongId"] not in songMean:
                songMean[song["annSongId"]] = song["D"]
            else:
                songMean[song["annSongId"]] += song["D"]
            if song["D"] not in instanceCount:
                instanceCount[song["D"]] = 1
                instanceMax = max(song["D"],instanceMax)
                instanceMin = min(song["D"],instanceMin)
            else:
                instanceCount[song["D"]] += 1

#print statistics
print("Pool Size: "+poolSize+" LoadingSize: "+loadingSize+" MeanSize: "+round(sum(listDistribution)/len(fileList),2)
print()
print(listDistribution)
print()
