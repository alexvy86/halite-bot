"""My Halite Bot"""

import logging, logging.config
from hlt import * # pylint: disable=W0401,W0614
from networking import * # pylint: disable=W0401,W0614
import util

def move(location, game_map, bot_id):
    """Defines the move logic for the bot"""
    site = game_map.getSite(location)

    # This strategy prioritizes expansion

    # Conquer neighbors that can be conquered
    for direction in CARDINALS:
        neighbour_site = game_map.getSite(location, direction)
        if neighbour_site.owner != MY_ID and neighbour_site.strength < site.strength:
            return Move(location, direction)

    # Do not stay still if the site's production will cause strength to go past the cap (255)
    if site.strength + site.production > 255:
        return Move(location, NORTH if random.random() > 0.5 else WEST)

    # Stay still until strength is 5 times the site's production
    if site.strength < site.production * 5:
        return Move(location, STILL)

    # Move randomly here, within our territory, north or west
    owned_directions = [d for d in CARDINALS if game_map.getSite(location, d).owner == bot_id]
    if len(owned_directions) > 0:
        return Move(location, random.choice(owned_directions))

    # Default, stay still
    return Move(location, STILL)

def main(bot_id, game_map):
    """Main logic of the bot"""

    # Initialize logging
    #logging.config.fileConfig("logging_config.ini")

    # Get maps
    prod_map = []
    strength_map = []
    for y in range(game_map.height): # pylint: disable=C0103
        prod_row = [game_map.getSite(Location(x, y)).production for x in range(game_map.width)]
        prod_map.append(prod_row)
        strength_row = [game_map.getSite(Location(x, y)).strength for x in range(game_map.width)]
        strength_map.append(strength_row)
    #logging.info("PRODUCTION MAP\r\n" + util.formatMatrix(prod_map))
    #logging.info("STRENGTH MAP\r\n" + util.formatMatrix(strength_map))

    while True:
        moves = []
        game_map = getFrame()
        for y in range(game_map.height): # pylint: disable=C0103
            for x in range(game_map.width): # pylint: disable=C0103
                loc = Location(x, y)
                if game_map.getSite(loc).owner == bot_id:
                    moves.append(move(loc, game_map, bot_id))
        sendFrame(moves)

MY_ID, GAME_MAP = getInit()
sendInit("Oldbot")

main(MY_ID, GAME_MAP)
