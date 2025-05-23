#TODO

#fileList replaced with pool.json
#add a sampleDistribution variable set to null
#Keep D value and song distribution (and song sample for _quiz/_practice)
#update _practice.json and _quiz.json

import json
import shutil

#Move downloaded file to local directory and delete previous version
shutil.move(r"..\..\..\Downloads\merged.json","merged.json")

'''
fileMerged = "merged"
fileList = ["0","10","20","30","40","50","60","70","80","90","100","last"]
fileLoad = "loadingcutlist"
filePrep = "preplist"
fileDead = "dead"
'''
fileMerged = "dummyMerged"
fileList = ["dummy0", "dummy1"]
fileLoad = "dummyLoad"
filePrep = "dummyPreplist"
fileDead = "dummyDead"

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
shortHand = ["ST","STN","ID","SN","EN","SA"]
longHand = ["songType","songTypeNumber","annSongId","songName","animeEnglishName","songArtist"]
songList = []
idMap = {}
for index in range(len(rawSongList)):
    idMap[rawSongList[index]["annSongId"]] = index
    songList.append({})
    for jindex in range(len(shortHand)):
        songList[index][shortHand[jindex]] = rawSongList[index][longHand[jindex]]
    for key in rawSongList[index]:
        songList[index][key] = rawSongList[index][key]
    songList[index]["D"] = 1
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
for index, URL in enumerate(brokenURLs):
    brokenMap[URL["annSongId"]] = index

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

if len(fixedList):
    #sort fixedList descending
    fixedList = sorted(fixedList, key=lambda index: brokenMap[songList[index]["annSongId"]], reverse = True)

    #print any fixed urls
    print("Fixed URLs______________________________________")
    for index in fixedList:
        print(songList[index]["songName"]+"__from__"+songList[index]["animeEnglishName"])

    #remove fixed urls from broken list
    for index in fixedList:
        brokenURLs.pop(brokenMap[songList[index]["annSongId"]])
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
    
deadCount = set()
oldSongs = set()
for file in fileList:
    with open(file+"cutlist.json", 'r+', encoding = 'utf8') as f:
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

with open(filePrep+".json", 'r+', encoding = 'utf8') as f:
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

#add dead songs to dead song list if there are any
if len(deadCount):
    print("DeadSongs:_______________________")
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

#add new songs to file Load, and print new songs
newSongs = []
with open(fileLoad+".json", 'r+', encoding = 'utf8') as f:
    knownList = json.load(f)
    for song in songList:
        if song["annSongId"] not in oldSongs:
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
print("NewSongs:_______________________")
for song in newSongs:
    print(song["songName"]+"__from__"+song["animeEnglishName"])
