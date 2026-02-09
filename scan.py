import os
import json
import random
from pathlib import Path

downloadFile = Path.home() / "Downloads" / "merged.json"

with open("pool.json", 'r', encoding = 'utf8') as f:
    known = json.load(f)
with open("preplist.json", 'r', encoding = 'utf8') as f:
    learning = json.load(f)
    learning.pop(0)
with open("loadingcutlist.json", 'r', encoding = 'utf8') as f:
    learning.extend(json.load(f))

with open(downloadFile, 'r', encoding = 'utf8') as f:
    playPool = json.load(f)

playMalIds = set()
for song in playPool:
    playMalIds.add(song["malId"])

learningMalIds = set()
print("unfinished MALIDs:__________________")
for song in learning:
    if song["malId"] in playMalIds:
        print(song["malId"])
        playMalIds.remove(song["malId"])
    learningMalIds.add(song["malId"])

print("unadded MALIDs:_____________________")
for song in known:
    if song["malId"] not in playMalIds and song["malId"] not in learningMalIds:
        print(song["malId"])
        playMalIds.add(song["malId"])

os.remove(downloadFile)
