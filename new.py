import os
files = ["merged","loadingcutlist"]
with open("../../../Downloads/merged.json","r", encoding='utf-8') as file:
    data = file.read()
    encodedData = data.encode("utf-8")
for f in files:
    f += ".json"
    with open(f,"r+b") as cfile:
        cfile.seek(-4,os.SEEK_END)
        charlist = cfile.read(4)
        fEnd = 0
        for i in range(4):
            if charlist[i] == 93:
                fEnd = i
        cfile.seek(-4+fEnd,os.SEEK_END)
        cfile.truncate()
        cfile.write(encodedData)
        cfile.write(b"]")
print("Written to merged and loading")
