import math
import numpy as np
import scipy as sp
from scipy import stats
from Biology import *
import time
from matplotlib import pyplot as plt


def intToListOfBits(num):
    if num == 0:
        return [0]
    ret = []
    curVal = num
    while curVal >= 1:
        ret = [curVal%2] + ret
        curVal = curVal/2
    return ret

def killProcess(agent, k1, power):
    dead = 0
    if agent not in agent.tribe.roster:
        print("Not in roster..?")
    if np.random.rand() < (float(agent.tribe.size))**power/float(k1): #Random Death, expected deaths are proportional to P^2/k1
        agent.die()
        dead = 1
    return dead


def sexualReproduction(agent, k1, numNewborns, agentIndex): #Sexual Reproduction
    tribe = agent.tribe
    matingCall = agent.DNA[0]
    children = 0
    dead = 0
    
    potentialPartners = tribe.size - numNewborns
    for i in range(agentIndex, potentialPartners):
        returnCall = tribe.roster[i].DNA[0]
        if agent is tribe.roster[i]:
            x = 0

        elif (matingCall == returnCall).all(): #We found a potential partner :D
            if np.random.rand() < float(k1)/float(potentialPartners):
                agent.reproduce()
                children += 1
    return children



#TERRIBLE!
def div7(agent, arr, k1): #Can our agents detect whether a number is divisible by 7? Not as currently devised...
    tribe = agent.tribe
    m = agent.tribe.m
    n = agent.tribe.n
    accum = 0
    children = 0
    deaths = 0
    
    out = agent.conceptualLogic(arr)
    
    if (num%7 == 0 and out[0] == 1): #Robot is correct!
        if np.random.rand() < k1:
            agent.reproduce()
            children += 1
    elif (num%7 != 0 and out[0] == 0): #Robot is also correct, but this one's easier to guess
        if np.random.rand() < k1/6:
            agent.reproduce()
            children += 1
    else:
        deaths = killProcess(agent, 4, 0)
    return [children, deaths, out[0]]

def passThrough(agent, num):
    tribe = agent.tribe
    m = agent.m
    n = agent.n
    corrects = 0
    out = agent.conceptualLogic(num)
    if agent not in tribe.roster:
        return -10000000
    
    corrects = 0
    for i in range(50):
        corrects += abs(out[i]-num[i])

    return -corrects


popSize = 200
m = 40
n = 10
westerners = Tribe()


for k in range(popSize):
    dna = np.zeros((m,n))
    for i in range(m):
        for j in range(n):
            r = np.random.rand()
            if j in (0,2):
                dna[i][j] = np.random.randint(2)
            elif j in (1,3):
                dna[i][j] = min(int(math.floor(-math.log(1-r,1.05))), (m*(n-6)-1))
            elif j == 4:
                dna[i][j] = np.random.randint(m)
            else:
                dna[i][j] = int(math.ceil(r*6)-0)
    sex = np.random.randint(2)
    a = Agent(westerners,dna,sex)
    westerners.addAgent(a)

#print(westerners.getDNAAverage())
cnt = 1
births = 0
deaths = 0
correctDivides = 0

tArr = []
fitArr = []
popArr = []
baArr = []
thinkArr = []
mArr = []
mBelow = []
mAbove = []

timeReproducing = 0
timeThinking = 0
timeSorting = 0

thinkThreshold = 0.06*np.sin(2*np.pi*cnt/1000 + np.pi/2) + 0.12

outsize = 50
num = [i for i in range(outsize)]

while cnt < 20000:
    i = 0
    if westerners.size == 0:
        break;
    tempRoster = westerners.roster.copy()
    tt = time.time()
    for i in range(westerners.size):
        agent = tempRoster[i]
        if time.time() - tt > thinkThreshold:
            agent.die()
            deaths += 1
            continue
        t = time.time()
        score = passThrough(agent, num)
        elapsed = time.time() - t
        if elapsed > thinkThreshold/(westerners.size) and np.random.rand() < 0.5:
            agent.die()
            deaths += 1
            continue
        agent.fitness = score - 10000*elapsed
    
    # Randomly increase num
    for i in range(len(num)):
        if np.random.rand() < 0.001:
            num[i] = num[i] + 1
        
    timeThinking += time.time() - tt

    #asexualReproduction(agent, 20, 2)

        #d = killProcess(agent, 5000, 1)
        #deaths += d
    ts = time.time()
    westerners.sexuallyRank()
    timeSorting += time.time() - ts
    
    # Implement sexual reproduction
    bestBoyAgentChildren = 0
    sbb = 0
    bbirths = births
    girls = 0
    bmates = np.zeros(westerners.size)
    gmates = np.zeros(westerners.size)
    tr = time.time()
    boys = westerners.getSortedBoys()
    girls = westerners.getSortedGirls()
    for girl in girls:
        if np.random.rand() > len(girls)/(len(girls) + 10*(girl.fitnessRank)):
            continue
        
        p = np.random.poisson(lam=girl.fitnessRank/4)
        partner = min(round(p), len(boys)-1)
        
        for k in range(np.random.randint(5) + 1):
                girl.reproduce(boys[partner])
                births += 1
                #print("Rank " + str(boy.fitnessRank) + " boy mated with rank " + str(girl.fitnessRank) + " girl")
                bmates[boys[partner].fitnessRank-1] += 1
                gmates[girl.fitnessRank-1] += 1
    timeReproducing += time.time() - tr
    cnt += 1
    if (cnt % 10 == 0):
        #print("\n total births are: " + str(births - bbirths))
        for i in range(min(len(boys), len(girls))):
            print("Rank " + str(boys[i].fitnessRank) + " boy wit " + str(int(bmates[i])) + " offspring! and fitness = " + str(boys[i].fitness))
            print("Rank " + str(i) + " girl wit " + str(int(gmates[i])) + " offspring! and fitness = " + str(girls[i].fitness))
    
    
        print("Time step " + str(cnt))
        print("There were " + str(births) + " births and " + str(deaths) + " deaths. Population size now " + str(westerners.size))
        print("Think threshhold: " + str(thinkThreshold))
        avgM = 0
        varM = 0
        for i in range(westerners.size):
            avgM += westerners.roster[i].m/westerners.size
        for i in range(westerners.size):
            varM += ((westerners.roster[i].m - avgM)**2)/westerners.size
        print("Average m: " + str(avgM))
        print("Variance m: " + str(varM))
        bestAgent = westerners.getBestAgent()
        print(np.array(num))
        print(bestAgent.conceptualLogic(num))
        score = 0
        trainingCorrect = 0
    
        print("Best agent fitness: " + str(bestAgent.fitness))
        print("Time reproducing: " + str(timeReproducing))
        print("Time thinking: " + str(timeThinking))
        print("Time sorting: " + str(timeSorting))
        timeReproducing = 0
        timeThinking = 0
        timeSorting = 0
        if (bestAgent.sex == 1):
            print("Best agent is MALE")
        else:
            print("Best agent is FEMALE")
        print("\n\n")
        
        tArr += [cnt]
        fitArr += [score/1000]
        popArr += [westerners.size]
        baArr += [-bestAgent.fitness]
        thinkArr += [1000*thinkThreshold]
        
        mArr += [avgM]
        inter = sp.stats.norm.interval(0.997, loc = avgM, scale = np.sqrt(varM))
        mBelow.append(inter[0])
        mAbove.append(inter[1])
        
        births = 0
        correctDivides = 0
        deaths = 0
    deaths += westerners.killAndGrow(2)
    thinkThreshold = 0.06*np.sin(2*np.pi*cnt/1000 + np.pi/2) + 0.12

#raw_input("Press a key to continue")
bestAgent = westerners.getBestAgent()

num = [k for k in range(outsize)]
o = square(bestAgent, num)
print("Final test")
print("input: " + str(num))
print("output: " + str(bestAgent.conceptualLogic(num)))
print("Score: " + str(o))

print("Best agent DNA: ")
print(bestAgent.DNA)

plt.plot(tArr, popArr, label="population")
plt.plot(tArr, baArr, label="loss kinda")
plt.plot(tArr, thinkArr, label="total thinking time per gen (msec)")

plt.title("Evolution alg")
plt.xlabel("Generation")
plt.ylabel("Various things, arbitrary units")

plt.plot(tArr, mArr, '-g', label="m mean")
plt.fill_between(tArr, mBelow, mAbove, alpha=0.3, label="m dist")

plt.legend(loc='upper right')

plt.show()

#print("Success rate: " + str(float(correct)/20))
#print("Success rate on training data: " + str(float(trainingCorrect)/10))

