import sys
import json
import random
import copy
import math

newShow = {}
itterationCount = 0
if len(sys.argv) == 2:
    newShow["name"] = sys.argv[1]
    newShow["score"] = 0
elif len(sys.argv) == 1:
    itterationCount = 2
else:
    print("rank takes 0-1 arguments")

with open("ranking.json", 'r', encoding = 'utf8') as f:
    showOrder = json.load(f)

#logic to rank shows
def rank(shows):
    for i,show in enumerate(shows):
        print(f"{i+1}: {show["name"]}")
    userOrdering = input("> ")
    try:
        numbers = [int(num) for num in userOrdering.split()]
    except ValueError:
        for i in range(len(shows)):
            print('\033[F', end = "")
            print('\033[K', end = "")
        return rank(shows)
    for i in range(len(shows)+1):
        print('\033[F', end = "")
        print('\033[K', end = "")
    newOrdering = []
    for num in numbers:
        newOrdering.append(shows[num-1])
    return newOrdering

if itterationCount: #check if we're reranking shows or inserting a new one
    while itterationCount > 0:
        itterationCount -= 1
        section = random.randint(0, len(showOrder)-4)
        segment = copy.deepcopy(showOrder[section:section+4])
        random.shuffle(segment)
        showOrder[section:section+4] = rank(segment)
else: #inserting new show
    minV = 0
    maxV = len(showOrder)
    while minV < maxV:
        pivot = random.randint(minV, maxV-1)
        comparison = rank([newShow, showOrder[pivot]])
        if comparison[0]["score"]:
            minV = pivot+1
        else:
            maxV = pivot
    showOrder.insert(minV, newShow)

#list any shows that need their score changed and rewrite ranking.json
print("Changes:_____________________________")
showCount = len(showOrder)
for i, show in enumerate(showOrder):
    if show["score"] != int(math.ceil(10-i*10/showCount)):
        show["score"] = int(math.ceil(10-i*10/showCount))
        print(f"{show["name"]} -> {show["score"]}")

with open("ranking.json", 'r+', encoding = 'utf8') as f:
    f.truncate(0)
    f.seek(0)
    json.dump(showOrder,f,ensure_ascii=False)
    f.seek(0)
    fileData = f.read()
    fileData = fileData.replace(", {","\n,{")
    fileData = fileData.replace("}]","}\n]")
    f.seek(0)
    f.write(fileData)
