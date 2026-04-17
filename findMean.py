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
songTotal = 0

weights = []
for song in known:
    totalWeight += 1.015625/(1+4**(song["D"]-3))
    weights.append(1.015625/(1+4**(song["D"]-3)))
    DMax = max(DMax, song["D"])

songDistribution = [0]*(int(round(DMax))+1)

for _ in range(1000):
    songSelector = [random.random() for _ in range(len(known))]
    for i in range(len(known)):
        if songSelector[i] < weights[i]:
            songSelector[i] = 1
            songDistribution[int(round(known[i]["D"]))] += 1
        else:
            songSelector[i] = 0
    minCount = min(minCount, sum(songSelector))
    maxCount = max(maxCount, sum(songSelector))
    songTotal += sum(songSelector)
print(f"totalWeight: {totalWeight}")
print(f"min: {minCount}")
print(f"max: {maxCount}")
print(f"mean: {songTotal/1000}")
print(songDistribution)
