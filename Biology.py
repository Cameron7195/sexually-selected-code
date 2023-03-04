import math
import numpy as np


class Tribe:
    def __init__(self):
        self.roster = [] #Array of agents, with length = size
        self.size = 0
        self.childRoster = []
        self.numChildren = 0
        return

    def addAgent(self, agent):
        self.roster += [agent]
        self.size += 1
        
    def addChild(self, child):
        self.childRoster += [child]
        self.numChildren += 1
        
    def sortKey(self, agent):
        return agent.fitness
        
    def getSortedBoys(self):
        boys = []
        for i in range(self.size):
            if self.roster[i].sex == 1:
                boys += [self.roster[i]]
        boys.sort(key=self.sortKey, reverse=True)
        return boys
    
    def getSortedGirls(self):
        girls = []
        for i in range(self.size):
            if self.roster[i].sex == 0:
                girls += [self.roster[i]]
        girls.sort(key=self.sortKey, reverse=True)
        return girls
        
    def sexuallyRank(self):
        boys = self.getSortedBoys()
        girls = self.getSortedGirls()
        
        r = 1
        for boy in boys:
            boy.fitnessRank = r
            r += 1
        r = 1
        for girl in girls:
            girl.fitnessRank = r
            r += 1
        return
        
    def getBestAgent(self):
        bestAgent = self.roster[0]
        for i in range(self.size):
            if (i == 0):
                continue
            if self.roster[i].fitness >= bestAgent.fitness:
                bestAgent = self.roster[i]
        return bestAgent
        
    def getAvgFitness(self):
        total = 0
        for i in range(self.size):
            # Don't include bottom half of pop
            total += self.roster[i].fitness/self.size
        return total

    def killAndGrow(self, killFraction):
        idx = 0
        killed = 0
        for i in range(self.size):
            if np.random.rand() < (self.roster[idx].fitnessRank/(self.roster[idx].fitnessRank + 0.5*self.size*killFraction)):
                #print("Rank " + str(self.roster[idx].fitnessRank) + " " + str(self.roster[idx].sex) + " just killed.")
                self.roster[idx].die()
                killed += 1
            else:
                idx += 1
        
        for i in range(self.numChildren):
            self.addAgent(self.childRoster[i])
        
        self.childRoster = []
        self.numChildren = 0
        return killed

    def getDNAAverage(self):
        if len(self.roster) == 0:
            return []
        ret = np.zeros((self.m, self.n))
        for agent in self.roster:
            for i in range(m):
                for j in range(n):
                    ret[i][j] += agent.DNA[i][j]
        return ret/self.size


    def getDNAVariance(self):
        mean = self.getDNAAverage()
        ret = np.zeros((self.m, self.n))
        for agent in self.roster:
            for i in range(self.m):
                for j in range(self.n):
                    ret[i][j] += (agent.DNA[i][j] - mean[i][j])**2
        return ret/self.size

    def getRosterDNA(self):
        ret = []
        for i in range(self.size):
            ret += [self.roster[i].DNA]
        return ret

class Agent:
    def __init__(self, tribe, dna, sex):
        self.tribe = tribe
        self.DNA = dna.astype(int)
        #DNA is an array of integers
        self.m = len(dna) #Rows of DNA in this agent
        self.n = len(dna[0]) #Columns of DNA in this agent
        self.sex = sex # 1 is male, 0 is female
        self.fitness = 0 # Sexual appeal
        self.fitnessRank = 0
        return
    
    #implement communication and vision?

    def mutate(self, dna, weight, lengthWeight):
        #Weight is a constant between 0 and 1, representing fraction of entries mutated
        m = len(dna)
        n = len(dna[0])
        
        ret = dna
        numMutations = int(round(m*n*weight))
        for k in range(numMutations):
            i = np.random.randint(m)
            j = np.random.randint(n)
            r = np.random.rand()
            if j in (0,2):
                ret[i][j] = np.random.choice((0, 0, 0, 1))
            elif j in (1,3):
                ret[i][j] = min(int(math.floor(-math.log(1-r,1.08))), (m*(n-6)-1))
            elif j == 4:
                ret[i][j] = np.random.randint(m)
            else:
                ret[i][j] = int(math.ceil((r-0.5)*100))
                
        nl = min(int(round(lengthWeight)), m - 2)

        if weight > 0:
            dnaChange = np.random.randint(2)
            location = np.random.randint(m-nl)
            
            if dnaChange == 0:
                location = np.random.randint(m-nl)
                newDNA = np.zeros((m-nl,n))
                for i in range(0, location):
                    newDNA[i] = ret[i]
                for i in range(location, m-nl):
                    newDNA[i] = ret[i+nl]
            elif dnaChange == 1:
                location = np.random.randint(m)
                newDNA = np.zeros((m+nl, n))
                # Rows 0 through m:
                for i in range(0, location):
                    newDNA[i] = ret[i]
                # Row m + 1 add random values
                for i in range(location, location + nl):
                    for j in range(n):
                        r = np.random.rand()
                        if j in (0,2):
                            newDNA[i][j] = np.random.choice((0, 0, 0, 1))
                        elif j in (1,3):
                            newDNA[i][j] = min(int(math.floor(-math.log(1-r,1.08))), (m*(n-6)-1))
                        elif j == 4:
                            newDNA[i][j] = np.random.randint(m)
                        else:
                            newDNA[i][j] = int(math.ceil((r-0.5)*100)-0)
                for i in range(location + nl, m + nl):
                    newDNA[i] = ret[i-nl]
            else:
                newDNA = ret
        else:
            newDNA = ret
        
        return newDNA
                
    def reproduce(self, partner):
        choiceLength = np.random.randint(2)
        cutoff = np.random.randint(min(self.m, partner.m))

        if choiceLength == 0:
            childDNA = np.zeros((self.m,self.n))
                        
            if self.m <= partner.m:
                swap = np.random.randint(2)
                if swap == 1:
                    childDNA[0:cutoff] = partner.DNA[0:cutoff]
                    childDNA[cutoff:self.m] = self.DNA[cutoff:self.m]
                else:
                    childDNA[0:cutoff] = self.DNA[0:cutoff]
                    childDNA[cutoff:self.m] = partner.DNA[cutoff:self.m]
            else:
                childDNA[0:cutoff] = partner.DNA[0:cutoff]
                childDNA[cutoff:self.m] = self.DNA[cutoff:self.m]
        else:
            childDNA = np.zeros((partner.m, partner.n))
            
            if partner.m <= self.m:
                swap = np.random.randint(2)
                if swap == 1:
                    childDNA[0:cutoff] = partner.DNA[0:cutoff]
                    childDNA[cutoff:partner.m] = self.DNA[cutoff:partner.m]
                else:
                    childDNA[0:cutoff] = self.DNA[0:cutoff]
                    childDNA[cutoff:partner.m] = partner.DNA[cutoff:partner.m]
            else:
                childDNA[0:cutoff] = self.DNA[0:cutoff]
                childDNA[cutoff:partner.m] = partner.DNA[cutoff:partner.m]
            
        #INCORPORATE MUTATIONS HERE!
        
        childSex = np.random.randint(2)
        amountToMutate = 0
        if childSex == 0:   # If girl, make mom's DNA active
            amountToMutate = -math.log(1-np.random.rand(),2)/5000
            lengthAmountToMutate = -0.5*math.log(1-np.random.rand(), 2)
        else:               # If boy, make dad's DNA active
            amountToMutate = -math.log(1-np.random.rand(),2)/250
            lengthAmountToMutate = -2*math.log(1-np.random.rand(), 2)
        
        childMutatedDNA = self.mutate(childDNA, amountToMutate, lengthAmountToMutate)
        child = Agent(self.tribe, childMutatedDNA, childSex)

            
        #print("Mom dna (m= " + str(self.m) + ")")
        #print(self.DNA)
        #print("dad dna (m= " + str(partner.m) + ")")
        #print(partner.DNA)
        #print("Child DNA, its a " + str(childSex))
        #print(child.DNA)
        
        
        self.tribe.addChild(child)
        

    def die(self):
        t = self.tribe
        pop = t.size
        agentInTribe = False
        for i in range(pop):
            if self is t.roster[i]:
                if i == pop-1:
                    t.roster = t.roster[0:pop-1]
                else:
                    t.roster = t.roster[0:i] + t.roster[i+1:pop]
                agentInTribe = True
                self.tribe.size -= 1
                break
        if agentInTribe == False:
            print("ERROR: KILLING DEAD MAN! This should not happen.")

    def conceptualLogic(self, input):
        #This function essentially implements the SUBLEQ function, through with all agent computations are performed.
        #Input is an array of bits, output is an array of bits.
        '''
            (0,1)   (0-m*(n-6))  (0,1)  (0-m*(n-6))  (0-m)        WORKING MEMORY
            | I/W_1   |  LOC_1  |  O/W_1  |  LOC_2  |   PC    |                       |
            |    0    |         |   0     |         |         |                       |
            |    1    |         |   1     |         |         |                       |
            |    2    |         |   2     |         |         |                       |
            |    0    |         |   0     |         |         |                       |
    
        '''
        output = np.zeros(50)
        workspace = self.DNA.copy()
        loopCnt = 0
        pc = int(0)
        while pc < self.m:
            a = 0
            b = 0
            c = 0
            
            if workspace[pc][0] == 0:                                    #Referencing a memory location in the input array
                a = input[workspace[pc][1]%len(input)]                   #Mem[a]
            elif workspace[pc][0] == 1:                                  #Referencing a memory location in the workspace
                i = (workspace[pc][1]//(self.n-6))%self.m                #compute row and column of workspace memory
                j = workspace[pc][1]%(self.n-6) + 6
                a = workspace[i][j]                                      #Mem[a]
            
            if workspace[pc][2] == 0:                                    #Referencing a memory location in the output array
                b = output[workspace[pc][3]%len(output)] - a             #Mem[b]
                output[workspace[pc][3]%len(output)] = b
            elif workspace[pc][2] == 1:                                  #Referencing a memory location in the workspace
                i = (workspace[pc][3]//(self.n-6))%self.m                #compute row and column of workspace memory
                j = workspace[pc][3]%(self.n-6) + 6
                b = workspace[i][j] - a                                  #Mem[b]
                workspace[i][j] = b
            
            c = int(workspace[pc][4])
            if (b <= 0):                                                 #Branch to c if less than or equal to.
                if c < 0 and -c < self.m:
                    #pc = self.m + c
                    pc = pc
                elif c < self.m:
                    #pc = c
                    pc = pc
                else:
                    return output
            
            pc += 1
            loopCnt += 1
            if loopCnt >= self.m:
                #This agent is infinite looping. STOP
                #self.die()
                return output
        return output
