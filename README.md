This is a program I made for personal use that is designed to be used alongside the CSL extension (https://github.com/amq-script-project/AMQ-Scripts/blob/master/gameplay/amqAutocomplete.user.js) for AnimeMusicQuiz (https://animemusicquiz.com/) which can be installed via Tampermonkey.
The purpose of this program is to help me effectively randomize the shows so that I am more likely to practice songs which I am less familiar with, but still have a chance to get songs that I haven't seen in a while

The following python programs have varying utilities
Pick2.py - Updates all learned songs. And creates a rewrites quiz.json to be utilized for practice. (note when the program says "practice on the 40" section, this means that the "sample" setting should go from 30-40, this holds for all other sections with 2 exceptions: 0 section means the sample is just 0, and last means the sample is 100.
      During (or after) gameplay, I open up the corresponding file in vim which I am playing the quiz on (i.e. if I'm practicing on 30-40 section, I'll open up 40cutlist in vim). Then, if I miss a song, I double the number of times it appears. If I get it right (and it is within the section), I halve the number of times it appears. (if it appears once, I delete it). If I miss the song, I additionally add it to a practice list so I can focus on the songs I missed in a game.

new.py - utilizing the ability of csl to download new songs, this program takes a downloaded song list and appends it to the loading and merged song lists. It is noted that this program reads the json file like a txt file, so it needs to be reformatted prior to download. (Each song is on a new line, the first bracket initilizing the json list is replaced with a comma, the bracket ending the json file is deleted.) I usually do the reformatting manually since shows sometimes have missing information.

add.py - when I want to add songs from loadinglist.json into the practice lists, I put them into _preplist.json (formatted in the same way as in new.py) and then this program adds them to all the practice lists.

fast.py - checks to see if a new songname would override any of the shortcuts listed in shortcuts.json
