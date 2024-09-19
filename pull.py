import os
import json
import shutil

#Move downloaded file to local directory and delete previous version
shutil.move(r"..\..\..\Downloads\merged.json","merged.json")

#load songs from each list
with open("merged.json", 'r', encoding = 'utf8') as f:
    songList = json.load(f)
with open("known.json", 'r', encoding = 'utf8') as f:
    knownList = json.load(f)
with open("loading.json", 'r', encoding = 'utf8') as f:
    loadingList = json.load(f)
with open("modifications.json", 'r', encoding = 'utf8') as f:
    equivalances = json.load(f)

#load equivalence mapping
equiv = dict()
index = 0
altNames = []
for relation in equivalances:
    for name in relation["equiv"]:
        equiv[name] = index
    index += 1
    altNames.append(set())

#prepare new lists
newKnownList = []
newLoadingList = []
newList = []
for song in songList:
    if song["video720"] is None:
        song["video720"] = song["video480"]
    if song["animeVintage"] is None:
        song["animeVintage"] = ""
    if song["songArtist"]+song["songName"] in equiv:
        for name in song["altAnimeNames"]:
           altNames[equiv[song["songArtist"]+song["songName"]]].add(name)
for song in songList:
    if song["songArtist"]+song["songName"] in equiv:
        song["altAnimeNamesAnswers"] = list(altNames[equiv[song["songArtist"]+song["songName"]]])

nameMap = []
mirrorMap = []
urlMap = []
vintageMap = []
for song in knownList:
    urlMap.append(song["video720"])
    nameMap.append(song["animeEnglishName"]+song["songName"])
    mirrorMap.append(song["songArtist"]+song["songName"])
    vintageMap.append(song["songArtist"]+song["songName"]+song["animeVintage"])

for song in loadingList:
    urlMap.append(song["video720"])
    vintageMap.append(song["animeEnglishName"]+song["songName"])

#add songs to respective lists by url
for song in songList:
    if song["animeEnglishName"]+song["songName"] in nameMap or song["songArtist"]+song["songName"] in mirrorMap:
        newKnownList.append(song)
    else:
        newLoadingList.append(song)
    if song["songArtist"]+song["songName"]+song["animeVintage"] not in vintageMap and song["video720"] not in urlMap:
        newList.append(song)

#Write songs to files
with open("known.json", 'w', encoding = 'utf8') as f:
    json.dump(newKnownList, f)
with open("known.json", 'r', encoding = 'utf8') as f:
    filedata = f.read()
filedata = filedata.replace(", {","\n,{")
filedata = filedata.replace("}]","}\n]")
with open("known.json", 'w', encoding = 'utf8') as f:
    f.write(filedata)

with open("loading.json", 'w', encoding = 'utf8') as f:
    json.dump(newLoadingList, f)
with open("loading.json", 'r', encoding = 'utf8') as f:
    filedata = f.read()
filedata = filedata.replace(", {","\n,{")
filedata = filedata.replace("}]","}\n]")
with open("loading.json", 'w', encoding = 'utf8') as f:
    f.write(filedata)

with open("merged.json", 'w', encoding = 'utf8') as f:
    json.dump(songList, f)
with open("merged.json", 'r', encoding = 'utf8') as f:
    filedata = f.read()
filedata = filedata.replace(", {","\n,{")
filedata = filedata.replace("}]","}\n]")
with open("merged.json", 'w', encoding = 'utf8') as f:
    f.write(filedata)

#Print out new songs
print("newSongs:")
for song in newList:
    print(song["animeEnglishName"]+": "+song["songName"]+" by "+song["songArtist"])
