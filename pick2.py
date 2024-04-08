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
print(rweightl)
sqweight = copy.deepcopy(rweightl)
for i in range(len(sqweight)):
    sqweight[i] = sqweight[i]*sqweight[i]
sqweight.pop()
r = random.choices(range(len(lists)-1), weights = sqweight)[0]
weightl[r] = 0
s = random.sample(range(len(lists)),k=4)
for i in range(4):
    if i==3 or s[i]==r:
        s.pop(i)
        break

#create random song selection from selected list
files = [str(lists[s[0]])+"cutlist.json", str(lists[s[1]])+"cutlist.json", str(lists[s[2]])+"cutlist.json", str(lists[r])+"cutlist.json"]
fileindices = s+[r]
songCounts = [math.ceil(math.sqrt(rweightl[s[0]])/3), math.ceil(math.sqrt(rweightl[s[1]])/3), math.ceil(math.sqrt(rweightl[s[2]])/3), math.ceil(math.sqrt(rweightl[r])/2)]
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
