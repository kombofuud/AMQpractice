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
filePrep = "preplist"
prepListSize = 50

#read number of new songs (default 0)
songCount = 0
if len(sys.argv) > 1:
    songCount = int(sys.argv[1])

#read files
nameSet = set()
mirrorSet = set()
urlSet = set()
with open(fileLoad+".json", 'r', encoding = 'utf8') as f:
    loadingList = json.load(f)
with open(filePrep+".json", 'r', encoding = 'utf8') as f:
    prepList = json.load(f)
songCounter = 0
uniqueSongCounter = 0
learnedCounter = 0
for file in fileList+[fileLearned]:
    with open(file+"cutlist.json", 'r', encoding = 'utf8') as f:
        tempList = json.load(f)
        countingSet = set()
        for song in tempList:
            nameSet.add(song["animeEnglishName"]+song["songName"])
            mirrorSet.add(song["songArtist"]+song["songName"])
            urlSet.add(song["video720"])
            if file != fileLearned:
                songCounter += 1
                if song["video720"] not in countingSet:
                    countingSet.add(song["video720"])
                    uniqueSongCounter += 1
            else:
                learnedCounter += 1

#get song samples
newPrep = random.sample(loadingList, max(0,min(songCount+prepListSize-len(prepList),len(loadingList),prepListSize)))
newSongs = prepList[:min(len(prepList),songCount)]
newPrepList = prepList[min(len(prepList),songCount):]+newPrep
prepList.extend(newSongs)
for song in prepList:
    '''nameSet.add(song["animeEnglishName"]+song["songName"])
    mirrorSet.add(song["songArtist"]+song["songName"])'''
    urlSet.add(song["video720"])

#get all songs similar to the songs in sample (deprecated)
'newSongList = []'
loadingSongList = []
duplicateSet = set()
for song in loadingList:
    if song["video720"] in duplicateSet:
        print(song["songName"])
        continue
    '''if song["animeEnglishName"]+song["songName"] in nameSet or song["songArtist"]+song["songName"] in mirrorSet:
        newSongList.append(song)'''
    if song["video720"] not in urlSet:
        loadingSongList.append(song)
    duplicateSet.add(song["video720"])

#rewrite files
for section in fileList:
    with open(section+"cutlist.json", 'r+', encoding = 'utf8') as f:
        if section != fileLearned:
            knownList = json.load(f)
            knownList.extend(newSongs)
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
    json.dump(newPrepList, f, ensure_ascii=False)
with open(filePrep+".json", 'r', encoding = 'utf8') as f:
    filedata = f.read()
filedata = filedata.replace(", {","\n,{")
filedata = filedata.replace("}]","}\n]")
with open(filePrep+".json", 'w', encoding = 'utf8') as f:
    f.write(filedata)

#print added songlist
print("Added Songs:")
for song in newSongs:
    print(song["animeEnglishName"]+": "+song["songName"]+" by "+song["songArtist"])
print("Raw average songCount: "+str(round(songCounter/len(fileList)+len(newSongs),4))+". Unique average SongCount: "+str(round(uniqueSongCounter/len(fileList)+len(newSongs),4))+".")
print(str(len(loadingSongList))+" songs in Loading. "+ str(len(urlSet)+len(newSongs)-learnedCounter)+" songs in circulation. "+str(len(newPrepList))+" songs on standby.")
