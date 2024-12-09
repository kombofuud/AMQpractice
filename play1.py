import random
import math
import statistics
import json
import fileinput
import copy
import numpy

#Read ALL Files
'''
fileMerged = "merged.json"
fileDead = "dead.json"
fileLearned = "learnedcutlist.json"
filePrep = "preplist.json"
fileLoad = "loadingcutlist.json"
fileList = ["0cutlist.json", "10cutlist.json", "20cutlist.json", "30cutlist.json", "40cutlist.json", "50cutlist.json", "60cutlist.json", "70cutlist.json", "80cutlist.json", "90cutlist.json", "100cutlist.json", "lastcutlist.json"]
'''
fileMerged = "dummyMerged.json"
fileDead = "dummyDead.json"
fileLearned = "dummyLearnedcutlist.json"
filePrep = "dummyPreplist.json"
fileLoad = "dummyLoad.json"
fileList = ["dummy0cutlist.json", "dummy1cutlist.json"]

equivalences = "modifications.json"

#Make list of all songs
with open(fileMerged, "r", encoding="utf-8") as file:
    fullSongList = json.load(file)
songMap = {}
songCounter = []
uniqueSongCounter = []
for index, song in enumerate(fullSongList):
    songMap[song["annSongId"]] = index
    songCounter.append(0)
    uniqueSongCounter.append(0)

#Read all relevant files
for file in fileList:
    with open(file, "r", encoding="utf-8") as file:
        localSongSet = set()
        localSongList = json.load(file)
        for index, song in enumerate(localSongList):
            songCounter[songMap[song["annSongId"]]] += 1
            if song["annSongId"] not in localSongSet:
                localSongSet.add(song["annSongId"])
                uniqueSongCounter[songMap[song["annSongId"]]] += 1
for file in [fileLoad, filePrep]:
    with open(file, "r", encoding="utf-8") as file:
        localSongList = json.load(file)
        for index, song in enumerate(localSongList):
            songCounter[songMap[song["annSongId"]]] += 1

#update LearnedcutList and mark hard songs
learnedList = []
hardList = []
hardCounter = 0
for song in fullSongList:
    if songCounter[songMap[song["annSongId"]]] == 0:
        learnedList.append(song)
        continue
    if songCounter[songMap[song["annSongId"]]]-uniqueSongCounter[songMap[song["annSongId"]]] > 8:
        hardList.append(song)
        hardCounter += uniqueSongCounter[songMap[song["annSongId"]]]

#Get new songs


#Remove hard songs and add new songs
for file in fileList:
    with open(file, "r+", encoding="utf-8") as file:
        localSongList = json.load(file)
        for song in localSongList:
            a