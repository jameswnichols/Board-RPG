import random
import math

MAP_WIDTH = 200
MAP_HEIGHT = 200

MAP_SAMPLE_SEGMENTS = 100
POINT_SHIFT_SAMPLES = 100
POINT_SHIFT_MAX_DISTANCE = 15

def setupMapDictionary():
    map = {}
    for y in range(MAP_HEIGHT):
        for x in range(MAP_WIDTH):
            map[(x, y)] = "≋"
    return map

def generatePointShiftValue(val):
    return ((random.random()*2)-1) * val

def getLength(pos1, pos2):
    return math.sqrt((pos1[0]-pos2[0])**2+(pos1[1]-pos2[1])**2)

def generatePointsOnLine(pos1, pos2):
    samplePoints = int(getLength(pos1, pos2) * 2)

    points = []

    xPerSample, yPerSample = (pos1[0] - pos2[0]) / samplePoints, (pos1[1] - pos2[1]) / samplePoints

    for i in range(samplePoints):
        points.append((pos1[0] - int(xPerSample * i), pos1[1] - int(yPerSample * i)))

    return points

def getPointsFromThreshold(points, smallestValue, threshold):
    thinPoints = []
    for i, pointValue in enumerate(points):
        pos, value = pointValue["coord"], abs(pointValue["value"])

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

        actualX, actualY = math.floor(circleX + xChangePerSample * sampleNo), math.floor(circleY + yChangePerSample * sampleNo)

        pointValues.append({"coord":(actualX, actualY),"value":sampleNo})
    
    return pointValues, smallestValue

def getPointOnLine(pos1, pos2, len):
    lineLength = getLength(pos1, pos2)
    xChange, yChange = (pos1[0] - pos2[0]) / lineLength, (pos1[1] - pos2[1]) / lineLength
    return (pos1[0] + xChange * len, pos1[1] + yChange * len)

def getAdjecentPoints(pos):
    shifts = [(-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1)]

    return [(pos[0]+s[0], pos[1]+s[1]) for s in shifts]

def generateMap(state):

    map = setupMapDictionary()

    centreX, centreY = MAP_WIDTH // 2, MAP_HEIGHT // 2

    shoreRadius = (MAP_WIDTH - centreX) * 0.8

    beachSize = (MAP_WIDTH - centreX) * 0.15

    grassRadius = (MAP_WIDTH - centreX) * 0.65

    grassSize = (MAP_WIDTH - centreX) * 0.15

    shorePointValues, smallestValue = generatePointsOnCircle((centreX, centreY), shoreRadius, POINT_SHIFT_MAX_DISTANCE)

    points = getPointsFromThreshold(shorePointValues, smallestValue, 0.65)

    for i, point in enumerate(points):

        pos1 = point["coord"]
        if i == len(points) - 1:
            pos2 = points[0]["coord"]
        else:
            pos2 = points[i + 1]["coord"]

        linePoints = generatePointsOnLine(pos1, pos2)

        for lp in linePoints:

            beachPoint = getPointOnLine(lp,(centreX,centreY),beachSize)

            beachLinePoints = generatePointsOnLine(lp, beachPoint)

            for blp in beachLinePoints:
                
                for adjP in getAdjecentPoints(blp):

                    map[adjP] = "∴"

    state["mapData"] = map

def renderMap(state):
    mapData = state["mapData"]

    mapLines = []

    for y in range(MAP_HEIGHT):
        mapLine = []
        for x in range(MAP_WIDTH):
            mapLine.append(mapData[(x, y)])
        
        mapLines.append(" ".join(mapLine)+"\n")
    
    with open("test.txt","w") as f:
        f.writelines(mapLines)


def generateState():
    state = {"playerInfo":{"position":{"x":0,"y":0}},"mapData":{}, "objectData":{}}

    generateMap(state)

    renderMap(state)

    return state

if __name__ == "__main__":
    generateState()