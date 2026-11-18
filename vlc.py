import json

with open("vlcJson.json", 'r', encoding = 'utf8') as f:
    learning = json.load(f)
    learning.pop(0)

learning.reverse()
with open("vlcList.m3u", "w", encoding = 'utf8') as f:
    f.write("#EXTM3U\n")
    for song in learning:
        f.write(f"#EXTINF:-1, {song["songName"]} from {song["animeEnglishName"]} by {song["songArtist"]}\n")
        f.write(f"https://nawdist.animemusicquiz.com/{song["audio"]}\n")
