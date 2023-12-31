#https://github.com/jameswnichols/Board-RPG
#19293404programmingCoursework4004
#When run on repl.it, must be started twice to stop a visual glitch.

import random
import math
import os
import inspect
import ast
import time
import pickle
import copy
import traceback

MAP_WIDTH = 200
MAP_HEIGHT = 200

SCREEN_WIDTH, SCREEN_HEIGHT = os.get_terminal_size()

SCREEN_HEIGHT -= 1

MAP_SAMPLE_SEGMENTS = 100
POINT_SHIFT_SAMPLES = 100
POINT_SHIFT_MAX_DISTANCE = 15

VILLAGE_RADIUS = 5
VILLAGE_EXCLUSION_RADIUS = 15
MIN_HOUSES = 5
MAX_HOUSES_PERCENTAGE = 0.5
VILLAGER_AMOUNT = 75
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
                   (1, 0, 1, 1):"╦",
                   (1, 1, 0, 0):"╝",
                   (1, 1, 0, 1):"╣",
                   (1, 1, 1, 0):"╩",
                   (1, 1, 1, 1):"╬"}

PLAYER_DIRECTIONS = {(0, -1):"↑",
                     (1, -1):"↗",
                     (1, 0):"→",
                     (1, 1):"↘",
                     (0, 1):"↓",
                     (-1, 1):"↙",
                     (-1, 0):"←",
                     (-1, -1):"↖",}

VALID_DIRECTIONS = {"n":(0, -1),
                    "ne":(1, -1),
                    "e":(1, 0),
                    "se":(1, 1),
                    "s":(0, 1),
                    "sw":(-1, 1),
                    "w":(-1, 0),
                    "nw":(-1, -1)}

VALID_DIRECTIONS_LOOKUP = {y : x for x, y in VALID_DIRECTIONS.items()}

TERRAIN_REQUIRED_ITEM = {
    "ocean":"UNOBTAINABLE",
    "hills":"Snow Boots",
    "innerHills":"Snow Boots",
    "mountains":"Ice Picks"
}

TREE_AMOUNT = 1500

HILL_TREE_AMOUNT = 500

HILL_ROCK_AMOUNT = 20

MOUNTAIN_ROCK_AMOUNT = 100

GOBLIN_AMOUNT = 500

KNIGHT_AMOUNT = 100

OGRE_AMOUNT = 50

MAX_HEALTH_RENDER = 800

AUTOSAVE_SECONDS = 300

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

        if not hasOverlapped:
            points.append(randomPoint)
            del pointListReduced[randomIndex]
            pickedSoFar += 1
    
    return points


def setupMapDictionary(char : str):
    map = {}
    for y in range(MAP_HEIGHT):
        for x in range(MAP_WIDTH):
            map[(x, y)] = char

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
    shifts = [(-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1)]

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

        notNearby = True
        for point in points:
            if abs(point[0] - pos[0]) == 1 or abs(point[1] - pos[1]) == 1:
                notNearby = False

        if pos not in points and notNearby:
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
    emptyPositions = []
    checks = [(posX - 1, posY), (posX, posY - 1), (posX + 1, posY), (posX, posY + 1)]

    adj = []

    for check in checks:
        
        if map[check] == "." or map[check] in POSSIBLE_COMBOS.values():
            adj.append(1)
        else:
            if check not in emptyPositions:
                emptyPositions.append(check)
            adj.append(0)

    return emptyPositions, tuple(adj)

def islandRing(map, centre, radius, shiftMaxDistance, ringSize, threshold, tile, getValidPoints = False, validDistance = 0, validRadius = 0, pointDict = None, ringName = ""):
    circlePoints, smallestValue = generatePointsOnCircle(centre, radius, shiftMaxDistance)
    points = getPointsFromThreshold(circlePoints, smallestValue, threshold)

    validPoints = []
    
    getAllPoints = isinstance(pointDict, dict)

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
                    
                    if getAllPoints:
                        pointDict[adjP] = ringName
                        pointDict["baseTiles"].add(tile)

    return validPoints

def generateVillages(map, objectData, possiblePositions : list):
    villagePositions = pickVillagePoints(possiblePositions, 3)

    villagerPositions = []

    for pos in villagePositions:

        villageCrossroads = getRandomPointsInCircle(pos, VILLAGE_RADIUS, 4)

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

        houseLocations = []

        for rp in roadPositions:
            empty, adj = getRoadAdjecent(map, rp)
            map[rp] = POSSIBLE_COMBOS[adj]
            houseLocations.extend(empty)
        
        houseSamples = random.randint(MIN_HOUSES, int(len(houseLocations) * MAX_HOUSES_PERCENTAGE))

        for houseLoc in random.sample(houseLocations, houseSamples):
            objectData[houseLoc] = {"objectType":"blocking","display":"⌂"}
            villagerPositions.extend(getAdjecentPoints(houseLoc))
    
    return villagerPositions


def getSpawnLocations(map, objectData, pointDict : dict):

    spawnLists = {}

    baseTiles = pointDict["baseTiles"]

    for val in list(pointDict.values()):
        if (not isinstance(val, set)) and val not in spawnLists:
            spawnLists[val] = []

    for pos, spawn in pointDict.items():
        if (not isinstance(spawn, set)) and map[pos] in baseTiles and pos not in objectData:
            spawnLists[spawn].append(pos)
    
    return spawnLists

def sampleWithRemove(possibleItems, amount):
    chosen = []
    for i in range(0, amount):
        try:
            randomIndex = random.randint(0, len(possibleItems)-1)
            chosen.append(possibleItems[randomIndex])
            del possibleItems[randomIndex]
        except:
            return chosen

    return chosen

def randomChance(chance, rolls):
    chanceLanded = False
    for r in range(rolls):
        if random.random() <= chance and chance != 0:
            chanceLanded = True
    return chanceLanded

def getDroppedItems(dropTable, rolls):
    rollCount, chanceData = rolls, dropTable["chanceData"]
    itemsDropped = {}
    for roll in range(rolls):
        for i, itemDrop in enumerate(chanceData):
            (item, count), chance = itemDrop
            if randomChance(chance, 1):
                if item in itemsDropped:
                    itemsDropped[item] += count
                else:
                    itemsDropped[item] = count
    
    return itemsDropped
    #Formatted as {chanceData: [[(ITEM, COUNT), CHANCE]]}

def generateDropTable(*itemDrops : list):
    dropDict = {"chanceData":[]}
    for drop in itemDrops:
        dropDict["chanceData"].append(drop)
    return dropDict

def generateTradeTable(*trades : list):
    table = []
    for trade in trades:
        table.append({"input":trade[0],"output":trade[1],"uses":trade[2]})
    return table

def pickTrade(tradeTable : list):
    hasChosenTrade = False
    while not hasChosenTrade:
        randomIndex = random.randint(0, len(tradeTable)-1)
        trade = tradeTable[randomIndex]
        tradeUses = trade["uses"]
        if not tradeUses:
            return {"input":trade["input"],"output":trade["output"]}
        elif tradeUses > 0:
            tradeTable[randomIndex]["uses"] -= 1
            return {"input":trade["input"],"output":trade["output"]}
            
def generateObjects(objectData, possibleSpawns, spawnAmount, symbol, dropTable, harvestRequires : list = []):
    chosenSpawns = sampleWithRemove(possibleSpawns,spawnAmount)
    for spawn in chosenSpawns:
        #itemsChosen = getDroppedItems(dropTable)
        #print(f"Object : {symbol} Drops : {itemsChosen}")
        objectData[spawn] = {"objectType":"intTile","display":symbol,"drops":dropTable,"harvestRequires":harvestRequires}

def generateEnemies(objectData, possibleSpawns, spawnAmount, symbol, dropTable, health, damage, name):
    chosenSpawns = sampleWithRemove(possibleSpawns, spawnAmount)
    for spawn in chosenSpawns:
        objectData[spawn] = {"objectType":"enemy","display":symbol,"drops":dropTable,"health":health,"maximumHealth":health,"damage":damage,"name":name}

def generateVillagers(map, objectData, positions, amount, tradeTable):
    chosen = 0
    while chosen < amount:
        chosenPosition = sampleWithRemove(positions, 1)
        if not chosenPosition:
            return
        chosenPosition = chosenPosition[0]
        #If space isnt occupied and space isnt a road
        if chosenPosition not in objectData and map[chosenPosition] not in list(POSSIBLE_COMBOS.values()):
            chosenTrade = pickTrade(tradeTable)
            objectData[chosenPosition] = {"objectType":"villager","display":"♙","trade":chosenTrade}
            chosen += 1

def generateMap(state):
    map = setupMapDictionary(" ")

    objectData = {}

    spawningPoints = setupMapDictionary("ocean")
    
    spawningPoints["baseTiles"] = {"ocean",}

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

    #Inner Hills
    innerHillRadius = (MAP_WIDTH - centreX) * 0.21
    innerHillSize = (MAP_WIDTH - centreX) * 0.21

    #Tall Mountains
    superMountainRadius = (MAP_WIDTH - centreX) * 0.15
    superMountainSize = (MAP_WIDTH - centreX) * 0.15

    islandRing(map, (centreX, centreY), shoreRadius, POINT_SHIFT_MAX_DISTANCE, shoreSize, 0.55, "…", False, 0, 0, spawningPoints, "beach")
    villagePositions = islandRing(map, (centreX, centreY), grassRadius, POINT_SHIFT_MAX_DISTANCE, grassSize, 0.65, "≡", True,grassSize/2.5,VILLAGE_RADIUS, spawningPoints, "grass")
    islandRing(map, (centreX, centreY), mountainRadius, POINT_SHIFT_MAX_DISTANCE+10, mountainSize, 0.35, "^", False, 0, 0, spawningPoints, "hills") #≙
    islandRing(map, (centreX, centreY), innerHillRadius, 1, innerHillSize, 0.35, "^", False, 0, 0, spawningPoints, "innerHills")
    islandRing(map, (centreX, centreY), superMountainRadius, POINT_SHIFT_MAX_DISTANCE+50, superMountainSize, 0.35, "Ʌ", False, 0, 0, spawningPoints, "mountains")

    state["islandMaskData"] = spawningPoints

    villagerPositions = generateVillages(map, objectData, villagePositions)

    spawnLists = getSpawnLocations(map, objectData, spawningPoints)

    #Generate Interactable Tiles
    woodDropTable = generateDropTable([("Wood", 1), 1], [("Wood", 1), 0.5], [("Wood", 1), 0.5])
    rockDropTable = generateDropTable([("Stone", 1), 1], [("Stone", 1), 0.5], [("Stone", 1), 0.5], [("Gem", 1), 0.1], [("Gem", 1), 0.05])
    moutainRockDropTable = generateDropTable([("Stone", 1), 1], [("Stone", 1), 0.5], [("Stone", 1), 0.5], [("Gem", 1), 0.5], [("Gem", 1), 0.25], [("Gem", 1), 0.125])

    goblinDropTable = generateDropTable([("Wood", 1), 1], [("Wood", 1), 0.5], [("Skill Fragment", 2), 1], [("Skill Fragment", 1), 0.5], [("Skill Fragment", 1), 0.5], [("Goblin Club", 1), 0.1], [("Goblin Shield", 1), 0.05], [("Snow Boots", 1), 0.01])
    knightDropTable = generateDropTable([("Stone", 1), 1], [("Stone", 1), 0.5], [("Skill Fragment", 4), 1], [("Skill Fragment", 2), 0.5], [("Skill Fragment", 2), 0.5], [("Knight's Sword", 1), 0.1], [("Knight's Shield", 1), 0.05], [("Ice Picks", 1), 0.01])
    ogreDropTable = generateDropTable([("Skill Fragment", 5), 1], [("Skill Fragment", 3), 0.5], [("Skill Fragment", 2), 0.5],[("Gem", 2), 1], [("Gem", 1), 0.5], [("Gem", 1), 0.5], [("Ogre Club", 1), 1])
    kingDropTable = generateDropTable([("Health Up Orb", 1), 1], [("Health Up Orb", 1), 0.5], [("Health Up Orb", 1), 0.5], [("Attack Up Orb", 1), 1], [("Attack Up Orb", 1), 0.5], [("Attack Up Orb", 1), 0.5], [("King's Sword", 1), 1], [("King's Shield", 1), 1])

    villagerTradeTable = generateTradeTable([("Wood", 10), ("Gem", 1), None],
                                            [("Stone", 10), ("Gem", 1), None],
                                            [("Wood", 15), ("Gem", 1), None],
                                            [("Stone", 15), ("Gem", 1), None],
                                            [("Gem", 2), ("Skill Fragment", 1), 50],
                                            [("Gem", 15), ("Snow Boots", 1), 50],
                                            [("Gem", 30), ("Ice Picks", 1), 30],
                                            [("Gem", 1), ("Med Kit", 1), 50],
                                            [("Skill Fragment", 10), ("Health Up Orb",1),30],
                                            [("Skill Fragment", 10), ("Attack Up Orb",1),30],
                                            [("Gem", 10), ("Soldier's Sword", 1), 30],
                                            [("Gem", 10), ("Miner's Pickaxe", 1), 30],
                                            [("Gem", 10), ("Lumber Axe", 1), 30]
                                            )

    generateObjects(objectData, spawnLists["grass"],TREE_AMOUNT, "♣", woodDropTable,["Axe","Lumber Axe"])

    generateObjects(objectData, spawnLists["hills"],HILL_TREE_AMOUNT,"↟", woodDropTable,["Axe","Lumber Axe"])

    generateObjects(objectData, spawnLists["innerHills"], HILL_ROCK_AMOUNT, "☁", rockDropTable,["Pickaxe","Miner's Pickaxe"])

    generateObjects(objectData, spawnLists["mountains"], MOUNTAIN_ROCK_AMOUNT, "☁", moutainRockDropTable,["Pickaxe","Miner's Pickaxe"])

    generateEnemies(objectData, spawnLists["grass"], GOBLIN_AMOUNT, "♀", goblinDropTable, 30, 10,"Goblin")

    generateEnemies(objectData, spawnLists["hills"], KNIGHT_AMOUNT, "♘", knightDropTable, 100, 20,"Knight")

    generateEnemies(objectData, spawnLists["hills"], OGRE_AMOUNT//2, "♗", ogreDropTable, 150, 20,"Ogre")

    generateEnemies(objectData, spawnLists["mountains"], OGRE_AMOUNT//2, "♗", ogreDropTable, 150, 20,"Ogre")

    generateEnemies(objectData, [(MAP_WIDTH//2,MAP_HEIGHT//2)], 1, "♔", kingDropTable, 200, 50,"The King")

    generateVillagers(map, objectData, villagerPositions, VILLAGER_AMOUNT, villagerTradeTable)

    playerSpawn = sampleWithRemove(spawnLists["beach"], 1)[0]

    state["playerData"]["position"] = playerSpawn

    state["mapData"] = map

    state["objectData"] = objectData

def generateScreen(size : tuple[int, int], char : str = " "):
    width, height = size
    screen = {"width":width, "height":height, "data":{}}
    for y in range(height):
        for x in range(width):
            screen["data"][(x, y)] = char

    return screen

def writeTextToScreen(screen : dict, text : str, position : tuple[int, int] = (0, 0)):
    screenWidth, screenHeight = screen["width"], screen["height"]
    for i, char in enumerate(list(text)):
        newX, newY = position[0]+i, position[1]
        if (newX >= 0 and newX < screenWidth) and (newY >= 0 and newY < screenHeight):
            screen["data"][(newX, newY)] = char

def renderScreenToConsole(screen : dict, offset : tuple[int, int] = (0, 0)):
    screenX, screenY = offset
    screenWidth, screenHeight = screen["width"], screen["height"]
    for y in range(SCREEN_HEIGHT):
        line = ""
        for x in range(SCREEN_WIDTH):
            writeData = " "
            if screenX <= x < screenX + screenWidth and screenY <= y < screenY + screenHeight:
                actualX, actualY = x-screenX, y-screenY
                writeData = screen["data"][(actualX, actualY)]
            line += writeData
        print(line)

def clearConsole():
    print("\n" * (SCREEN_HEIGHT + 1))

def getMapTile(mapData, objectData, position):
    if position in objectData:
        return objectData[position]["display"]
    if position in mapData:
        return mapData[position]
    return " "

def generateHealthBar(health, maximumHealth):
    playerHealth, maxHealth = min(health,MAX_HEALTH_RENDER), min(maximumHealth,MAX_HEALTH_RENDER)
    playerHealth = math.floor(playerHealth / 10)
    maxHealth = math.ceil(maxHealth / 10)
    #emptyHearts = totalHearts - filledHearts
    healthBarLines = []
    heartString = ""
    for i in range(0, maxHealth):
        if i < playerHealth:
            heartString += "♥"
        else:
            heartString += "♡"
        if len(heartString) == 20:
            healthBarLines.append(heartString)
            heartString = ""
    healthBarLines.append(heartString)
    return healthBarLines

def show_board(state):
    mapData = state["mapData"]
    objectData = state["objectData"]
    playerData = state["playerData"]
    selectedItem = playerData["selectedItem"]
    board = generateScreen((SCREEN_WIDTH, SCREEN_HEIGHT))
    halfWidth, halfHeight = SCREEN_WIDTH//2, SCREEN_HEIGHT//2
    playerX, playerY = state["playerData"]["position"]
    playerDirection = state["playerData"]["direction"]
    areaX, areaY = playerX-halfWidth, playerY - halfHeight

    for y in range(areaY, areaY + SCREEN_HEIGHT):
        for x in range(areaX, areaX + SCREEN_WIDTH):
            boardX, boardY = x-areaX, y-areaY
            character = getMapTile(mapData, objectData, (x, y))

            if x == playerX and y == playerY:
                character = PLAYER_DIRECTIONS[playerDirection]

            writeTextToScreen(board, character, (boardX, boardY))
    
    healthBarLines = generateHealthBar(playerData["health"], playerData["maximumHealth"])

    for i, line in enumerate(healthBarLines):
        writeTextToScreen(board, line,(0, i))
    selectedText = f"Selected: {selectedItem}"
    writeTextToScreen(board, selectedText, (SCREEN_WIDTH-len(selectedText), 0))
    
    renderScreenToConsole(board)

def getItemDescription(state : dict, itemName : str):
    itemDescription = "No description."
    try:
        desc = state["itemData"][itemName]["description"]
        if desc != "":
            return desc
    except:
        return itemDescription
    return itemDescription

def findItemPage(state : dict, itemName):
    playerInventory = state["playerData"]["inventory"]
    itemIndex = list(playerInventory.keys()).index(itemName)+1
    itemsPerPage = ((SCREEN_HEIGHT-1)//3)
    return math.ceil(itemIndex/itemsPerPage)

def showInventory(state : dict):
    playerInventory = state["playerData"]["inventory"]
    selectedItem = state["playerData"]["selectedItem"]
    page = state["page"]
    itemsPerPage = ((SCREEN_HEIGHT-1)//3) #Space for top bar
    totalPages = math.ceil(len(playerInventory)/itemsPerPage)
    if page > totalPages:
        page = totalPages
    inventory = generateScreen((SCREEN_WIDTH, SCREEN_HEIGHT))
    pageText = f"Page {page}/{totalPages}"
    writeTextToScreen(inventory,"Inventory:")
    writeTextToScreen(inventory,pageText,(SCREEN_WIDTH-len(pageText),0))

    invKeys = list(playerInventory.keys())

    startIndex = itemsPerPage * (page-1)

    nextNextIndex = itemsPerPage * (page)

    for i in range(startIndex, min(nextNextIndex,len(invKeys))):
        itemName, count = invKeys[i], playerInventory[invKeys[i]]
        equippedText = " - Equipped" if itemName == selectedItem else ""
        writeTextToScreen(inventory, f"{i+1}: {itemName} x {count}{equippedText}", (0, 1 + 3 * (i-startIndex)))

        itemDescription = getItemDescription(state, itemName)

        writeTextToScreen(inventory,f"↳ {itemDescription}",(3, 2 + 3 * (i-startIndex)))

    renderScreenToConsole(inventory)

def showHelp(state : dict):
    page = state["page"]
    commandsPerPage = ((SCREEN_HEIGHT-1)//3)
    totalPages = math.ceil(len(COMMANDS)/commandsPerPage)
    if page > totalPages:
        page = totalPages
    helpScreen = generateScreen((SCREEN_WIDTH, SCREEN_HEIGHT))
    pageText = f"Page {page}/{totalPages}"
    writeTextToScreen(helpScreen,"Help:")
    writeTextToScreen(helpScreen,pageText,(SCREEN_WIDTH-len(pageText),0))

    commandKeys = list(COMMANDS.keys())

    startIndex = commandsPerPage * (page-1)
    endIndex = commandsPerPage * page

    for i in range(startIndex, min(endIndex, len(commandKeys))):
        command = commandKeys[i]
        commandArgCount = COMMANDS[command].__code__.co_argcount
        commandArgs = COMMANDS[command].__code__.co_varnames[1:commandArgCount]
        commandAnnotations = COMMANDS[command].__annotations__
        commandsCombined = {command : commandAnnotations[command].__name__ for command in commandArgs}
        argsPretty = ", ".join([f"{arg} : {argType}" for arg, argType in commandsCombined.items()])
        writeTextToScreen(helpScreen, f"• {command}", (0, 1 + 3 * (i-startIndex)))
        if commandArgs:
            writeTextToScreen(helpScreen, f"↳ {argsPretty}", (2, 2 + 3 * (i-startIndex)))

    writeTextToScreen(helpScreen,"https://github.com/jameswnichols/Board-RPG#commands",(0, SCREEN_HEIGHT-1))

    renderScreenToConsole(helpScreen)

def validateTradeInput(inp : str):
    if inp.lower() in ["a", "all"]:
        return "all"
    if inp.lower() in ["c","confirm"]:
        return "confirm"
    elif inp.lower() in ["d", "deny"]:
        return "deny"
    else:
        return "undef"

def showTradeMenu(state : dict, trade : dict):
    state["renderView"] = "showBoard"
    inputItemName, inputItemCount = trade["input"]
    outputItemName, outputItemCount = trade["output"]

    madeTrade = False
    while not madeTrade:

        inputHas, outputHas = getAmountOfItem(state, inputItemName), getAmountOfItem(state, outputItemName)

        tradeScreen = generateScreen((SCREEN_WIDTH, SCREEN_HEIGHT))
        writeTextToScreen(tradeScreen,f"Trade:")

        heightSplit = SCREEN_HEIGHT//4
        writeTextToScreen(tradeScreen,"You Give:",(0, heightSplit * 1))
        writeTextToScreen(tradeScreen,f"{inputItemName} x {inputItemCount} (Have {inputHas})",(0, (heightSplit * 1) + 1))
        writeTextToScreen(tradeScreen,f"↳ {getItemDescription(state, inputItemName)}",(1, (heightSplit * 1) + 2))

        receiveText = ":You Receive"
        writeTextToScreen(tradeScreen,receiveText,(SCREEN_WIDTH-len(receiveText),heightSplit * 3))
        itemInfo = f"{outputItemCount} x {outputItemName} (Have {outputHas})"
        writeTextToScreen(tradeScreen,itemInfo,(SCREEN_WIDTH-len(itemInfo),(heightSplit * 3) + 1))
        outputDesc = f"{getItemDescription(state, outputItemName)} ↲"
        writeTextToScreen(tradeScreen, outputDesc, (SCREEN_WIDTH-len(outputDesc)-1,(heightSplit * 3) + 2))

        playerHasEnough = getAmountOfItem(state, inputItemName) >= inputItemCount

        allCount = inputHas // inputItemCount

        playerHasAll = getAmountOfItem(state, inputItemName) >= allCount

        tradeText = f"(A) to Trade All ({allCount}) / (C) to Confirm / (D) to Deny" if playerHasEnough else "(D) to Deny"
        writeTextToScreen(tradeScreen,tradeText,(0, SCREEN_HEIGHT-1))
        
        clearConsole()
        renderScreenToConsole(tradeScreen)
        userInput = input("> ")
        validated = validateTradeInput(userInput)
        if validated == "deny":
            return
        if validated == "confirm" and playerHasEnough:
            removePlayerItem(state, inputItemName, inputItemCount)
            givePlayerItem(state, outputItemName, outputItemCount)
        if validated == "all" and playerHasAll:
            removePlayerItem(state, inputItemName, allCount * inputItemCount)
            givePlayerItem(state, outputItemName, allCount)

def caughtErrorPage(state : dict, previousState : dict, ex : Exception):
    errorPage = generateScreen((SCREEN_WIDTH, SCREEN_HEIGHT))
    errorName = type(ex).__name__
    errorTraceList = []
    for error in list(traceback.TracebackException.from_exception(ex).format()):
        errorTraceList.extend(error.split("\n"))
    errorTraceList = [x.strip() for x in errorTraceList if x]
    writeTextToScreen(errorPage,"A fatal error has occured:")
    startPositionX, startPositionY = 0, 2
    for trace in errorTraceList:
        startPositionX = 0
        for char in trace:
            writeTextToScreen(errorPage, char, (startPositionX,startPositionY))
            startPositionX += 1
            if startPositionX == SCREEN_WIDTH:
                startPositionX = 0
                startPositionY += 1
        startPositionY += 1
    overwriteState(state, previousState)
    writeTextToScreen(errorPage,"Previous state has been restored!",(0, startPositionY + 1))
    writeTextToScreen(errorPage,"Press Return to continue:",(0, SCREEN_HEIGHT-1))
    clearConsole()
    renderScreenToConsole(errorPage)
    input()

def validateFightInput(userInput : str):
    if userInput.lower() in ["a","attack"]:
        return "attack"
    elif userInput.lower() in ["r","run"]:
        return "run"
    else:
        return "undef"

def fightEnemy(state : dict, location):
    state["renderView"] = "showBoard"
    enemyData = state["objectData"][location]
    enemyName = enemyData["name"]
    enemyDamage = enemyData["damage"]
    fightList = []
    fighting = True
    while fighting:
        fightScreen = generateScreen((SCREEN_WIDTH, SCREEN_HEIGHT))
        enemyHealth, enemyMaxHealth = enemyData["health"], enemyData["maximumHealth"]
        playerHealth, playerMaxHealth = state["playerData"]["health"], state["playerData"]["maximumHealth"]
        playerDamage = state["playerData"]["attackBonus"] + getItemDamage(state, state["playerData"]["selectedItem"])
        playerBlockChance = sum([getItemBlockChance(state, item) * amount for item, amount in state["playerData"]["inventory"].items() if playerHasItem(state, item)])
        writeTextToScreen(fightScreen,"Your Health:")
        enemyNameFormatted = f"{enemyName}'s Health:"
        writeTextToScreen(fightScreen,enemyNameFormatted,(SCREEN_WIDTH-len(enemyNameFormatted), 0))
        for pi, bar in enumerate(generateHealthBar(playerHealth, playerMaxHealth)):
            writeTextToScreen(fightScreen, bar, (0, 1 + pi))
        for ei, bar in enumerate(generateHealthBar(enemyHealth, enemyMaxHealth)):
            writeTextToScreen(fightScreen, bar, (SCREEN_WIDTH-len(bar), 1 + ei))
        bottomOfHealth = (max(max(ei, pi), 1) + 2)
        prevMoveSpace = (SCREEN_HEIGHT - 1 ) - bottomOfHealth
        amountOfPreviousMoves = prevMoveSpace // 2
        startIndex = 0
        if len(fightList) > amountOfPreviousMoves:
            startIndex = len(fightList) - amountOfPreviousMoves
        for attackIndex in range(startIndex, len(fightList)):
            attackText, side = fightList[attackIndex]
            actualY = bottomOfHealth + ((attackIndex - startIndex) * 2)
            if side == "left":
                writeTextToScreen(fightScreen, attackText, (0, actualY))
            else:
                writeTextToScreen(fightScreen, attackText, (SCREEN_WIDTH-len(attackText), actualY))
        writeTextToScreen(fightScreen, f"(A) to Attack for {playerDamage//10} x ♥ / (R) to Run",(0, SCREEN_HEIGHT - 1))
        clearConsole()
        renderScreenToConsole(fightScreen)
        userInput = validateFightInput(input("> "))
        if userInput == "attack":
            newEnemyHealth = 0 if enemyHealth - playerDamage < 0 else enemyHealth - playerDamage
            state["objectData"][location]["health"] = newEnemyHealth
            fightList.append((f"Hit {enemyName} for {playerDamage//10} x ♥","left"))
            if newEnemyHealth == 0:
                dropRolls = getItemRolls(state, getPlayerSelected(state))
                enemyDrops = getDroppedItems(enemyData["drops"],dropRolls)
                for item, amount in enemyDrops.items():
                    givePlayerItem(state, item, amount)
                del state["objectData"][location]
                fighting = False
            else:
                if randomChance(playerBlockChance, 1):
                    fightList.append((f"{enemyName}'s attack blocked ({int(playerBlockChance * 100)}% Chance)","right"))
                else:
                    newPlayerHealth = 0 if playerHealth - enemyDamage < 0 else playerHealth - enemyDamage
                    state["playerData"]["health"] = newPlayerHealth

                    fightList.append((f"{enemyName} hit you for {enemyDamage//10} x ♥","right"))
                    
                    if newPlayerHealth == 0:
                        fighting = False

        if userInput == "run":
            fighting = False

def isPlayerDead(state : dict):
    if not state["playerData"]["health"] == 0:
        return
    state["running"] = False
    deathScreen = generateScreen((SCREEN_WIDTH, SCREEN_HEIGHT))
    deathText = "You Died :("
    deathTextX = SCREEN_WIDTH // 2 - (len(deathText)//2)
    writeTextToScreen(deathScreen, deathText,(deathTextX,(SCREEN_HEIGHT-1) // 2))
    writeTextToScreen(deathScreen,"Press Return to Exit:",(0, SCREEN_HEIGHT - 1))
    clearConsole()
    renderScreenToConsole(deathScreen)
    input("> ")

def renderMap(state):
    mapData = state["mapData"]
    objectData = state["objectData"]
    mapLines = []
    for y in range(MAP_HEIGHT):
        mapLine = []
        for x in range(MAP_WIDTH):
            mapTile = mapData[(x, y)]
            if (x, y) in objectData:
                mapTile = objectData[(x, y)]["display"]
            mapLine.append(mapTile)
        mapLines.append(" ".join(mapLine)+"\n")
    with open("map.txt","w") as f:
        f.writelines(mapLines)

def renderView(state):
    if not state["renderView"]:
        return
    view = state["renderView"]
    if view == "showBoard":
        show_board(state)
    if view == "inventory":
        showInventory(state)
    if view == "help":
        showHelp(state)
    state["renderView"] = None

def getItemRolls(state : dict, itemName : str):
    return 0 if itemName not in state["itemData"] else state["itemData"][itemName]["randomRolls"]

def getPlayerSelected(state : dict):
    return state["playerData"]["selectedItem"]

def playerHasItem(state : dict, itemName : str):
    return (itemName in state["playerData"]["inventory"]) and state["playerData"]["inventory"][itemName] > 0

def getAmountOfItem(state : dict, itemName : str):
    return 0 if not playerHasItem(state, itemName) else state["playerData"]["inventory"][itemName]

def getItemDamage(state : dict, itemName : str):
    return 0 if itemName not in state["itemData"] else state["itemData"][itemName]["itemDamage"]

def getItemBlockChance(state : dict, itemName : str):
    return 0 if itemName not in state["itemData"] else state["itemData"][itemName]["nullifyChance"]

def getPlayerInventory(state : dict):
    return state["playerData"]["inventory"]

def indexOfItem(state : dict, itemName : str):
    if itemName not in getPlayerInventory(state):
        return 0
    return list(getPlayerInventory(state).keys()).index(itemName)

def givePlayerItem(state : dict, itemName : str, itemCount : int):
    if not playerHasItem(state, itemName):
        state["playerData"]["inventory"][itemName] = itemCount
    else:
        state["playerData"]["inventory"][itemName] += itemCount
    updatePlayerOrbs(state)

def removePlayerItem(state : dict, itemName : str, itemCount : int):
    itemAmount = getAmountOfItem(state, itemName)
    if itemAmount > 0:
        amountLeftOver = 0 if itemAmount - itemCount < 0 else itemAmount - itemCount
        state["playerData"]["inventory"][itemName] = amountLeftOver
        if amountLeftOver == 0:
            if getPlayerSelected(state) == itemName:
                itemIndex = indexOfItem(state, getPlayerSelected(state))
                itemIndex = itemIndex - 1 if itemIndex > 0 else itemIndex
                state["playerData"]["selectedItem"] = list(state["playerData"]["inventory"].keys())[itemIndex]
            deletePlayerItem(state, itemName)
    updatePlayerOrbs(state)

def deletePlayerItem(state : dict, itemName : str):
    if itemName in state["playerData"]["inventory"]:
        del state["playerData"]["inventory"][itemName]

def updatePlayerOrbs(state):
    baseHealth = state["playerData"]["baseMaximumHealth"]
    newMaximumHealth = baseHealth + getAmountOfItem(state, "Health Up Orb") * 10
    state["playerData"]["maximumHealth"] = newMaximumHealth
    state["playerData"]["attackBonus"] = getAmountOfItem(state, "Attack Up Orb") * 10

def convertArgs(argList : list):
    convertedList = []
    for arg in argList:
        try:
            convertedList.append(ast.literal_eval(arg))
        except:
            convertedList.append(arg)

    return convertedList

def parseCommand(state : dict, command : str):
    splitCommand = command.strip().split()
    if not splitCommand:
        return
    command = splitCommand[0].lower()
    args = convertArgs(splitCommand[1:])
    if command in COMMANDS:
        functionSignature = inspect.signature(COMMANDS[command])
        #-1 on allParameters and co_argcount because state is always supplied
        allParameters = len(functionSignature.parameters)-1
        #DefaultArgs arent required so arent needed for minimum and are None if there isnt any so 0
        defaultArgs = 0 if not COMMANDS[command].__defaults__ else len(COMMANDS[command].__defaults__)
        necessaryArgcount = COMMANDS[command].__code__.co_argcount-1 - defaultArgs
        if len(args) >= necessaryArgcount and len(args) <= allParameters:
            COMMANDS[command](state, *args)

def show(state : dict, showType : str, page : int = 1):
    if showType in ["board","map"]:
        state["renderView"] = "showBoard"
    if showType in ["inv","inventory"]:
        state["renderView"] = "inventory"
        state["page"] = page if isinstance(page, int) and page > 1 else 1
    if showType in ["help"]:
        state["renderView"] = "help"
        state["page"] = page if isinstance(page, int) and page > 1 else 1

def shiftIndex(l : list, index : int, shift : int):
    direction = -1 if shift < 0 else 1
    currentIndex = index
    for i in range(0, abs(shift)):
        currentIndex += direction
        if currentIndex < 0:
            currentIndex = len(l) - 1
        if currentIndex == len(l):
            currentIndex = 0
    return currentIndex

def changePlayerDirection(state : dict, direction : str):
    if direction in VALID_DIRECTIONS:
        state["playerData"]["direction"] = VALID_DIRECTIONS[direction]
        state["renderView"] = "showBoard"

def validPlayerPosition(state : dict, position : tuple):
    terrainType = state["islandMaskData"][position]
    canTraverse = True
    if terrainType in TERRAIN_REQUIRED_ITEM and not playerHasItem(state, TERRAIN_REQUIRED_ITEM[terrainType]):
        canTraverse = False
    if position in state["objectData"]:
        canTraverse = False

    return canTraverse

def movePlayer(state : dict, moveDirection : str = "f", steps : int = 1):
    state["renderView"] = "showBoard"
    playerX, playerY = state["playerData"]["position"]
    playerDirection = state["playerData"]["direction"]
    directions = list(VALID_DIRECTIONS_LOOKUP.keys())
    playerDirectionIndex = directions.index(playerDirection)
    validMove = True
    moveShift = 0
    if not isinstance(moveDirection, str):
        return
    arg = moveDirection.lower()
    if arg in ["f","for","forwards"]:
        moveShift = 0
    elif arg in ["b","back","backwards"]:
        moveShift = -4
    elif arg in ["l","left"]:
        moveShift = -2
    elif arg in ["r",'right']:
        moveShift = 2
    else:
        validMove = False

    if (not isinstance(steps, int)) or steps <= 0:
        validMove = False

    if validMove:
        shiftedIndex = shiftIndex(directions, playerDirectionIndex, moveShift)
        newDirectionX, newDirectionY = directions[shiftedIndex]
        newPosition = (playerX, playerY)
        wasLastMoveValid = True
        shifted = 0
        while shifted < steps and wasLastMoveValid:
            shifted += 1
            newPosition = (newPosition[0]+newDirectionX,newPosition[1]+newDirectionY)
            if validPlayerPosition(state, newPosition):
                state["playerData"]["position"] = newPosition
                #Might delete
                if shifted < steps:
                    clearConsole()
                    show_board(state)
                    time.sleep(0.1)
            else:
                wasLastMoveValid = False

def equipItem(state : dict, slot : int):
    playerInvKeys = list(state["playerData"]["inventory"].keys())
    if isinstance(slot, int):
        index = slot - 1
        if 0 <= index < len(playerInvKeys):
            itemName = playerInvKeys[index]
            state["playerData"]["selectedItem"] = itemName
            state["renderView"] = "inventory"
            state["page"] = findItemPage(state, itemName)

def harvestTile(state, location):
    objectData = state["objectData"][location]
    selectedItem = getPlayerSelected(state)
    if not objectData["harvestRequires"] or selectedItem in objectData["harvestRequires"]:
        rolls = getItemRolls(state, selectedItem)
        droppedItems = getDroppedItems(objectData["drops"], rolls)
        for item, amount in droppedItems.items():
            givePlayerItem(state, item, amount)
        del state["objectData"][location]

def interactLookup(state : dict):
    state["renderView"] = "showBoard"
    playerX, playerY = state["playerData"]["position"]
    playerDirection = state["playerData"]["direction"]
    interactLocation = (playerX + playerDirection[0], playerY + playerDirection[1])
    #If there is nothing at that spot skip.

    if getAmountOfItem(state,"Med Kit") > 0 and getPlayerSelected(state) == "Med Kit" and state["playerData"]["health"] < state["playerData"]["maximumHealth"]:
        state["playerData"]["health"] = state["playerData"]["maximumHealth"]
        removePlayerItem(state, "Med Kit", 1)
        return

    if not interactLocation in state["objectData"]:
        return
    
    objectAt = state["objectData"][interactLocation]
    objectType = objectAt["objectType"]
    
    if objectType == "villager":
        showTradeMenu(state, objectAt["trade"])
    elif objectType == "intTile":
        harvestTile(state, interactLocation)
    elif objectType == "enemy":
        fightEnemy(state, interactLocation)

def overwriteState(state : dict, newState : dict):
    for key, value in newState.items():
        state[key] = value

def saveGame(state : dict, filename : str):
    if not filename:
        return
    filename = filename+".sav"
    with open(filename, "wb") as f:
        pickle.dump(state, f)
    state["renderView"] = "showBoard"

def loadGame(state : dict, filename : str):
    if not filename:
        return
    filename = filename+".sav"
    with open(filename, "rb") as f:
        overwriteState(state, pickle.load(f))
    state["renderView"] = "showBoard"

def handleAutosave(state : dict):
    if time.time() - state["autosaveTimestamp"] > AUTOSAVE_SECONDS:
        state["autosaveTimestamp"] = time.time()
        saveGame(state, "autosave")

def giveAllItems(state : dict):
    for item, data in state["itemData"].items():
        givePlayerItem(state, item, 1000)

COMMANDS = {
    "show" : show,
    "dir" : changePlayerDirection,
    "face" : changePlayerDirection,
    "move" : movePlayer,
    "equip" : equipItem,
    "select" : equipItem,
    "i" : interactLookup,
    "med" : interactLookup,
    "interact" : interactLookup,
    "cut" : interactLookup,
    "mine" : interactLookup,
    "trade" : interactLookup,
    "attack" : interactLookup,
    "save" : saveGame,
    "load" : loadGame,
    "giveall" : giveAllItems,
    "rendermap" : renderMap,
}

def generateItem(itemData, itemName : str, itemDamage : str, nullifyChance : int, randomRolls : int, description : str):
    itemData[itemName] = {"itemDamage":itemDamage,"nullifyChance":nullifyChance,"randomRolls":randomRolls,"description":description}

def generateItemData(itemData : dict):
    generateItem(itemData, "Axe", 10, 0, 1,"Can cut trees and does 1 x ♥.")
    generateItem(itemData, "Lumber Axe", 30, 0, 2, "Can cut trees, does 3 x ♥ and has 2 x drop rates.")
    generateItem(itemData, "Wood", 0, 0, 1, "A Common resource that's useful for trading.")
    generateItem(itemData, "Stone", 0, 0, 1, "A tough material that's useful for trading.")
    generateItem(itemData, "Gem", 0, 0, 1, "A rare gem that's valuable to Villagers.")
    generateItem(itemData, "Skill Fragment", 0, 0, 1,"Collect 10 to convert their energy via trading.")
    generateItem(itemData, "Health Up Orb", 0, 0, 1,"Increases your maximum health by 1 x ♥.")
    generateItem(itemData, "Attack Up Orb", 0, 0, 1,"Increases your damage by 1 x ♥.")
    generateItem(itemData, "Pickaxe", 10, 0, 1,"Can break rocks and does 1 x ♥.")
    generateItem(itemData, "Miner's Pickaxe", 10, 0, 2,"Can break rocks, does 1 x ♥ and has 2 x drop rates.")
    generateItem(itemData, "Goblin Club", 30, 0, 1,"Does 3 x ♥.")
    generateItem(itemData, "Soldier's Sword", 50, 0, 1,"Does 5 x ♥.")
    generateItem(itemData, "Knight's Sword", 70, 0, 2,"Does 7 x ♥ and has 2 x drop rates.")
    generateItem(itemData, "Ogre Club", 70, 0.05, 1,"Does 7 x ♥ and has a 5% chance to block.")
    generateItem(itemData, "King's Sword", 5000, 0, 5,"Does 500 x ♥ and has 5 x drop rates.")
    generateItem(itemData, "Goblin Shield", 0, 0.05, 1,"Has a 5% chance to block.")
    generateItem(itemData, "Soldier's Shield", 0, 0.10, 1,"Has a 10% chance to block.")
    generateItem(itemData, "Knight's Shield", 0, 0.20, 1,"Has a 20% chance to block.")
    generateItem(itemData, "King's Shield", 0, 1, 1,"Blocks all attacks.")
    generateItem(itemData, "Snow Boots", 0, 0, 1,"Needed to traverse hill tiles.")
    generateItem(itemData, "Ice Picks", 0, 0, 1,"Needed to climb mountain tiles.")
    generateItem(itemData, "Med Kit", 0, 0, 1,"Heals you back to full health immediately.")

def generateState():
    state = {"autosaveTimestamp":time.time(),"running":True,"renderView":None,"page":1,"playerData":{"health":100,"maximumHealth":100,"baseMaximumHealth":100,"attackBonus":0,"position":(0, 0),"direction":(0, 1),"inventory":{"Pickaxe" : 1, "Axe" : 1}, "selectedItem":"Axe"},"mapData":{},"objectData":{},"islandMaskData":{},"itemData":{}}

    generateItemData(state["itemData"])

    generateMap(state)

    return state

def main():
    state = generateState()

    while state["running"]:
        previousState = copy.deepcopy(state)
        try:
            handleAutosave(state)
            isPlayerDead(state)
            if state["running"]:
                clearConsole()
                renderView(state)
                playerCommand = input("Command > ")
                parseCommand(state, playerCommand)
        except Exception as e:
            caughtErrorPage(state, previousState, e)

if __name__ == "__main__":
    main()

    