#Team Members:
# Dhruv Bajpai - dbajpai - 6258833142
# Anupam Mishra - anupammi - 2053229568
import numpy as np

dataFileName = "hmm-data.txt"
boardXLimit = 10
boardYLimit = 10

def findCellLocations(file, wordLine, width):
    count=0
    free_cell=[]
    with open(file) as f:
        for line in f:
            line=line.strip()
            line=line.split()
            if (any(check in line for check in wordLine)):
                continue
            if(line== []):
                continue
            for index,l in enumerate(line):
                if l=='1':
                    free_cell.append([int(count),int(index)])
            if len(line) > 0:
                count += 1
            if count == width:
                break
    return free_cell



wordLine=['Grid-World:', 'Locations:', 'Noisy']
free_cell = findCellLocations(dataFileName, wordLine, 10)

def isWithinBoard(newPoint):
    x = newPoint[0]
    y = newPoint[1]
    if (x>=0 and x<boardXLimit and y>=0 and y<boardYLimit):
        return True
    return False
    
def getNeighbourList(point,free_cell):
    x = point[0]
    y = point[1]
    neighbourList = []
#     going down
    newPoint = [x+1,y]
    if(isWithinBoard(newPoint) and newPoint in free_cell):
        neighbourList.append(newPoint)
    
    #     going up
    newPoint = [x-1,y]
    if(isWithinBoard(newPoint) and newPoint in free_cell):
        neighbourList.append(newPoint)

    #     going right
    newPoint = [x,y+1]
    if(isWithinBoard(newPoint) and newPoint in free_cell):
        neighbourList.append(newPoint)

    #     going left
    newPoint = [x,y-1]
    if(isWithinBoard(newPoint) and newPoint in free_cell):
        neighbourList.append(newPoint)
    return neighbourList

def getTransitionDictionary(free_cell):
    tranDict = {}
    for point in free_cell:
        neighbourList = getNeighbourList(point,free_cell)
        totalNeighbours = len(neighbourList)
        neighbourProbDict = {}
        for neighbour in neighbourList:
            neighbourProbDict[tuple(neighbour)] = 1/totalNeighbours
        tranDict[tuple(point)] = neighbourProbDict
    return tranDict


def getTowerLocations(file, checks):
    tower_loc=[]
    with open(file) as f:
        for line in f:
            line=line.strip()
            line=line.split()
            if (any(check in line for check in checks)):
                continue
            if(line==[]):
                continue
            if(line[0]=='Tower'):
                tower_loc.append([int(line[2]),int(line[3])])
    return tower_loc


def robot_tower_dist(file,checks,li):
    noisy_dist=[]
    with open(file) as f:
        for line in f:
            if(li>0):
                li=li-1	
                continue
            elif(li==0):
                line=line.strip()
                line=line.split()
                if (any(check in line for check in checks)):
                    continue
                if(line==[]):
                    continue
                noisy_dist.append(line)
    for i in range(0,len(noisy_dist)):
        print (noisy_dist[i])
    return noisy_dist


towerLocations = getTowerLocations(dataFileName, wordLine)

noisyDist = [['6.3', '5.9', '5.5', '6.7'],
['5.6', '7.2', '4.4', '6.8'],
['7.6', '9.4', '4.3', '5.4'],
['9.5', '10.0', '3.7', '6.6'],
['6.0', '10.7', '2.8', '5.8'],
['9.3', '10.2', '2.6', '5.4'],
['8.0', '13.1', '1.9', '9.4'],
['6.4', '8.2', '3.9', '8.8'],
['5.0', '10.3', '3.6', '7.2'],
['3.8', '9.8', '4.4', '8.8'],
['3.3', '7.6', '4.3', '8.5']]


noisyDist = [[float(x) for x in line] for line in noisyDist]

transitionDictionary = getTransitionDictionary(free_cell)
solArray = np.zeros((len(free_cell),11))
emissionMatrix = np.zeros((len(free_cell),11))

def getEmission(noisyDist,point):
    t = [[0,0],[0,9],[9,0],[9,9]]
    probs = [] #Four emission probabilities from 4 towers to multiply
    for i in range(0,4):
        curTower = t[i]
        distance = np.sqrt(np.square(point[0]-curTower[0]) + np.square(point[1]-curTower[1]))
        curNoisyDist = noisyDist[i]
        if (curNoisyDist <= round((1.3*distance),1) and curNoisyDist >= round((0.7 * distance),1)):
            prob = 1 / (round((0.6 * distance),1)*10 + 1)
            probs.append(prob)
        else:
            probs.append(0)
    return np.prod(np.array(probs))
        

def fillEmissionMatrix(emissionMatrix):
    for timeStep in range(0,11):
        curNoisyDist = noisyDist[timeStep]
        for i in range(0,len(free_cell)):#Iterating over all states in all timesteps
            emissionMatrix[i][timeStep] = getEmission(curNoisyDist,free_cell[i])
    return emissionMatrix

emissionMatrix = fillEmissionMatrix(emissionMatrix)
solArray[:,0] = 1/len(free_cell) * emissionMatrix[:,0]
backtrackingMat = np.ones((len(free_cell),11))


solutionStateIndexes = []
for timestep in range(1,11):
    for state in range(0,len(free_cell)):
        lastBestState = -1
        lastBestProb = -1
        curState = state
        for prevStateIndex in range(0,len(free_cell)):
            prevStateProb = solArray[prevStateIndex][timestep-1]
            transElement1 = transitionDictionary[tuple(free_cell[prevStateIndex])]
            multiplier = 0.0 # for when there isnt a map from one of 87 prev
            if tuple(free_cell[curState]) in transElement1: # If curstate present in transitionList
                multiplier = transElement1[tuple(free_cell[curState])]
            probToCurState = prevStateProb * multiplier * float(emissionMatrix[curState][timestep])
            if (probToCurState>lastBestProb):
                lastBestProb = probToCurState
                lastBestState = prevStateIndex
        solArray[curState][timestep] = lastBestProb
        backtrackingMat[curState][timestep] = lastBestState

#         find max of timestep-1 all states to timestep values current state
        
bestSequence = []
prevStateIndex = np.argmax(solArray[:,10])
colMax = prevStateIndex
for j in range(10,-1,-1):
    prevStateIndex = int(backtrackingMat[colMax][j])
    bestSequence.append(free_cell[colMax])
    colMax = prevStateIndex

sequence = []
for i in reversed(bestSequence):
    sequence.append(i)
print("MOST LIKELY TRAJECTORY")
for i in range(0,len(sequence)):
    print ("Cell {} at TimeStep: {}".format(sequence[i],i+1))
