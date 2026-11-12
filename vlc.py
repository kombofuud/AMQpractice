import json

with open("preplist.json", 'r', encoding = 'utf8') as f:
    learning = json.load(f)
    learning.pop(0)

learning.reverse()
with open("vlcList.m3u", "r+", encoding = 'utf8') as f:
    song_count = (sum(1 for line in f)-1)//2
    learning = learning[:22-song_count]
    f.seek(0,2)
    for song in learning:
        f.write(f"#EXTINF:-1, {song["songName"]} from {song["animeEnglishName"]} by {song["songArtist"]}\n")
        f.write(f"https://nawdist.animemusicquiz.com/{song["audio"]}\n")
