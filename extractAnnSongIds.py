with open("pool.json", 'r', encoding = 'utf8') as f:
    known = json.load(f)

idList = [str(song["annSongId"]) for song in known]
idString = "\n".join(idList)

with open("annSongIds.txt", 'w', encoding = 'utf8') as f:
    f.write(idString)
