import sys
import json
import random

#read number of new songs (default 15)
songCount = 15
if len(sys.argv) > 1:
    songCount = int(sys.argv[1])

#read files
with open("loading.json", 'r', encoding = 'utf8') as f:
    loadingList = json.load(f)
with open("known.json", 'r', encoding = 'utf8') as f:
    knownList = json.load(f)

#get song samples
newSongs = random.sample(loadingList, songCount)
nameMap = []
mirrorMap = []
for song in newSongs:
    nameMap.append(song["animeEnglishName"]+song["songName"])
    mirrorMap.append(song["songArtist"]+song["songName"])

#get all songs similar to the songs in sample
newSongList = []
loadingSongList = []
for song in loadingList:
    if song["animeEnglishName"]+song["songName"] in nameMap or song["songArtist"]+song["songName"] in mirrorMap:
        newSongList.append(song)
    else:
        loadingSongList.append(song)
knownList += newSongList

#rewrite files
with open("known.json", 'w', encoding = 'utf8') as f:
    json.dump(knownList, f)
with open("known.json", 'r', encoding = 'utf8') as f:
    filedata = f.read()
filedata = filedata.replace(", {","\n,{")
filedata = filedata.replace("}]","}\n]")
with open("known.json", 'w', encoding = 'utf8') as f:
    f.write(filedata)

with open("loading.json", 'w', encoding = 'utf8') as f:
    json.dump(loadingSongList, f)
with open("loading.json", 'r', encoding = 'utf8') as f:
    filedata = f.read()
filedata = filedata.replace(", {","\n,{")
filedata = filedata.replace("}]","}\n]")
with open("loading.json", 'w', encoding = 'utf8') as f:
    f.write(filedata)

#print added songlist
print("Added Songs:")
for song in newSongList:
    print(song["animeEnglishName"]+": "+song["songName"]+" by "+song["songArtist"])
