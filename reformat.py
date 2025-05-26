import json

'''
fileList = ["0","10","20","30","40","50","60","70","80","90","100","last"]
fileTarget = "filePool"
'''
fileList = ["dummy0", "dummy1"]
fileTarget = "dummyPool"

songWeightsMap = dict()
for file in fileList:
    with open(file+"cutlist.json", 'r', encoding = 'utf8') as f:
        songList = json.load(f)
        for song in songList:
            if song["annSongId"] in songWeightsMap:
                songWeightsMap[song["annSongId"]].append(song["D"])
            else:
                songWeightsMap[song["annSongId"]] = [song["D"]]

with open(fileList[0]+"cutlist.json", 'r', encoding = 'utf8') as f:
    songList = json.load(f)
    for index, song in enumerate(songList):
        songList[index]["sampleWeights"] = songWeightsMap[song["annSongId"]]
        songList[index]["D"] = sum(songWeightsMap[song["annSongId"]])

with open(fileTarget+".json", 'r+', encoding = 'utf8') as f:
    f.truncate(0)
    f.seek(0)
    json.dump(songList,f,ensure_ascii=False)
    f.seek(0)
    fileData = f.read()
    fileData = fileData.replace(", {","\n,{")
    fileData = fileData.replace("}]","}\n]")
    f.seek(0)
    f.write(fileData)
   
