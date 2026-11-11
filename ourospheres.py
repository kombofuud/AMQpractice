#computes optimal strategy for ourospheres
#red=156
#orange=96
#yellow=61
#green=41
#teal=26
#blue=16

import math

marbleValues = (16,26,41,61,96,156)

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

def legalList(colorIndices, colors):
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

def redCenterCombinations(colorIndices, colors):
    centerPool = legalList(colorIndices, colors)
    centerWeights = []
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
        diagLength = 6
        if i//5 in (0,4) or i%5 in (0,4):
            diagLength = 4
        adjLength = 4-(i//5 in (0,4))-(i%5 in (0,4))
        #compute number of combination next
        centerWeights.append(math.comb(adjLength-len(adj), 2-adj.count(4))*math.comb(6-len(horiz)-len(adj)+adj.count(4),4-adj.count(2)-horiz.count(2))*math.comb(diagLength-len(diag),3-diag.count(3))/math.comb(diagLength,3)/math.comb(adjLength,2))
    return centerPool, centerWeights

def tealCount(colorIndices, colors, center):
    hCount = 0
    dCount = 0
    for pos, color in zip(colorIndices, colors):
        if color != 1:
            continue
        if center%5 == pos%5 or center//5 == pos//5:
            hCount += 1
        else:
            dCount += 1
    return hCount, dCount
def adjCounter(colorIndices, colors, center):
    adjCount = 0
    for pos in colorIndices:
        if abs(center%5-pos%5)+abs(center//5-pos//5) == 1:
            adjCount += 1
    return adjCount

def squareExpectedValues(colorIndices, colors):
    if len(colorIndices) == 5:
        return [0]
    centerList, centerWeights = redCenterCombinations(colorIndices, colors)
    centerWeightTotal = sum(centerWeights)
    if centerWeightTotal == 0:
        return [0]*(25-len(colorIndices))
    guessList = [x for x in range(25) if x not in colorIndices]
    if len(colors)==0:
        guessList = [0,1,2,6,7,12]
    oCount = colors.count(4)
    yCount = colors.count(3)
    gCount = colors.count(2)
    guessEVs = []
    for guess in guessList:
        pList = [0,0,0,0,0,0]
        for center, weight in zip(centerList, centerWeights):
            hTeal, dTeal = tealCount(colorIndices, colors, center)
            aCount = adjCounter(colorIndices, colors, center)
            if center == guess:
                pList[5] += weight/centerWeightTotal
            elif abs(center%5-guess%5) + abs(center//5-guess//5) == 1:
                adjLength = 4-(center%5 in (0,4))-(center//5 in (0,4))
                pList[4] += weight/centerWeightTotal*(2-oCount)/(adjLength-aCount)
                pList[1] += weight/centerWeightTotal*(adjLength+oCount-aCount-2)/(adjLength-aCount)*(2-hTeal)/(6-gCount-hTeal)
                pList[2] += weight/centerWeightTotal*(adjLength+oCount-aCount-2)/(adjLength-aCount)*(4-gCount)/(6-gCount-hTeal)
            elif abs(center%5-guess%5) ==  abs(center//5-guess//5):
                diagLength = 6-2*(center%5 in (0,4) or center//5 in (0,4))
                pList[1] += weight/centerWeightTotal*(diagLength-3-dTeal)/(diagLength-yCount-dTeal)
                pList[3] += weight/centerWeightTotal*(3-yCount)/(diagLength-yCount-dTeal)
            elif center%5 == guess%5 or center//5 == guess//5:
                pList[1] += weight/centerWeightTotal*(2-hTeal)/(6-gCount-hTeal)
                pList[2] += weight/centerWeightTotal*(4-gCount)/(6-gCount-hTeal)
            else:
                pList[0] += weight/centerWeightTotal
        ev = 0
        for i in range(5):
            if pList[i] == 0:
                continue
            ev += pList[i] * (marbleValues[i]+max(squareExpectedValues(colorIndices+[guess], colors+[i])))
        if pList[5] != 0:
            hTeal, dTeal = tealCount(colorIndices, colors, guess)
            ev += pList[5]*(156+EVRed(oCount, yCount, gCount, hTeal, dTeal, 6-2*(guess%5 in (0,4) or guess//5 in (0,4))-yCount-dTeal, 4-(guess%5 in (0,4))-(guess//5 in (0,4))-adjCounter(colorIndices, colors, guess), 4-len(colorIndices)))
        guessEVs.append(ev)
    return guessEVs

def display(colorIndices, colors):
    EVs = squareExpectedValues(colorIndices, colors)
    redSpots = legalList(colorIndices, colors)
    if len(colors) == 0:
        EVs = [EVs[0], EVs[1], EVs[2], EVs[1], EVs[0], EVs[1], EVs[3], EVs[4], EVs[3], EVs[1], EVs[2], EVs[4], EVs[5], EVs[4], EVs[2], EVs[1], EVs[3], EVs[4], EVs[3], EVs[1], EVs[0], EVs[1], EVs[2], EVs[1], EVs[0]]
    j = 0
    myArray = []
    for i in range(25):
        if i in colorIndices:
            myArray.append(["Blue", "Teal", "Green", "Yellow", "Orange", "Red"][colors[colorIndices.index(i)]])
        else:
            myArray.append(round(EVs[j], 4))
            j+=1
    if len(redSpots) == 1 and round(myArray[redSpots[0]],4) == round(max(EVs),4):
        print(f"Max: \033[31m {redSpots[0]}\033[0m, {round(max(EVs),4)}")
    else:
        print(f"Max: {myArray.index(round(max(EVs),4))}, {round(max(EVs),4)}")
        print(redCenterCombinations(colorIndices, colors))
    matrix = [myArray[i : i + 5] for i in range(0, len(myArray), 5)]
    for row in matrix:
        print("".join(f"{val:<10}" for val in row))

#print(legalList([1,5,6],[4,4,3]))
#print(redCenterCombinations([],[]))
#print(squareExpectedValues([1,5,6],[4,4,3]))
display([6,18],[3,3])
