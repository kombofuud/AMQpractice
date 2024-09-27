import os
import json
import shutil

#Move downloaded file to local directory and delete previous version
#shutil.move(r"..\..\..\Downloads\merged.json","merged.json")
#load songs from each list
'''
fileMerged = "merged"
fileList = ["0","10","20","30","40","50","60","70","80","90","100","last"]
fileLoad = "loadingcutlist"
fileLearned = "learnedcutlist"
fileDead = "Dead"
'''
fileLearned = "dummyLearned"
fileMerged = "dummyMerged"
fileList = ["dummy0", "dummy1", "dummyLearned"]
fileLoad = "dummyLoad"
fileDead = "dummyDead"

with open(fileMerged+".json", 'r', encoding = 'utf8') as f:
    songList = json.load(f)
with open(fileLoad+".json", 'r', encoding = 'utf8') as f:
    loadingList = json.load(f)
with open("modifications.json", 'r', encoding = 'utf8') as f:
    equivalances = json.load(f)
with open(fileDead+".json", 'r', encoding = 'utf8') as f:
    deadList = json.load(f)

#load equivalence mapping
equiv = dict()
index = 0
altNames = []
deadSongs = []
deadSongMap = set()
for relation in equivalances:
    for name in relation["equiv"]:
        equiv[name] = index
    index += 1
    altNames.append(set())

for song in deadList:
    deadSongMap.add(song["video720"])

#add missing info to songs
songCodes = dict()
nameCodes = dict()
index = 0
for song in songList:
    if song["video720"] is None:
        song["video720"] = song["video480"]
    if song["animeVintage"] is None:
        song["animeVintage"] = ""
    if song["songArtist"]+song["songName"] in equiv:
        for name in song["altAnimeNames"]:
           altNames[equiv[song["songArtist"]+song["songName"]]].add(name)
    songCodes[song["video720"]] = index
    nameCodes[song["songArtist"]+song["songName"]+song["animeVintage"]] = index
    index += 1
for song in songList:
    if song["songArtist"]+song["songName"] in equiv:
        song["altAnimeNamesAnswers"] = list(altNames[equiv[song["songArtist"]+song["songName"]]])

#Replace old json objects with new ones
nameSet = set()
mirrorSet = set()
urlSet = set()
vintageSet = set()
pickedMap = dict()
deadSongs = []
for section in fileList:
    with open(section+"cutlist.json", 'r', encoding = 'utf8') as f:
        knownList = json.load(f)
    index = 0
    while index<len(knownList):
        song = knownList[index]
        if song["video720"] is None:
            song["video720"] = song["video480"]
        if song["animeVintage"] is None:
            song["animeVintage"] = ""
        urlSet.add(song["video720"])
        nameSet.add(song["animeEnglishName"]+song["songName"])
        mirrorSet.add(song["songArtist"]+song["songName"])
        vintageSet.add(song["songArtist"]+song["songName"]+song["animeVintage"])
        if song["video720"] in songCodes:
            knownList[index] = songList[songCodes[song["video720"]]]
            index = index+1
        elif song["songArtist"]+song["songName"]+song["animeVintage"] in nameCodes:
            knownList[index] = songList[nameCodes[song["songArtist"]+song["songName"]+song["animeVintage"]]]
            index = index+1
        else:
            knownList.pop(index)
            if song["video720"] not in deadSongMap:
                deadSongMap.add(song["video720"])
                deadSongs.append(song)
    with open(section+"cutlist.json", 'w', encoding = 'utf8') as f:
        f.truncate(0)
        f.seek(0)
        json.dump(knownList, f)

newKnownList = []
with open(fileLoad+".json", 'r', encoding = 'utf8') as f:
    knownList = json.load(f)
index = 0
while index<len(knownList):
    song = knownList[index]
    if song["video720"] is None:
        song["video720"] = song["video480"]
    if song["animeVintage"] is None:
        song["animeVintage"] = ""
    urlSet.add(song["video720"])
    vintageSet.add(song["songArtist"]+song["songName"]+song["animeVintage"])
    if song["video720"] in songCodes:
        knownList[index] = songList[songCodes[song["video720"]]]
    elif song["songArtist"]+song["songName"]+song["animeVintage"] in nameCodes:
        knownList[index] = songList[nameCodes[song["songArtist"]+song["songName"]+song["animeVintage"]]]
    else:
        knownList.pop(index)
        continue
    if song["animeEnglishName"]+song["songName"] in nameSet:
        knownList.pop(index)
        newKnownList.append(song)
        urlSet.add(song["video720"])
        vintageSet.add(song["songArtist"]+song["songName"]+song["animeVintage"])
        continue
    elif song["songArtist"]+song["songName"] in mirrorSet:
        knownList.pop(index)
        newKnownList.append(song)
        urlSet.add(song["video720"])
        nameSet.add(song["animeEnglishName"]+song["songName"])
        continue
    index = index+1
with open(fileLoad+".json", 'w', encoding = 'utf8') as f:
    f.truncate(0)
    f.seek(0)
    json.dump(knownList, f)

#add new songs to respective lists depending on if it's similar to other practiced ones
newLoadingList = []
newList = []
for song in songList:
    if song["video720"] not in urlSet and song["songArtist"]+song["songName"]+song["animeVintage"] not in vintageSet:
        if song["animeEnglishName"]+song["songName"] in nameSet or song["songArtist"]+song["songName"] in mirrorSet:
            newKnownList.append(song)
        else:
            newLoadingList.append(song)
        newList.append(song)
for section in fileList:
    with open(section+"cutlist.json", 'r+', encoding = 'utf8') as f:
        if section != fileLearned:
            knownList = json.load(f)
            knownList.extend(newKnownList)
            f.truncate(0)
            f.seek(0)
            json.dump(knownList,f)
        f.seek(0)
        fileData = f.read()
        fileData = fileData.replace(", {","\n,{")
        fileData = fileData.replace("}]","}\n]")
        f.seek(0)
        f.write(fileData)

with open(fileLoad+".json", "r+", encoding = 'utf8') as f:
    knownList = json.load(f)
    knownList.extend(newLoadingList)
    f.truncate(0)
    f.seek(0)
    json.dump(knownList,f)
    f.seek(0)
    fileData = f.read()
    fileData = fileData.replace(", {","\n,{")
    fileData = fileData.replace("}]","}\n]")
    f.seek(0)
    f.write(fileData)

with open(fileDead+".json", "r+", encoding = 'utf8') as f:
    knownList = json.load(f)
    knownList.extend(deadSongs)
    f.truncate(0)
    f.seek(0)
    json.dump(knownList,f)
    f.seek(0)
    fileData = f.read()
    fileData = fileData.replace(", {","\n,{")
    fileData = fileData.replace("}]","}\n]")
    f.seek(0)
    f.write(fileData)

with open(fileMerged+".json", "r+", encoding = 'utf8') as f:
    f.truncate(0)
    json.dump(songList,f)
    f.seek(0)
    fileData = f.read()
    fileData = fileData.replace(", {","\n,{")
    fileData = fileData.replace("}]","}\n]")
    f.seek(0)
    f.write(fileData)


#Print out new songs
print("newLearning:-----------------------------------")
for song in newKnownList:
    print(song["animeEnglishName"]+": "+song["songName"]+" by "+song["songArtist"])
print("newLoading:-----------------------------------")
for song in newLoadingList:
    print(song["animeEnglishName"]+": "+song["songName"]+" by "+song["songArtist"])
print("Deprecated:-----------------------------------")
for song in deadSongs:
    print(song["animeEnglishName"]+": "+song["songName"]+" by "+song["songArtist"])
