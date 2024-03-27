import random
import math
import statistics
import json
import fileinput

#updating learnedcutlist.json
filelist = [0,10,20,30,40,50,60,70,80,90,100,"last","loading"]
includedSongs = set()

# read songs from files and add them to a set
for filename in filelist:
    with open(str(filename)+"cutlist.json",'r', encoding='utf8') as f:
        data = json.load(f)
        for entry in data:
            includedSongs.add(entry["video720"])

#read list of all songs
with open("merged.json",'r', encoding = 'utf8') as f:
    allSongs = json.load(f)

#put learnedcut songs in a list
learnedcutSongs = []
for entry in allSongs:
    if entry["video720"] not in includedSongs:
        learnedcutSongs.append(entry)

#write data to json file
with open("learnedcutlist.json", 'w', encoding = 'utf8') as f:
    json.dump(learnedcutSongs, f)

#correct formatting
with open("learnedcutlist.json", 'r', encoding = 'utf8') as f:
    filedata = f.read()
filedata = filedata.replace(", {","\n,{")
filedata = filedata.replace("}]","}\n]")
with open("learnedcutlist.json", 'w', encoding = 'utf8') as f:
    f.write(filedata)

#actually picking the list
lists = [0,10,20,30,40,50,60,70,80,90,100,'last','learned']
weightl = []
rweightl = []
learnedsize = 0
index = -1
for file in lists:
  with open((str(file)+"cutlist.json"),'r', encoding = 'utf-8') as f:
    weightl.append(1)
    rweightl.append(len(f.readlines())-2)
  f.close()
learnedsize = rweightl.pop()+1
songmin = min(rweightl)+1
songmax = max(rweightl)+1
songmean = math.floor(statistics.mean(rweightl)+1)
songtotal = sum(rweightl)+len(rweightl)
r = random.choices(range(len(lists)), weights = weightl)[0]
for i in range(len(rweightl)):
    rweightl[i] = rweightl[i]*rweightl[i]
r2 = random.choices(range(len(lists)-1),weights = rweightl)[0]
for i in range(len(rweightl)):
    rweightl[i] = int(math.sqrt(rweightl[i]))
rweightl.append(min(learnedsize,songmax))

#create random song selection from selected list
file = str(lists[r])+"cutlist.json"
songCount = math.ceil((math.sqrt(rweightl[r])))
totalSongs = rweightl[r]
permutation = list(range(totalSongs))
random.shuffle(permutation)

with open(file,'r', encoding = 'utf8') as f:
    data1 = json.load(f)
songs = set()
index = 0
songlist = []
while index<math.floor(totalSongs*3/4) and len(songlist) < songCount:
    if data1[permutation[index]]["video720"] not in songs:
        songs.add(data1[permutation[index]]["video720"])
        songlist.append(data1[permutation[index]])
    index+=1

file2 = str(lists[r2])+"cutlist.json"
with open(file2,'r', encoding = 'utf8') as f:
    data1 = json.load(f)
random.shuffle(permutation)
while index<totalSongs and len(songlist) < songCount:
    if data1[permutation[index]]["video720"] not in songs:
        songs.add(data1[permutation[index]]["video720"])
        songlist.append(data1[permutation[index]])
    index+=1
with open("_quiz.json", 'w', encoding = 'utf8') as f:
    json.dump(songlist, f)

#clear practice list
with open("_practice.json", 'w', encoding = 'utf8') as f:
    f.write("]")

#print out the randomized practice stataistics
print("Test the "+str(lists[r2])+" section which has "+str(rweightl[r])+" songs.\nMin: "+str(songmin)+" Mean: "+str(songmean)+" Max: "+str(songmax)+" Total: "+str(songtotal)+" Learned: "+str(learnedsize))
