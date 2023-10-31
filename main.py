import random
import math

MAP_WIDTH = 200
MAP_HEIGHT = 200

MAP_SAMPLE_SEGMENTS = 100
POINT_SHIFT_SAMPLES = 100
POINT_SHIFT_MAX_DISTANCE = 10

def setupMapDictionary():
    map = {}
    for y in range(MAP_HEIGHT):
        for x in range(MAP_WIDTH):
            map[(x, y)] = " "
    return map

def generatePointShiftValue(val):
    return ((random.random()*2)-1) * val

def generateMap(state):

    map = setupMapDictionary()

    sampleStep = (2 * math.pi) / MAP_SAMPLE_SEGMENTS

    centreX, centreY = MAP_WIDTH // 2, MAP_HEIGHT // 2

    radius = (MAP_WIDTH - centreX) * 0.8

    lastPointShiftValue = generatePointShiftValue(POINT_SHIFT_MAX_DISTANCE)

    for i in range(MAP_SAMPLE_SEGMENTS):

        #Get point on circle at i
        
        steppedRadians = sampleStep * i

        circleX = radius * (math.cos(steppedRadians)) + centreX

        circleY = radius * (math.sin(steppedRadians)) + centreY

        #Offset each point a bit

        #Last value * 0.5

        xChangePerSample, yChangePerSample = (circleX - centreX) / POINT_SHIFT_SAMPLES, (circleY - centreY) / POINT_SHIFT_SAMPLES

        lastValueMin = lastPointShiftValue - lastPointShiftValue * 0.5

        sampleNo = lastValueMin + generatePointShiftValue(lastPointShiftValue)

        actualX, actualY = math.floor(circleX + xChangePerSample * sampleNo), math.floor(circleY + yChangePerSample * sampleNo)

        map[(actualX, actualY)] = "X"

        lastPointShiftValue = sampleNo

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