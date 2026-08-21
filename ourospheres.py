#computes optimal strategy for ourospheres
#red=156
#orange=96
#yellow=61
#green=41
#teal=26
#blue=16

def yellowOdds(y, diagCount):
    return (3-y)/diagCount, 1-(3-y)/diagCount

def orangeOddsGivenRed(o, g, adjCount, horizCount):
    pOrange = (2-o)/adjCount
    pGreen= (4-g)/(horizCount-2+o)
    return pOrange, (1-pOrange)*pGreen, (1-pOrange)*(1-pGreen)

def EVRed(o, y, g, horizTeal, diagTeal, diagCount, adjCount, guesses):
    if guesses == 0:
        return 0
    if o== 2:
        pYellow, pTeal = yellowOdds(y, diagCount)
        eYellow = EVRed(2, y+1, g, horizTeal, diagTeal, diagCount-1, adjCount, guesses-1) if pYellow > 0 else 0
        eTeal = EVRed(2, y, g, horizTeal, diagTeal+1, diagCount-1, adjCount, guesses-1) if pTeal > 0 else 0
        return pYellow*(61+eYellow)+pTeal*(26+eTeal)
    else:
        pOrange, pGreen, pTeal = orangeOddsGivenRed(o, g, adjCount, 8-o-g-horizTeal)
        eOrange = EVRed(o+1, y, g, horizTeal, diagTeal, diagCount, adjCount-1, guesses-1) if pOrange > 0 else 0
        eGreen = EVRed(o, y, g+1, horizTeal, diagTeal, diagCount, adjCount-1, guesses-1) if pGreen > 0 else 0
        eTeal = EVRed(o, y, g, horizTeal+1, diagTeal, diagCount, adjCount-1, guesses-1) if pTeal > 0 else 0
        return pOrange*(96+eOrange)+pGreen*(41+eGreen)+pTeal*(26+eTeal)

def legalList(colors, colorIndices):
    legalList = [0,1,2,3,4,5,6,7,8,9,10,11,13,14,15,16,17,18,19,20,21,22,23,24]
    legalList = [x for x in legalList if x not in colorIndices]
    for i in range(len(colorIndices)):
        match colors[i]:
            case 0:
                legalList = [x for x in legalList if x//5 != colorIndices[i]//5 and x%5 != colorIndices[i]%5 and abs(x//5-colorIndices[i]//5) != abs(x%5-colorIndices[i]%5)]
            case 1:
                legalList = [x for x in legalList if x//5 == colorIndices[i]//5 or x%5 == colorIndices[i]%5 or abs(x//5-colorIndices[i]//5) == abs(x%5-colorIndices[i]%5)]
            case 2:
                legalList = [x for x in legalList if x//5 == colorIndices[i]//5 or x%5 == colorIndices[i]%5]
            case 3:
                legalList = [x for x in legalList if abs(x//5-colorIndices[i]//5) == abs(x%5-colorIndices[i]%5)]
            case 4:
                legalList = [x for x in legalList if abs(x//5 - colorIndices[i]//5) + abs(x%5 - colorIndices[i]%5) == 1]
    return legalList

def redCenterOdds(colors, colorIndices):
    centerPool = legalList(colors, colorIndices)
    for i in centerPool:
        adj = []
        horiz = []
        diag = []
        for j in range(len(colors)):
            if abs(i//5 - colorIndices[j]//5) + abs(i%5 - colorIndices[j]%5) == 1:
                adj.append(colors[j])
            elif abs(i//5-colorIndices[j]//5) == abs(i%5-colorIndices[j]%5):
                diag.append(colors[j])
            elif i//5 == colorIndices[j]//5 or i%5 == colorIndices[j]%5:
                horiz.append(colors[j])
        diagLength = 4
        if i//5 in (0,4) or i%5 in (0,4):
            diagLength = 6
        #compute number of combination next
print(legalList([0],[0]))
print(legalList([1],[1]))
print(legalList([2],[2]))
print(legalList([3],[3]))
print(legalList([4],[4]))

'''
def adjOdds(redIndex):
    adj = 4
    if redIndex in [1,2,3,5,9,10,14,15,19,21,22,23]:
        adj = 3
    elif redIndex in [0,4,20,24]:
        adj = 2
    pOrange = 2/adj
    return [0, (1-pOrange)/3,(1-pOrange)*2/3, 0, pOrange, 0]
def diagOdds(redIndex):
    diag = 4
    if redIndex in [6,7,8,11,13,16,17,18]:
        diag = 6
    return [0,(diag-3)/diag,0,3/diag,0,0]

def horizOdds(color):
    return [0,1/3,2/3,0,0,0]

def nothingOdds(color):
    return[1,0,0,0,0,0]

def centerOdds(redIndex, colors, colorIndices):
    odds = 1
    for i in range(len(colorIndices)):
        if abs(redIndex-colorIndices[i]) == 5 or (abs(redIndex-colorIndices[i]) == 1 and abs(redIndex%5-colorIndices[i]%5) == 1):
            odds *= adjOdds(redIndex)[colors[i]]
        elif redIndex // 5 == colorIndices[i]//5 or redIndex%5 == colorIndices[i]%5:
            odds *= horizOdds[colors[i]]
        elif abs(redIndex // 5 - colorIndices[i] // 5) == abs(redIndex%5 - colorIndices[i]%5):
            odds *= diagOdds(redIndex)[colors[i]]
        else:
            odds *= nothingOdds[colors[i]]
        if odds==0:
            return 0
    return odds


def colorOdds(colors, colorIndices, index):
    indexOdds = [0]*6
    for i in range(25):
        if i==13 or i in colorIndices:
            continue
        #looping through possible red centers here
'''
