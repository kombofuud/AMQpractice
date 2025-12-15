import math
import numpy
import json
import random

with open("pool.json", 'r', encoding = 'utf8') as f:
    known = json.load(f)

DList = []
DMax = -1
indexMap = dict()
maxWeightCount = 0
songCounter = 0
for song in known:
    if song["D"] == 0:
        maxWeightCount += 1
    DList.append(math.exp(-song["D"])*math.sqrt(len(song["sampleWeights"])))
    DMax = max(DMax, song["D"])
    songCounter += 1

minCount = len(DList)+1
maxCount = -1
songTotal = 0
songDistribution = [0]*(int(math.ceil(DMax))+1)
for _ in range(1000):
    randomSongList = list(numpy.random.choice(known, size = len(DList), p = DList/numpy.sum(DList), replace = False))
    songCount = 0
    testWeightCount = maxWeightCount
    for song in randomSongList:
        songCount += 1
        songDistribution[int(math.ceil(song["D"]))] += 1
        if song["D"] == 0:
            testWeightCount-= 1
        if testWeightCount == 0:
            break
    minCount = min(minCount, songCount)
    maxCount = max(maxCount, songCount)
    songTotal += songCount
print(f"min: {minCount}")
print(f"max: {maxCount}")
print(f"mean: {songTotal/1000}")
print(songDistribution)
