import json
import re
newshow = input("Name: ").lower()
with open("shortcuts.json","r") as file:
    data = json.load(file)
for show in data:
    if len(show['name']) < len(newshow) or (len(show['name']) == len(newshow) and show['name'] <= newshow):
        continue
    regexstring = ".*"
    cut = show['shortcut']
    for i in range(len(cut)):
        if cut[i] not in "ouac e\'n2i3xb.^$*+?[]|()\\-&!~\"":
            regexstring += cut[i]
        elif cut[i] == 'o':
            regexstring += "([oōóòöôøΦ]|ou|oo)"
        elif cut[i] == 'u':
            regexstring += "([uūûúùüǖ]|uu)"
        elif cut[i] == 'a':
            regexstring += '[aä@âàáạåæā]'
        elif cut[i] == 'c':
            regexstring += '[cč]'
        elif cut[i] == ' ':
            regexstring += '( ?[★☆\\/\\*=\\+·♥∽・〜†×♪→␣:;~\\-?,.!@_#]+ ?| )'
        elif cut[i] == 'e':
            regexstring += '[eéêëèæē]'
        elif cut[i] == '\'':
            regexstring += '[\'’]'
        elif cut[i] == 'n':
            regexstring += '[nñ]'
        elif cut[i] == '2':
            regexstring += '[2²]'
        elif cut[i] == 'i':
            regexstring += '[ií]'
        elif cut[i] == '3':
            regexstring += '[3³]'
        elif cut[i] == 'x':
            regexstring += '[x×]'
        elif cut[i] == 'b':
            regexstring += '[bß]'
        elif cut[i] == '.':
            regexstring += '\\.'
        elif cut[i] == '^':
            regexstring += '\\^'
        elif cut[i] == '$':
            regexstring += '\\$'
        elif cut[i] == '*':
            regexstring += '\\*'
        elif cut[i] == '+':
            regexstring += '\\+'
        elif cut[i] == '?':
            regexstring += '\\?'
        elif cut[i] == '[':
            regexstring += '\\['
        elif cut[i] == ']':
            regexstring += '\\]'
        elif cut[i] == '|':
            regexstring += '\\|'
        elif cut[i] == '(':
            regexstring += '\\('
        elif cut[i] == ')':
            regexstring += '\\)'
        elif cut[i] == '\\':
            regexstring += '\\\\'
        elif cut[i] == '-':
            regexstring += '\\-'
        elif cut[i] == '&':
            regexstring += '\\&'
        elif cut[i] == '!':
            regexstring += '\\!'
        elif cut[i] == '~':
            regexstring += '\\~'
        elif cut[i] == '"':
            regexstring += '\"'
    regexstring += ".*"
    pattern = re.compile(regexstring)
    if pattern.search(newshow):
        print("    ", end = "")
        print(show['allnames'])
