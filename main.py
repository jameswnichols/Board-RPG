import random
import math

MAP_WIDTH = 200
MAP_HEIGHT = 200

MAP_SAMPLE_SEGMENTS = 100
POINT_SHIFT_SAMPLES = 100
POINT_SHIFT_MAX_DISTANCE = 15

VILLAGE_RADIUS = 5
VILLAGE_EXCLUSION_RADIUS = 15
#LEFT UP RIGHT DOWN
POSSIBLE_COMBOS = {(0, 0, 0, 0):" ",
                   (0, 0, 0, 1):"║",
                   (0, 0, 1, 0):"═",
                   (0, 0, 1, 1):"╔",
                   (0, 1, 0, 0):"║",
                   (0, 1, 0, 1):"║",
                   (0, 1, 1, 0):"╚",
                   (0, 1, 1, 1):"╠",
                   (1, 0, 0, 0):"═",
                   (1, 0, 0, 1):"╗",
                   (1, 0, 1, 0):"═",
                   (1, 0, 1, 1):"╩",
                   (1, 1, 0, 0):"╝",
                   (1, 1, 0, 1):"╣",
                   (1, 1, 1, 0):"╩",
                   (1, 1, 1, 1):"╬"}


def checkIfCirclesOverlap(centre1, radius1, centre2, radius2):
    distance = getLength(centre1, centre2)
    if distance <= radius1 - radius2 or distance <= radius2 - radius1:
        return True
    if distance < radius1 + radius2 or distance == radius1 + radius2:
        return True

    return False

def pickVillagePoints(pointList : list, amount : int):
    pointListReduced = pointList
    points = []
    pickedSoFar = 0
    while pickedSoFar != amount:
        randomIndex = random.randint(0, len(pointListReduced)-1)
        randomPoint = pointListReduced[randomIndex]
        
        hasOverlapped = False
        for point in points:
            if checkIfCirclesOverlap(point, VILLAGE_EXCLUSION_RADIUS, randomPoint, VILLAGE_EXCLUSION_RADIUS):
                hasOverlapped = True
                break

        if not hasOverlapped:
            points.append(randomPoint)
            del pointListReduced[randomIndex]
            pickedSoFar += 1
    
    return points


def setupMapDictionary():
    map = {}
    for y in range(MAP_HEIGHT):
        for x in range(MAP_WIDTH):
            map[(x, y)] = " "

    return map

def generatePointShiftValue(val):
    return ((random.random()*2)-1) * val

def getLength(pos1, pos2):
    return math.sqrt((pos1[0]-pos2[0])**2+(pos1[1]-pos2[1])**2)

def removeDuplicates(l : list):
    return list({x : 0 for x in l}.keys())

def generatePointsOnLine(pos1, pos2):
    if pos1 == pos2:
        return []
    samplePoints = int(getLength(pos1, pos2) * 2)
    points = []
    xPerSample, yPerSample = (pos1[0] - pos2[0]) / samplePoints, (pos1[1] - pos2[1]) / samplePoints
    for i in range(samplePoints):
        points.append((pos1[0] - int(xPerSample * i), pos1[1] - int(yPerSample * i)))

    return removeDuplicates(points)

def getPointsFromThreshold(points, smallestValue, threshold):
    if threshold == 0:
        return points
    
    thinPoints = []
    for i, pointValue in enumerate(points):
        _, value = pointValue["coord"], abs(pointValue["value"])
        if abs(value - abs(smallestValue)) > abs(smallestValue) * threshold: #0.65
            thinPoints.append(pointValue)
    
    return thinPoints

def generatePointsOnCircle(centre, radius, shiftMax):
    sampleStep = (2 * math.pi) / MAP_SAMPLE_SEGMENTS
    centreX, centreY = centre
    radius = radius
    smallestValue = 0
    pointValues = []

    for i in range(MAP_SAMPLE_SEGMENTS):

        #Get point on circle at i
        steppedRadians = sampleStep * i
        circleX = radius * (math.cos(steppedRadians)) + centreX
        circleY = radius * (math.sin(steppedRadians)) + centreY

        #Offset each point a bit
        xChangePerSample, yChangePerSample = (circleX - centreX) / POINT_SHIFT_SAMPLES, (circleY - centreY) / POINT_SHIFT_SAMPLES
        sampleNo = generatePointShiftValue(shiftMax)
        if sampleNo < smallestValue:
            smallestValue = sampleNo

        #Calculate shifted position and add to dict.
        actualX, actualY = math.floor(circleX + xChangePerSample * sampleNo), math.floor(circleY + yChangePerSample * sampleNo)
        pointValues.append({"coord":(actualX, actualY),"value":sampleNo})
    
    return pointValues, smallestValue

def getPointOnLine(pos1, pos2, len):
    lineLength = getLength(pos1, pos2)
    xChange, yChange = (pos1[0] - pos2[0]) / lineLength, (pos1[1] - pos2[1]) / lineLength

    return (pos1[0] - xChange * len, pos1[1] - yChange * len)

def getAdjecentPoints(pos):
    shifts = [(-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1)]

    return [(pos[0]+s[0], pos[1]+s[1]) for s in shifts]

def getRandomPointsInCircle(centre, radius, amount):
    points = []
    while amount != len(points):
        centreX, centreY = centre
        rValue = radius * math.sqrt(random.random())
        angle = random.random() * 2 * math.pi
        randomX = centreX + rValue * math.cos(angle)
        randomY = centreY + rValue * math.sin(angle)
        pos = (int(randomX), int(randomY))
        if pos not in points:
            points.append(pos)
    
    return points

def quadraticFormula(a, b, c):
    outputs = []
    rightHalf = math.sqrt(b**2 - (4 * a * c))
    options = [rightHalf, -rightHalf]

    for option in options:
        topHalf = -b + option
        solution = topHalf / (2 * a)
        outputs.append(solution)
    
    return outputs

def getBoundsOfCirclePoint(centre, radius, point):
    #Find y values first
    centreX, centreY = centre
    pointX, pointY = point
    a = 1
    b = -2 * centreY
    c = ((pointX - centreX)**2) + (centreY**2) - (radius**2)
    yValues = quadraticFormula(a, b, c)

    #Find x values next
    a = 1
    b = -2 * centreX
    c = ((pointY - centreY)**2) + (centreX)**2 - (radius**2)
    xValues = quadraticFormula(a, b, c)

    return ([int(x) for x in xValues], [int(y) for y in yValues])

def getRoadAdjecent(map, pos):
    posX, posY = pos
    checks = [(posX - 1, posY), (posX, posY - 1), (posX + 1, posY), (posX, posY + 1)]

    adj = []

    for check in checks:
        
        if map[check] == "." or map[check] in POSSIBLE_COMBOS.values():
            adj.append(1)
        else:
            adj.append(0)

    return tuple(adj)


def islandRing(map, centre, radius, shiftMaxDistance, ringSize, threshold, tile, getValidPoints = False, validDistance = 0, validRadius = 0):
    circlePoints, smallestValue = generatePointsOnCircle(centre, radius, shiftMaxDistance)
    points = getPointsFromThreshold(circlePoints, smallestValue, threshold)

    validPoints = []

    for i, point in enumerate(points):
        pos1 = point["coord"]
        if i == len(points) - 1:
            pos2 = points[0]["coord"]
        else:
            pos2 = points[i + 1]["coord"]
        linePoints = generatePointsOnLine(pos1, pos2)
        for lp in linePoints:
            innerRingPoint = getPointOnLine(lp,centre,ringSize)
            ringWidthPoints = generatePointsOnLine(lp, innerRingPoint)
            for i, rwp in enumerate(ringWidthPoints):
                if getLength(lp, rwp) <= validDistance-validRadius and getLength(lp, rwp) > validRadius:
                    validPoints.append(rwp)
                for adjP in getAdjecentPoints(rwp):
                    map[adjP] = tile

    return validPoints

def generateMap(state):
    map = setupMapDictionary()
    centreX, centreY = MAP_WIDTH // 2, MAP_HEIGHT // 2

    #Beach
    shoreRadius = (MAP_WIDTH - centreX) * 0.8
    shoreSize = (MAP_WIDTH - centreX) * 0.5

    #Grass
    grassRadius = (MAP_WIDTH - centreX) * 0.69
    grassSize = (MAP_WIDTH - centreX) * 0.5

    #Small Mountaims
    mountainRadius = (MAP_WIDTH - centreX) * 0.35
    mountainSize = (MAP_WIDTH - centreX) * 0.35

    #Tall Mountains
    superMountainRadius = (MAP_WIDTH - centreX) * 0.15
    superMountainSize = (MAP_WIDTH - centreX) * 0.15

    islandRing(map, (centreX, centreY), shoreRadius, POINT_SHIFT_MAX_DISTANCE, shoreSize, 0.65, "…")
    villagePositions = islandRing(map, (centreX, centreY), grassRadius, POINT_SHIFT_MAX_DISTANCE, grassSize, 0.65, "≡", True,grassSize/3,VILLAGE_RADIUS)
    islandRing(map, (centreX, centreY), mountainRadius, POINT_SHIFT_MAX_DISTANCE+10, mountainSize, 0.35, "^") #≙
    islandRing(map, (centreX, centreY), superMountainRadius, POINT_SHIFT_MAX_DISTANCE+50, superMountainSize, 0.35, "Ʌ")

    villagePositions = pickVillagePoints(villagePositions, 5)

    for pos in villagePositions:

        villageCrossroads = getRandomPointsInCircle(pos, VILLAGE_RADIUS, 1)

        islandRing(map, pos, VILLAGE_RADIUS, 0, 1, 0, "!")

        roadPositions = []
        
        for cr in villageCrossroads:
            crXEdges, crYEdges  = getBoundsOfCirclePoint(pos, VILLAGE_RADIUS, cr)
            smallX, largeX = min(crXEdges), max(crXEdges)
            smallY, largeY = min(crYEdges), max(crYEdges)
            for x in range(smallX, largeX+1):
                map[(x, cr[1])] = "."
                roadPositions.append((x, cr[1]))
            for y in range(smallY, largeY):
                map[(cr[0], y)] = "."
                roadPositions.append((cr[0], y))
                
        for rp in roadPositions:
            map[rp] = POSSIBLE_COMBOS[getRoadAdjecent(map, rp)]

    state["mapData"] = map

def renderMap(state):
    mapData = state["mapData"]
    mapLines = []
    for y in range(MAP_HEIGHT):
        mapLine = []
        for x in range(MAP_WIDTH):
            mapLine.append(mapData[(x, y)])
        mapLines.append(" ".join(mapLine)+"\n")
    with open("map.txt","w") as f:
        f.writelines(mapLines)

def testMap(state, times):
    fails = 0
    for i in range(0, times):
        print(f"Try: {i+1}")
        try:
            generateMap(state)
        except:
            fails += 1
    print(f"Test failed {fails} times.")


def generateState():
    state = {"playerInfo":{"position":{"x":0,"y":0}},"mapData":{}, "objectData":{}}

    generateMap(state)

    renderMap(state)

    return state

if __name__ == "__main__":
    generateState()