import json
import random
import sys
import copy

sampleLength = 15

with open("merged.json", "r", encoding="utf-8") as f:
    songPool = json.load(f)
with open("splitData.json", "r", encoding="utf-8") as f:
    splitData = json.load(f)

#turn range strings into numbers
def getRanges(rangeString):
    splitRanges = rangeString.split(',')
    timeList = []
    for element in splitRanges:
        startEnd = element.split('-')
        if len(startEnd) != 2:
            print(f"Error - Range: {element} of String: {rangeString} is not a valid Range")
            sys.exit(1)
        secondsRange = []
        for number in startEnd:
            minutesSeconds = number.split(':')
            if len(minutesSeconds) >= 2:
                print(f"Error - TimeStamp: {minutesSeconds} of Range: {element} of String: {rangeString} is not a valid TimeStamp")
                sys.exit(1)
            if minutesSeconds.length == 1:
                minutesSeconds.insert(0,0)
            minutesSeconds[0] = int(minutesSeconds[0])
            minutesSeconds[1] = float(minutesSeconds[1])
            timeList.append(60*minutesSeconds[0]+minutesSeconds[1])
        if timeList[1]-timeList[0] <= 0:
            continue
        timeList.append([timeList[0],timeList[1]-timeList[0]])
    return timeList[]

#make maps from ids to important information
timeMap = {}
for i,ID in enumerate(splitData):
    idMap[ID["ID"]] = getRanges(ID["sample"])

songMap = {}
for i,song in enumerate(songPool):
    if song["ID"] in idMap:
        songMap[song["ID"]] = i

#randomize the list
sampleSongs = []
for i in range(1000):
    songID = splitData[random.randint(0,len(splitData)-1)]["ID"]
    weightRanges = idMap[songID]
    weightList = []
    for element in weightRanges:
        weightList.append(weightRanges[1])
    section = random.choices(range(len(weightList)), weights=weightList, k=1)[0]
    song = copy.deepcopy(songPool[songID])
    song["startPoint"] = weightRanges[section][0]+weightRanges[section][1]*random.random()
    sampleSongs.append(song)

with open("_split.json", 'r+', encoding = 'utf8') as file:
        file.truncate(0)
        file.seek(0)
        json.dump(sampleSongs,file,ensure_ascii=False)
        file.seek(0)
        fileData = file.read()
        fileData = fileData.replace(", {","\n,{")
        fileData = fileData.replace("}]","}\n]")
        file.seek(0)
        file.write(fileData)

print("_split.json written sucessfully")
