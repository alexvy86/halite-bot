import logging, logging.config
from hlt import *
from networking import *
import util

def move(location):
    site = gameMap.getSite(location)

    # This strategy prioritizes expansion
    
    # Conquer neighbors that can be conquered
    for d in CARDINALS:
        neighbour_site = gameMap.getSite(location, d)
        if neighbour_site.owner != myID and neighbour_site.strength < site.strength:
            return Move(location, d)
    
    # Do not stay still if the site's production will cause strength to go past the cap (255)
    if site.strength + site.production > 255:
        return Move(location, NORTH if random.random() > 0.5 else WEST) 

    # Stay still until strength is 5 times the site's production
    if site.strength < site.production * 5:
        return Move(location, STILL)    

    return Move(location, STILL)

myID, gameMap = getInit()
sendInit("MyPythonBot")

# Initialize logging
logs_directory = "logs" 
logging.config.fileConfig("logging_config.ini")

# Get maps
prodMap = []
strengthMap = []
for y in range(gameMap.height):
    prodMap.append([gameMap.getSite(Location(x, y)).production for x in range(gameMap.width)])
    strengthMap.append([gameMap.getSite(Location(x, y)).strength for x in range(gameMap.width)])
logging.info("PRODUCTION MAP\r\n" + util.formatMatrix(prodMap))
logging.info("STRENGTH MAP\r\n" + util.formatMatrix(strengthMap))

while True:
    moves = []
    gameMap = getFrame()
    for y in range(gameMap.height):
        for x in range(gameMap.width):
            location = Location(x, y)
            if gameMap.getSite(location).owner == myID:
                moves.append(move(location))
    sendFrame(moves)
