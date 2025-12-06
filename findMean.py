import math
import numpy
import json
import random

with open("pool.json", 'r', encoding = 'utf8') as f:
    known = json.load(f)

DList = []
DMin = 9999
DMax = 8
indexMap = dict()
maxWeightCount = 0
songCounter = 0
for song in known:
    if song["D"] == DMax:
        maxWeightCount += 1
    DList.append(math.exp(song["D"])*len(song["sampleWeights"]))
    DMin = min(DMin, song["D"])
    songCounter += 1

minCount = 9999999999
maxCount = -1
songTotal = 0
for _ in range(1000):
    randomSongList = list(numpy.random.choice(known, size = len(DList), p = DList/numpy.sum(DList), replace = False))
    songCount = 0
    testWeightCount = maxWeightCount
    for song in randomSongList:
        songCount += 1
        if song["D"] == 8:
            testWeightCount-= 1
        if testWeightCount == 0:
            break
    minCount = min(minCount, songCount)
    maxCount = max(maxCount, songCount)
    songTotal += songCount
print(f"min: {minCount}")
print(f"max: {maxCount}")
print(f"mean: {songTotal/1000}")
