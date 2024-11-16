import os
import json
import shutil

#Move downloaded file to local directory and delete previous version
shutil.move(r"..\..\..\Downloads\merged.json","merged.json")
#load songs from each list

fileMerged = "merged"
fileList = ["0","10","20","30","40","50","60","70","80","90","100","last"]
fileLoad = "loadingcutlist"
filePrep = "preplist"
fileLearned = "learned"
fileDead = "dead"
'''
fileLearned = "dummyLearned"
fileMerged = "dummyMerged"
fileList = ["dummy0", "dummy1"]
fileLoad = "dummyLoad"
filePrep = "dummyPreplist"
fileDead = "dummyDead"
'''
if fileLearned not in fileList:
    fileList.append(fileLearned)

with open(fileMerged+".json", 'r', encoding = 'utf8') as f:
    rawSongList = json.load(f)
with open(fileLoad+".json", 'r', encoding = 'utf8') as f:
    loadingList = json.load(f)
with open("modifications.json", 'r', encoding = 'utf8') as f:
    equivalances = json.load(f)
with open(fileDead+".json", 'r', encoding = 'utf8') as f:
    deadList = json.load(f)

#put useful information at start of list
shortHand = ["ST","STN","V","SN","EN","SA"]
longHand = ["songType","songTypeNumber","animeVintage","songName","animeEnglishName","songArtist"]
songList = []
for index in range(len(rawSongList)):
    songList.append({})
    for jindex in range(len(shortHand)):
        songList[index][shortHand[jindex]] = rawSongList[index][longHand[jindex]]
    for key in rawSongList[0]:
        songList[index][key] = rawSongList[index][key]

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
equivList = set()
index = 0
for song in songList:
    if song["video720"] is None or song["video720"] == "":
        song["video720"] = song["video480"]
    if song["animeVintage"] is None:
        song["animeVintage"] = ""
    if song["songArtist"]+song["songName"] in equiv:
        equivList.add(song["songArtist"]+song["songName"])
        for name in song["altAnimeNames"]:
           altNames[equiv[song["songArtist"]+song["songName"]]].add(name)
    songCodes[song["video720"]] = index
    nameCodes[song["songArtist"]+song["songName"]+str(song["songType"])+song["animeVintage"]] = index
    index += 1
for song in songList:
    if song["songArtist"]+song["songName"] in equiv:
        song["altAnimeNamesAnswers"] = list(altNames[equiv[song["songArtist"]+song["songName"]]])
    altNameList = set()
    for name in song["altAnimeNames"]:
        altNameList.add(name)
    for name in song["altAnimeNamesAnswers"]:
        altNameList.add(name)
    song["altAnimeNames"] = list(altNameList)

#Replace old json objects with new ones
nameSet = set()
mirrorSet = set()
urlSet = set()
vintageSet = set()
pickedMap = dict()
changedSet = set()
nameChangeSet = set()
nameChangeList = []
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
        vintageSet.add(song["songArtist"]+song["songName"]+str(song["songType"])+song["animeVintage"])
        if song["video720"] in songCodes:
            knownList[index] = songList[songCodes[song["video720"]]]
        elif song["songArtist"]+song["songName"]+str(song["songType"])+song["animeVintage"] in nameCodes:
            if knownList[index]["video720"] not in changedSet:
                changedSet.add(songList[nameCodes[song["songArtist"]+song["songName"]+str(song["songType"])+song["animeVintage"]]]["video720"])
            knownList[index] = songList[nameCodes[song["songArtist"]+song["songName"]+str(song["songType"])+song["animeVintage"]]]
        else:
            knownList.pop(index)
            if song["video720"] not in deadSongMap:
                deadSongMap.add(song["video720"])
                deadSongs.append(song)
            continue
        if set(song["altAnimeNames"]) != set(knownList[index]["altAnimeNames"]) and song["animeEnglishName"]+song["animeVintage"] not in nameChangeSet:
            nameChangeSet.add(song["animeEnglishName"]+song["animeVintage"])
            lostNames = set(song["altAnimeNames"])-set(knownList[index]["altAnimeNames"])
            gainedNames = set(knownList[index]["altAnimeNames"])-set(song["altAnimeNames"])
            nameChangeList.append([song["animeVintage"],song["animeEnglishName"],lostNames,gainedNames])
        song = knownList[index]
        urlSet.add(song["video720"])
        nameSet.add(song["animeEnglishName"]+song["songName"])
        mirrorSet.add(song["songArtist"]+song["songName"])
        vintageSet.add(song["songArtist"]+song["songName"]+str(song["songType"])+song["animeVintage"])
        index = index+1
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
    vintageSet.add(song["songArtist"]+song["songName"]+str(song["songType"])+song["animeVintage"])
    if song["video720"] in songCodes:
        knownList[index] = songList[songCodes[song["video720"]]]
    elif song["songArtist"]+song["songName"]+str(song["songType"])+song["animeVintage"] in nameCodes:
        knownList[index] = songList[nameCodes[song["songArtist"]+song["songName"]+str(song["songType"])+song["animeVintage"]]]
    else:
        knownList.pop(index)
        if song["video720"] not in deadSongMap:
            deadSongMap.add(song["video720"])
            deadSongs.append(song)
        continue
    '''
    if song["animeEnglishName"]+song["songName"] in nameSet:
        knownList.pop(index)
        newKnownList.append(song)
        nameSet.add(song["animeEnglishName"]+song["songName"])
        mirrorSet.add(song["songArtist"]+song["songName"])
        continue
    elif song["songArtist"]+song["songName"] in mirrorSet:
        knownList.pop(index)
        newKnownList.append(song)
        nameSet.add(song["animeEnglishName"]+song["songName"])
        mirrorSet.add(song["songArtist"]+song["songName"])
        continue
    '''
    song = knownList[index]
    urlSet.add(song["video720"])
    vintageSet.add(song["songArtist"]+song["songName"]+str(song["songType"])+song["animeVintage"])
    index = index+1
with open(fileLoad+".json", 'w', encoding = 'utf8') as f:
    f.truncate(0)
    f.seek(0)
    json.dump(knownList, f)

with open(filePrep+".json", 'r', encoding = 'utf8') as f:
    knownList = json.load(f)
index = 0
while index<len(knownList):
    song = knownList[index]
    if song["video720"] is None:
        song["video720"] = song["video480"]
    if song["animeVintage"] is None:
        song["animeVintage"] = ""
    urlSet.add(song["video720"])
    vintageSet.add(song["songArtist"]+song["songName"]+str(song["songType"])+song["animeVintage"])
    if song["video720"] in songCodes:
        knownList[index] = songList[songCodes[song["video720"]]]
    elif song["songArtist"]+song["songName"]+str(song["songType"])+song["animeVintage"] in nameCodes:
        knownList[index] = songList[nameCodes[song["songArtist"]+song["songName"]+str(song["songType"])+song["animeVintage"]]]
    else:
        knownList.pop(index)
        if song["video720"] not in deadSongMap:
            deadSongMap.add(song["video720"])
            deadSongs.append(song)
        continue
    song = knownList[index]
    urlSet.add(song["video720"])
    vintageSet.add(song["songArtist"]+song["songName"]+str(song["songType"])+song["animeVintage"])
    index = index+1
with open(filePrep+".json", 'w', encoding = 'utf8') as f:
    f.truncate(0)
    f.seek(0)
    json.dump(knownList, f)

#check to see if any name in equivalences was changed
for relation in equivalances:
    for name in relation["equiv"]:
        if name not in equivList:
            print("Equivalence missing for: "+name)

#add new songs to respective lists depending on if it's similar to other practiced ones
newLoadingList = []
newList = []

for song in songList:
    if song["video720"] not in urlSet and song["songArtist"]+song["songName"]+str(song["songType"])+song["animeVintage"] not in vintageSet:
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
            json.dump(knownList,f,ensure_ascii=False)
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
    json.dump(knownList,f,ensure_ascii=False)
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
    json.dump(knownList,f,ensure_ascii=False)
    f.seek(0)
    fileData = f.read()
    fileData = fileData.replace(", {","\n,{")
    fileData = fileData.replace("}]","}\n]")
    f.seek(0)
    f.write(fileData)

with open(fileMerged+".json", "r+", encoding = 'utf8') as f:
    f.truncate(0)
    json.dump(songList,f,ensure_ascii=False)
    f.seek(0)
    fileData = f.read()
    fileData = fileData.replace(", {","\n,{")
    fileData = fileData.replace("}]","}\n]")
    f.seek(0)
    f.write(fileData)

#Print out new songs
print("changedURLs:-----------------------------------")
for url in changedSet:
    print(songList[songCodes[url]]["animeEnglishName"]+": "+songList[songCodes[url]]["songName"]+" by "+songList[songCodes[url]]["songArtist"])
print("changedNames:-----------------------------------")
for show in nameChangeList:
    print(show[0]+" "+show[1]+"-> Names Lost: "+str(show[2])+" Names Gained: "+str(show[3]))
print("newLoading:-----------------------------------")
for song in newLoadingList:
    print(song["animeEnglishName"]+": "+song["songName"]+" by "+song["songArtist"])
print("Deprecated:-----------------------------------")
for song in deadSongs:
    print(song["animeEnglishName"]+": "+song["songName"]+" by "+song["songArtist"])
