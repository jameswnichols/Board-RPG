import random
import math

MAP_WIDTH = 50
MAP_HEIGHT = 50

MAP_SAMPLE_SEGMENTS = 360
POINT_SHIFT_SAMPLES = 100
POINT_SHIFT_MAX_DISTANCE = 10

def setupMapDictionary():

    map = {}

    for y in range(MAP_HEIGHT):
        for x in range(MAP_WIDTH):
            map[(x, y)] = " "
    
    return map

def generateMap(state):

    map = setupMapDictionary()

    sampleStep = (2 * math.pi) / MAP_SAMPLE_SEGMENTS

    centreX, centreY = MAP_WIDTH // 2, MAP_HEIGHT // 2

    radius = (MAP_WIDTH - centreX) * 0.8

    for i in range(MAP_SAMPLE_SEGMENTS):

        #Get point on circle at i
        
        steppedRadians = sampleStep * i

        circleX = radius * (math.cos(steppedRadians)) + centreX

        circleY = radius * (math.sin(steppedRadians)) + centreY

        #Offset each point a bit

        xChangePerSample, yChangePerSample = (circleX - centreX) / POINT_SHIFT_SAMPLES, (circleY - centreY) / POINT_SHIFT_SAMPLES

        pointShiftAmount = (random.random()*2)-1

        sampleNo = pointShiftAmount * POINT_SHIFT_MAX_DISTANCE

        actualX, actualY = math.floor(circleX + xChangePerSample * sampleNo), math.floor(circleY + yChangePerSample * sampleNo)

        map[(actualX, actualY)] = "X"

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