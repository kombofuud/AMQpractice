import numpy as np

sampleSize = 1000000
pity = [99]*sampleSize
wishCount = [0]*sampleSize

legendaryMiyu = np.random.geometric(p=0.005*(1/2+1/17), size = sampleSize)
epicMiyu = np.random.geometric(p=0.0028125, size = sampleSize)
epicRin = np.random.geometric(p=0.01125, size = sampleSize)

def LegendaryMiyu(i):
    if 2*legendaryMiyu[i]+pity[i] > 500:
        wishCount[i] += 500-pity[i]
        pity[i] = pity[i]%2

    else:
        wishCount[i] += legendaryMiyu[i]
        pity[i] = (int)((pity[i]+1)/2)
        pity[i] += legendaryMiyu[i]

def EpicMiyu(i):
    if 2*epicMiyu[i]+pity[i] > 200:
        wishCount[i] += max(0,200-pity[i])
        pity[i] = max(0,(int)((pity[i]-199)/2))
    else:
        wishCount[i] += epicMiyu[i]
        pity[i] = (int)((pity[i]+1)/2)
        pity[i] += epicMiyu[i]

def EpicRin(i):
    if 2*epicRin[i]+pity[i] > 200:
        wishCount[i] += max(0,200-pity[i])
        pity[i] = max(0,(int)((pity[i]-199)/2))
    else:
        wishCount[i] += epicRin[i]
        pity[i] = (int)((pity[i]+1)/2)
        pity[i] += epicRin[i]

for i in range(sampleSize):
    LegendaryMiyu(i)
    if pity[i] < 52:
        EpicRin(i)
        EpicMiyu(i)
    else:
        EpicMiyu(i)
        EpicRin(i)

print(np.mean(wishCount))
