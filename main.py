import random
import math

MAP_WIDTH = 200
MAP_HEIGHT = 200

MAP_SAMPLE_SEGMENTS = 100
POINT_SHIFT_SAMPLES = 100

def generateMap(state):
    sampleStep = (2 * math.pi) / MAP_SAMPLE_SEGMENTS

    centreX, centreY = MAP_WIDTH // 2, MAP_HEIGHT // 2

    radius = (MAP_WIDTH - centreX) * 0.8

    for i in range(0, MAP_SAMPLE_SEGMENTS):

        #Get point on circle at i
        
        steppedRadians = sampleStep * i

        circleX = radius * (math.cos(steppedRadians)) + centreX

        circleY = radius * (math.sin(steppedRadians)) + centreY

        #Offset each point a bit

        xChangePerSample, yChangePerSample = (circleX - centreX), (circleY - centreY)

        pointShiftAmount = (random.random()*2)-1

        sampleNo = pointShiftAmount * POINT_SHIFT_SAMPLES

        actualX, actualY = math.floor(xChangePerSample * sampleNo), math.floor(yChangePerSample * sampleNo)



        



def generateState():
    state = {"playerInfo":{"Position":{"x":0,"y":0}},"MapData":[]}

    return state

if __name__ == "__main__":
    pass