import random
import math
import statistics
import json
import fileinput
import copy

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
learnedsize = rweightl[-1]+1
songmin = min(rweightl[:12])+1
songmax = max(rweightl[:12])+1
songmean = math.floor(statistics.mean(rweightl[:12])+1)
songtotal = sum(rweightl[:12])+len(rweightl[:12])
#selecting the target list
rweightl[-1] = min(songmean, rweightl[-1])
sqweight = copy.deepcopy(rweightl)
for i in range(len(sqweight)):
    sqweight[i] = sqweight[i]*sqweight[i]
sqweight.pop()
r = random.choices(range(len(lists)-1), weights = sqweight)[0]
s = random.sample(range(len(lists)),k=6)
for i in range(6):
    if s[i]==r:
        s.pop(i)
i = 0
while len(s) > 4:
    if math.abs(s[i]-r) > 1 or s[i] = len(lists)-1:
        s.pop(i)
    else
        i+=1

#create random song selection from selected list
fileindices = s+[r]
files = []
for i in fileindices:
    files.append(str(lists[i])+"cutlist.json")
songCounts = []
for i in s:
    songCounts.append(math.ceil(math.sqrt(rweightl[i])/4))
songCounts.append(math.ceil(math.sqrt(rweightl[r])*2/3))
totalSongs = rweightl[r]
songs = set()
practicesonglist = []
fileindex = 0

for file in files:
    with open(file, 'r', encoding = 'utf8') as f:
        data1 = json.load(f)
    index = 0
    songlist = []
    permutation = list(range(rweightl[fileindices[fileindex]]))
    random.shuffle(permutation)
    while index<len(permutation) and len(songlist) < songCounts[fileindex]:
        if data1[permutation[index]]["video720"] not in songs:
            songs.add(data1[permutation[index]]["video720"])
            songlist.append(data1[permutation[index]])
        index+=1
    practicesonglist += songlist
    fileindex+=1
    
with open("_quiz.json", 'w', encoding = 'utf8') as f:
    json.dump(practicesonglist, f)
#clear practice list
with open("_practice.json", 'w', encoding = 'utf8') as f:
    f.write("]")

#print out the randomized practice stataistics
print("Test the "+str(lists[r])+" section which has "+str(rweightl[r]+1)+" songs.\nMin: "+str(songmin)+" Mean: "+str(songmean)+" Max: "+str(songmax)+" Total: "+str(songtotal)+" Learned: "+str(learnedsize))
