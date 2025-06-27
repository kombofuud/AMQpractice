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
            if len(minutesSeconds) > 2:
                print(f"Error - TimeStamp: {minutesSeconds} of Range: {element} of String: {rangeString} is not a valid TimeStamp")
                sys.exit(1)
            if len(minutesSeconds) == 1:
                minutesSeconds.insert(0,0)
            minutesSeconds[0] = int(minutesSeconds[0])
            minutesSeconds[1] = float(minutesSeconds[1])
            secondsRange.append(60*minutesSeconds[0]+minutesSeconds[1])
        if secondsRange[1]-secondsRange[0] <= sampleLength:
            continue
        timeList.append([secondsRange[0],secondsRange[1]-secondsRange[0]-sampleLength])
    if len(timeList) == 0:
        print(f"Error - no timeStamps found for String: {rangeString}")
    return timeList

#make maps from ids to important information
timeMap = {}
for i,ID in enumerate(splitData):
    timeMap[ID["ID"]] = getRanges(ID["sample"])

songMap = {}
for i,song in enumerate(songPool):
    if song["ID"] in timeMap:
        songMap[song["ID"]] = i

#randomize the list
sampleSongs = []
for i in range(1000):
    songID = splitData[random.randint(0,len(splitData)-1)]["ID"]
    weightRanges = timeMap[songID]
    weightList = []
    for element in weightRanges:
        weightList.append(element[1])
    section = random.choices(range(len(weightList)), weights=weightList, k=1)[0]
    song = copy.deepcopy(songPool[songMap[songID]])
    song["startPoint"] = max(100*(weightRanges[section][0]+weightRanges[section][1]*random.random())/(song["length"]-sampleLength),0)
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
