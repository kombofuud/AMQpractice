import sys
import json
import random
import copy
import math

newShow = {}
itterationCount = 0:
if len(sys.argv) == 1:
    newShow["name"] = sys.argV[0]
    newShow["score"] = 0
elif len(sys.argv) == 0:
    itterationCount = 5
else:
    print("rank takes 0-1 arguments")

with open("ranking.json", 'r', encoding = 'utf8') as f:
    showOrder = json.load(f)

#logic to rank shows
def rank(shows):
    for show in shows:
        print(show["name"])
    userOrdering = input("> ")
    try:
        numbers = [float(num) for num in userOrdering.split()]
    except ValueError:
        for i in range(len(shows))
            sys.stdout.write('\033[F')
            sys.stdout.write('\033[K')
        return rank(shows)
    newOrdering = []
    for num in numbers:
        newOrdering.append(shows[num])
    return newOrdering

if itterationCount and len(showOrder) >= 5: #check if we're reranking shows or inserting a new one
    while itterationCount > 0:
        itterationCount -= 1
        section = random.randomInt(0, len(showOrder)-5)
        segment = copy.deepcopy(showOrder[section:section+5])
        showOrder[section:section+5] = rank(segment)
else: #inserting new show
    minV = 0
    maxV = len(showOrder)
    while min < max:
        pivot = random.randomInt(minV, maxV-1)
        comparison = rank([newShow, songOrder[pivot]])
        if comparison[0]["score"]:
            minV = pivot+1
        else:
            maxV = pivot
    songOrder.insert(minV, newShow)

#list any shows that need their score changed
showCount = len(showOrder)
for i, show in enumerate(showOrder):
    if show["score"] != int(math.ceil(10-i*10/showCount))
        show["score"] = int(math.ceil(10-i*10/showCount))
        print(f"{show["name"]} -> {show["score"]}")
