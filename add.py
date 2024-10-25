import sys
import json
import random


fileList = ["0","10","20","30","40","50","60","70","80","90","100","last"]
fileLoad = "loadingcutlist"
fileLearned = "learned"
'''
fileList = ["dummy0", "dummy1"]
fileLoad = "dummyLoad"
fileLearned = "dummyLearned"
'''
filePrep = "_preplist"
#read number of new songs (default 15)
songCount = 0
if len(sys.argv) > 1:
    songCount = int(sys.argv[1])

#read files
nameSet = set()
mirrorSet = set()
urlSet = set()
with open(fileLoad+".json", 'r', encoding = 'utf8') as f:
    loadingList = json.load(f)
for file in fileList+[fileLearned]:
    with open(file+"cutlist.json", 'r', encoding = 'utf8') as f:
        tempList = json.load(f)
        for song in tempList:
            nameSet.add(song["animeEnglishName"]+song["songName"])
            mirrorSet.add(song["songArtist"]+song["songName"])
            urlSet.add(song["video720"])

#get song samples
newSongs = random.sample(loadingList, min(songCount,len(loadingList)))
for song in newSongs:
    nameSet.add(song["animeEnglishName"]+song["songName"])
    mirrorSet.add(song["songArtist"]+song["songName"])

#get all songs similar to the songs in sample
newSongList = []
loadingSongList = []
duplicateSet = set()
for song in loadingList:
    if song["video720"] in duplicateSet:
        print(song["songName"])
        continue
    if song["animeEnglishName"]+song["songName"] in nameSet or song["songArtist"]+song["songName"] in mirrorSet:
        newSongList.append(song)
    else:
        loadingSongList.append(song)
    duplicateSet.add(song["video720"])

#rewrite files
for section in fileList:
    with open(section+"cutlist.json", 'r+', encoding = 'utf8') as f:
        if section != fileLearned:
            knownList = json.load(f)
            knownList.extend(newSongList)
            f.truncate(0)
            f.seek(0)
            json.dump(knownList,f,ensure_ascii=False)
        f.seek(0)
        fileData = f.read()
        fileData = fileData.replace(", {","\n,{")
        fileData = fileData.replace("}]","}\n]")
        f.seek(0)
        f.write(fileData)

with open(fileLoad+".json", 'w', encoding = 'utf8') as f:
    json.dump(loadingSongList, f, ensure_ascii=False)
with open(fileLoad+".json", 'r', encoding = 'utf8') as f:
    filedata = f.read()
filedata = filedata.replace(", {","\n,{")
filedata = filedata.replace("}]","}\n]")
with open(fileLoad+".json", 'w', encoding = 'utf8') as f:
    f.write(filedata)

with open(filePrep+".json", 'w', encoding = 'utf8') as f:
    json.dump(newSongList, f, ensure_ascii=False)
with open(filePrep+".json", 'r', encoding = 'utf8') as f:
    filedata = f.read()
filedata = filedata.replace(", {","\n,{")
filedata = filedata.replace("}]","}\n]")
with open(filePrep+".json", 'w', encoding = 'utf8') as f:
    f.write(filedata)

#print added songlist
print("Added Songs:")
for song in newSongList:
    print(song["animeEnglishName"]+": "+song["songName"]+" by "+song["songArtist"])
print(str(len(loadingSongList))+" songs in Loading. "+ str(len(urlSet)+len(newSongList))+" songs in circulation.")
