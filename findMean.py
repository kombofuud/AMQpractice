import math
import numpy
import json
import random

with open("pool.json", 'r', encoding = 'utf8') as f:
    known = json.load(f)

DList = []
DMax = -100
DMin = 0
indexMap = dict()
maxWeightCount = 0
songCounter = 0
totalWeight = 0
minCount = len(known)+1
maxCount = -1
totalGain = 0
minGain = 100
maxGain = 0
songTotal = 0

weights = []
for song in known:
#    songWeight = 1.015625/(1+4**(song["D"]-3))
    songWeight = 1/(1+((2**song["D"]-1)/(100+2**song["D"]))*2**(song["D"]+1))
    totalWeight += songWeight
    weights.append(songWeight)
    DMax = max(DMax, song["D"])

songDistribution = [0]*(int(math.ceil(DMax))+1)

for _ in range(1000):
    songSelector = [random.random() for _ in range(len(known))]
    songGain = 0
    for i in range(len(known)):
        if songSelector[i] < weights[i]:
            songSelector[i] = 1
            songDistribution[int(math.ceil(known[i]["D"]))] += 1
            songGain += weights[i]-1.015625/(1+4**(known[i]["D"]-2))
        else:
            songSelector[i] = 0
    minCount = min(minCount, sum(songSelector))
    maxCount = max(maxCount, sum(songSelector))
    songTotal += sum(songSelector)
    minGain = min(minGain, songGain)
    maxGain = max(maxGain, songGain)
    totalGain += songGain
print(f"totalWeight: {totalWeight}")
print(f"min: {minCount} minGain: {minGain}")
print(f"max: {maxCount} maxGain: {maxGain}")
print(f"mean: {songTotal/1000}, meanGain {totalGain/1000}")
print(songDistribution)
