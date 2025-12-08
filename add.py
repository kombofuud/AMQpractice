import json
import sys

filePool = "pool"
filePrep = "preplist"
fileLoad = "loadingcutlist"
with open(filePrep+".json", 'r', encoding = 'utf8') as f:
    prepSongs = json.load(f)
    elementNull = prepSongs.pop(0)
with open(fileLoad+".json", 'r', encoding = 'utf8') as f:
    loadingSongs = json.load(f)
loadingSongs.sort(key = lambda x: (x["ST"], x["STN"] if x["STN"] is not None else 0, x["rebroadcast"]), reverse = True)
with open(filePool+".json", 'r', encoding = 'utf8') as f:
    songPool = json.load(f)

includedSet = set()
for song in prepSongs:
    includedSet.add(song["malId"])

loadingMap = {}
for i, song in enumerate(loadingSongs):
    loadingMap[song["malId"]] = i

missingSet = set()
for song in songPool:
    if song["malId"] not in includedSet and song["malId"] in loadingMap:
        missingSet.add(song["malId"])

missingList = list(missingSet)
for ID in missingList:
    print(f"ID={ID} had undetected songs")
malids = sys.argv[1:]

malids.extend(missingList)
indexList = []
for ID in malids:
    ID = int(ID)
    if ID in includedSet:
        print(f"ID={ID} is already in preplist")
        continue
    if ID not in loadingMap:
        print(f"ID={ID} has no songs")
        continue
    if loadingMap[ID] in indexList:
        print(f"ID={ID} was duplicated")
        continue
    indexList.append(loadingMap[ID])
indexList.sort(reverse = True)
for ID in indexList:
    prepSongs.append(loadingSongs.pop(ID))

with open(filePrep+".json", 'r+', encoding = 'utf8') as f:
    f.truncate(0)
    f.seek(0)
    prepSongs.insert(0, elementNull)
    json.dump(prepSongs,f,ensure_ascii=False)
    f.seek(0)
    fileData = f.read()
    fileData = fileData.replace(", {","\n,{")
    fileData = fileData.replace("}]","}\n]")
    f.seek(0)
    f.write(fileData)

with open(fileLoad+".json", 'r+', encoding = 'utf8') as f:
    f.truncate(0)
    f.seek(0)
    loadingSongs.sort(key = lambda x : x["songDifficulty"], reverse=True)
    json.dump(loadingSongs,f,ensure_ascii=False)
    f.seek(0)
    fileData = f.read()
    fileData = fileData.replace(", {","\n,{")
    fileData = fileData.replace("}]","}\n]")
    f.seek(0)
    f.write(fileData)

print(f"{len(indexList)} songs added. {len(malids)-len(indexList)} skipped")
