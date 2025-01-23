#THINGS TO TEST
#moves merged.json to local directory
#adds information to start of the json files including the D value
#correctly adds alt names to alt answers
#correctly fixes broken urls
#removes fixed urls from broken urls
#replaces old instances of songs in each list with new ones while keeping the old D value
#adds dead songs to dead song list
#adds new songs to loading list
#adds updated songs to merged.json
#prints dead songs
#prints new songs
#prints modified songs

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
with open("modifications.json", 'r', encoding = 'utf8') as f:
    equivalances = json.load(f)
with open("broken.json", 'r', encoding = 'utf8') as f:
    brokenURLs = json.load(f)

#put useful information at start of list
shortHand = ["ST","STN","V","SN","EN","SA"]
longHand = ["songType","songTypeNumber","animeVintage","songName","animeEnglishName","songArtist"]
songList = []
idMap = map()
for index in range(len(rawSongList)):
    idMap[rawSongList[index]["annSongId"]] = index
    songList.append({"D": 1})
    for jindex in range(len(shortHand)):
        songList[index][shortHand[jindex]] = rawSongList[index][longHand[jindex]]
    for key in rawSongList[index]:
        songList[index][key] = rawSongList[index][key]

#map song ID's and broken URL's to equivalences
equivMap = map()
altNames = []
for index, entry in enumerate(equivalances):
    for ID in entry:
        equivMap[ID] = index
    altNames.append([])
brokenMap = map()
for index, URL in enumerate(brokenURLs):
    brokenMap[brokenURLs["annSongId"]] = index

for song in songList:
    if song["annSongId"] in equivMap:
        altNames[equivMap[song["annSongId"]]].append(song["altAnimeNames"]+song["altAnimeNamesAnswers"])

fixedList = []
for index, song in enumerate(songList):
    if song["annSongId"] in equivMap:
        song["altAnimeNames"] = altNames[equivMap[song["annSongId"]]]
    song["altAnimeNames"] = list(set(song["altAnimeNames"]))
    if song["annSongId"] in brokenMap:
        if song["video720"] == brokenURLs[brokenMap[song["annSongId"]]]["video720"]:
            fixedList.append(index)
        else:
            song["video720"] = brokenURLs[brokenMap[song["annSongId"]]]["video720"]

if len(fixedList):

    #print any fixed urls
    print("Fixed URLs______________________________________")
    for index in fixedList:
        print(songList[idMap[index]]["songName"]+"__from__"+songList[idMap[index]]["animeEnglishName"])

    #remove fixed urls from broken list
    fixedList.reverse()
    for index in fixedList:
        brokenURLs.pop(index)
    with open("broken.json", 'w', encoding = 'utf8') as f:
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
deadCount = set()
oldSongs = set()
for file in fileList:
    with open(file+"cutlist.json", 'r+', encoding = 'utf8') as f:
        knownList = json.load(f)
        for index, song in enumerate(knownList):
            if song["annSongId"] not in idMap:
                if song not in deadCount:
                    deadList.append(song)
                    deadCount.add(song)
                continue
            oldSongs.add(song["annSongId"])
            knownList[index] = songList[idMap[song["annSongId"]]]
            knownList[index]["D"] = song["D"]

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
    for index, song in enumerate(knownList):
        if song["annSongId"] not in idMap:
            if song not in deadCount:
                deadList.append(song)
                deadCount.add(song)
            continue
        oldSongs.add(song["annSongId"])
        knownList[index] = songList[idMap[song["annSongId"]]]

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
    for index, song in enumerate(knownList):
        if song["annSongId"] not in idMap:
            if song not in deadCount:
                deadList.append(song)
                deadCount.add(song)
            continue
        oldSongs.add(song["annSongId"])
        knownList[index] = songList[idMap[song["annSongId"]]]

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
    with open(fileDead+".json", 'w', encoding = 'utf8') as f:
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
