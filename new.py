import json
import shutil
import math

#Move downloaded file to local directory and delete previous version

shutil.move(r"..\\..\\..\\Downloads\\merged.json","merged.json")
fileMerged = "merged"
filePool = "pool"
fileLoad = "loadingcutlist"
filePrep = "preplist"
fileDead = "dead"
filePractice = "_practice"
fileQuiz = "_quiz"
'''
shutil.copy("dummyDownload.json", "dummyMerged.json")
fileMerged = "dummyMerged"
filePool = "dummyPool"
fileLoad = "dummyLoad"
filePrep = "dummyPreplist"
fileDead = "dummyDead"
filePractice = "dummyPractice"
fileQuiz = "dummyQuiz"
'''

startingD = 18

#get list of all songs
with open(fileMerged+".json", 'r', encoding = 'utf8') as f:
    rawSongList = json.load(f)
with open(fileLoad+".json", 'r', encoding = 'utf8') as f:
    loadingList = json.load(f)
with open(filePrep+".json", 'r', encoding = 'utf8') as f:
    prepList = json.load(f)
with open(fileDead+".json", 'r', encoding = 'utf8') as f:
    deadList = json.load(f)
    deadListInit = len(deadList)
with open("modifications.json", 'r', encoding = 'utf8') as f:
    equivalances = json.load(f)
with open("broken.json", 'r', encoding = 'utf8') as f:
    brokenURLs = json.load(f)

#put useful information at start of list
shortHand = ["ST","STN","ID","SN","EN","SA","AID"]
longHand = ["songType","songTypeNumber","annSongId","songName","animeEnglishName","songArtist","annId"]
songList = []
idMap = {}
for index in range(len(rawSongList)):
    idMap[rawSongList[index]["annSongId"]] = index
    songList.append({})
    songList[index]["X"] = 0
    for jindex in range(len(shortHand)):
        songList[index][shortHand[jindex]] = rawSongList[index][longHand[jindex]]
    for key in rawSongList[index]:
        songList[index][key] = rawSongList[index][key]
    songList[index]["sampleWeights"] = None
    songList[index]["D"] = startingD
    songList[index]["annId"] = songList[index]["annSongId"]
    songList[index]["SN"] = "`"+songList[index]["SN"]+"`"

#map song ID's and broken URL's to equivalences
equivMap = {}
altNames = []
for index, entry in enumerate(equivalances):
    for ID in entry["equiv"]:
        equivMap[ID] = index
    altNames.append([])
brokenMap = {}
deadSongIdsQ = 0
for index, URL in enumerate(brokenURLs):
    brokenMap[URL["annSongId"]] = index
    if URL["annSongId"] not in idMap and index > 1:
        deadSongIdsQ = 1

for song in songList:
    if song["annSongId"] in equivMap:
        altNames[equivMap[song["annSongId"]]].extend(song["altAnimeNames"]+song["altAnimeNamesAnswers"])

fixedList = []
for index, song in enumerate(songList):
    if song["annSongId"] in equivMap:
        song["altAnimeNames"] = altNames[equivMap[song["annSongId"]]]
    song["altAnimeNames"] = list(set(song["altAnimeNames"]+song["altAnimeNamesAnswers"]))
    if song["annSongId"] in brokenMap:
        if song["video720"] == brokenURLs[brokenMap[song["annSongId"]]]["video720"]:
            fixedList.append(index)
        else:
            song["video720"] = brokenURLs[brokenMap[song["annSongId"]]]["video720"]

if len(fixedList) > 0 or deadSongIdsQ == 1:
    #sort fixedList descending
    fixedList = sorted(fixedList, key=lambda index: brokenMap[songList[index]["annSongId"]], reverse = True)

    #print any fixed urls
    print("Fixed URLs______________________________________")
    for index in fixedList:
        print(songList[index]["songName"]+"__from__"+songList[index]["animeEnglishName"])

    #remove fixed urls from broken list
    for index in fixedList:
        brokenURLs.pop(brokenMap[songList[index]["annSongId"]])
    #remove fixes corresponding to non-existant songs
    for index in reversed(range(2,len(brokenURLs))):
        if brokenURLs[index]["annSongId"] not in idMap:
            print(f"ANNID: {brokenURLs[index]["annSongId"]} no longer exists.")
            brokenURLs.pop(index)
    with open("broken.json", 'r+', encoding = 'utf8') as f:
        f.truncate(0)
        f.seek(0)
        json.dump(brokenURLs,f,ensure_ascii=False)
        f.seek(0)
        fileData = f.read()
        fileData = fileData.replace(", {","\n,{")
        fileData = fileData.replace("}]","}\n]")
        f.seek(0)
        f.write(fileData)

#replace songs in each list 1 by 1, but keep the old "D" value for songs in pool. Eliminate dead songs
with open(fileMerged+".json", 'r+', encoding = 'utf8') as f:
        f.truncate(0)
        f.seek(0)
        json.dump(songList,f,ensure_ascii=False)
        f.seek(0)
        fileData = f.read()
        fileData = fileData.replace(", {","\n,{")
        fileData = fileData.replace("}]","}\n]")
        f.seek(0)
        f.write(fileData)

def translateLength(oldList, oldSize, size, annId):
    if size is None:
        if oldList is None:
            return [0]*12
        elif oldSize is not None:
            print(f"Size lost for ANNID: {annId}")
        return oldList
    elif oldList is None:
        if oldSize is not None:
            print("SongWeights for ANNID="+str(annId)+" previously uninitialized")
        return [0]*int(max(math.ceil((size-15)/7.5)+2, 1))
    elif oldSize is not None and oldList is not None:
        if math.ceil((size-15)/7.5) == len(oldList)-2:
            return oldList
        print("\033[0;36mSongWeights for ANNID="+str(annId)+" reinitialized\033[0m")
        return [0]*int(max(math.ceil((size-15)/7.5)+2, 1))
    elif oldSize is None:
        start = oldList.pop(0)
        end = oldList.pop(-1)
        oldSize = len(oldList)
        newSize = math.ceil((size-15)/7.5)
        newList = [None]*newSize
        for i in range(newSize):
            low = int(math.floor(i*oldSize/newSize))
            high = int(math.ceil((i+1)*oldSize/newSize)-1)
            if low==high:
                newList[i] = oldList[low]
            else:
                val = oldList[low]*((low+1)/oldSize-i/newSize)+oldList[high]*((i+1)/newSize-high/oldSize)
                low += 1
                while low < high:
                    val += oldList[low]/oldSize
                    low += 1
                val *= newSize
                val = int(round(val,0))
                newList[i] = val
        return [start]+newList+[end]
    print("ANNID: "+annId+" avoided all checks")
    return oldList

deadCount = set()
oldSongs = set()
familiarMalIds = set()
with open(filePool+".json", 'r+', encoding = 'utf8') as f:
    knownList = json.load(f)
    deadIndices = []
    for index, song in enumerate(knownList):
        if song["annSongId"] not in idMap:
            deadIndices.append(index)
            if song["annSongId"] not in deadCount:
                deadList.append(song)
                deadCount.add(song["annSongId"])
            continue
        oldSongs.add(song["annSongId"])
        knownList[index] = songList[idMap[song["annSongId"]]]
        knownList[index]["D"] = song["D"]
        knownList[index]["X"] = song["X"]
        familiarMalIds.add(knownList[index]["malId"])
        knownList[index]["sampleWeights"] = translateLength(song["sampleWeights"], song["length"], knownList[index]["length"], knownList[index]["annId"])
        if song["length"] is not None and knownList[index]["length"] is not None:
            if abs(song["length"]-knownList[index]["length"]) > 1:
                print(f"ANNID={song["ID"]} {song["EN"]} by {song["SA"]} length increased by {song["length"]-knownList[index]["length"]} seconds")
                knownList[index]["D"] = startingD
    deadIndices.reverse()
    for index in deadIndices:
        knownList.pop(index)

    f.truncate(0)
    f.seek(0)
    json.dump(knownList,f,ensure_ascii=False)
    f.seek(0)
    fileData = f.read()
    fileData = fileData.replace(", {","\n,{")
    fileData = fileData.replace("}]","}\n]")
    f.seek(0)
    f.write(fileData)

with open(fileQuiz+".json", 'r+', encoding = 'utf8') as f:
    knownList = json.load(f)
    for index, song in enumerate(knownList):
        if song["annSongId"] in idMap:
            knownList[index] = songList[idMap[song["annSongId"]]]
            knownList[index]["D"] = song["D"]
            knownList[index]["startPoint"] = song["startPoint"]
            knownList[index]["sampleWeights"] = song["sampleWeights"]
    
    f.truncate(0)
    f.seek(0)
    json.dump(knownList,f,ensure_ascii=False)
    f.seek(0)
    fileData = f.read()
    fileData = fileData.replace(", {","\n,{")
    fileData = fileData.replace("}]","}\n]")
    f.seek(0)
    f.write(fileData)

with open(filePractice+".json", 'r+', encoding = 'utf8') as f:
    knownList = json.load(f)
    for index, song in enumerate(knownList):
        if song["annSongId"] in idMap:
            knownList[index] = songList[idMap[song["annSongId"]]]
            knownList[index]["D"] = song["D"]
            knownList[index]["startPoint"] = song["startPoint"]
            knownList[index]["sampleWeights"] = song["sampleWeights"]
    
    f.truncate(0)
    f.seek(0)
    json.dump(knownList,f,ensure_ascii=False)
    f.seek(0)
    fileData = f.read()
    fileData = fileData.replace(", {","\n,{")
    fileData = fileData.replace("}]","}\n]")
    f.seek(0)
    f.write(fileData)

learningMalIds = set()
newSongs = []
with open(filePrep+".json", 'r+', encoding = 'utf8') as f:
    knownList = json.load(f)
    elementNull = knownList.pop(0)
    deadIndices = []
    for index, song in enumerate(knownList):
        if song["annSongId"] not in idMap:
            deadIndices.append(index)
            if song["annSongId"] not in deadCount:
                deadList.append(song)
                deadCount.add(song["annSongId"])
            continue
        oldSongs.add(song["annSongId"])
        knownList[index] = songList[idMap[song["annSongId"]]]
        knownList[index]["sampleWeights"] = translateLength(None, None, knownList[index]["length"], song["annSongId"])
        knownList[index]["D"] = startingD
        learningMalIds.add(knownList[index]["malId"])
    deadIndices.reverse()
    for index in deadIndices:
        knownList.pop(index)
    for song in songList:            
        if song["annSongId"] not in oldSongs and song["malId"] in familiarMalIds and song["malId"] not in learningMalIds:
            song["sampleWeights"] = translateLength(None, None, song["length"], song["annSongId"])
            newSongs.append(song)
            knownList.append(song)
            oldSongs.add(song["annSongId"])
            learningMalIds.add(song["malId"])
            print(f"Previously learned MalID: {song["malId"]} gained at least 1 song.")

    f.truncate(0)
    f.seek(0)
    knownList.insert(0, elementNull)
    json.dump(knownList,f,ensure_ascii=False)
    f.seek(0)
    fileData = f.read()
    fileData = fileData.replace(", {","\n,{")
    fileData = fileData.replace("}]","}\n]")
    f.seek(0)
    f.write(fileData)

#swap old songs from fileLoad out and add any new songs to it.
with open(fileLoad+".json", 'r+', encoding = 'utf8') as f:
    knownList = json.load(f)
    deadIndices = []
    for index, song in enumerate(knownList):
        if song["annSongId"] not in idMap:
            deadIndices.append(index)
            if song["annSongId"] not in deadCount:
                deadList.append(song)
                deadCount.add(song["annSongId"])
            continue
        oldSongs.add(song["annSongId"])
        knownList[index] = songList[idMap[song["annSongId"]]]
        knownList[index]["sampleWeights"] = translateLength(None, None, knownList[index]["length"], song["annSongId"])
        knownList[index]["D"] = startingD
    deadIndices.reverse()
    for index in deadIndices:
        knownList.pop(index)

    for song in songList:
        if song["annSongId"] not in oldSongs:
            song["sampleWeights"] = translateLength(None, None, song["length"], song["annSongId"])
            newSongs.append(song)
            knownList.append(song)

    f.truncate(0)
    f.seek(0)
    json.dump(knownList,f,ensure_ascii=False)
    f.seek(0)
    fileData = f.read()
    fileData = fileData.replace(", {","\n,{")
    fileData = fileData.replace("}]","}\n]")
    f.seek(0)
    f.write(fileData)

#add dead songs to dead song list if there are any
if len(deadCount):
    print("\033[31mDeadSongs:\033[0m_______________________")
    for index in range(deadListInit, len(deadList)):
        print(deadList[index]["songName"]+"__from__"+deadList[index]["animeEnglishName"])
    with open(fileDead+".json", 'r+', encoding = 'utf8') as f:
        f.truncate(0)
        f.seek(0)
        json.dump(deadList,f,ensure_ascii=False)
        f.seek(0)
        fileData = f.read()
        fileData = fileData.replace(", {","\n,{")
        fileData = fileData.replace("}]","}\n]")
        f.seek(0)
        f.write(fileData)

#print new songs
print("\033[31mNewSongs:\033[0m_______________________")
for song in newSongs:
    print(song["songName"]+"__from__"+song["animeEnglishName"])
