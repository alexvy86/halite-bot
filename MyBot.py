"""My Halite Bot"""

import logging, logging.config
from hlt import * # pylint: disable=W0401,W0614
from networking import * # pylint: disable=W0401,W0614
import util

def determineDirection(source_location, target_location, game_map):
    dif_x = target_location.x - source_location.x
    dif_y = target_location.y - source_location.y
    if abs(dif_x) >= game_map.width/2:
        dif_x = -(game_map.width - dif_x)
    if abs(dif_y) >= game_map.height/2:
        dif_y = -(game_map.height - dif_y)
    if dif_y == 0:
        return EAST if dif_x > 0 else WEST
    elif dif_x == 0:
        return SOUTH if dif_y > 0 else NORTH
    elif abs(dif_x) < abs(dif_y):
        return EAST if dif_x > 0 else WEST
    else:
        return SOUTH if dif_y > 0 else NORTH

def move(location, game_map, bot_id, outer_perimeter_noman, outer_perimeter_enemy):
    """Defines the move logic for the bot"""
    site = game_map.getSite(location)

    # Stay still until strength is 5 times the site's production
    if site.strength < site.production * 5:
        return Move(location, STILL)

    perimeter = outer_perimeter_enemy + outer_perimeter_noman
    perimeter = [(game_map.getDistance(p[0], location), p[0], p[1]) for p in perimeter]
    logging.debug("Location: {0}".format((location.x,location.y)))
    logging.debug("Perimeter: {0}".format([(p[1].x,p[1].y) for p in perimeter]))
    
    min_dist_to_perimeter = min(x[0] for x in perimeter)
    perimeter = filter(lambda x: x[0] == min_dist_to_perimeter, perimeter)

    target_point = sorted(perimeter, key=lambda perimeter_point: perimeter_point[2].strength)[0]
    
    logging.debug("Determined target_point {0} from Location {1}".format((str(target_point[0]), str(target_point[1])), location))
    direction = determineDirection(location, target_point[1], game_map)
    logging.debug("Determined direction {0}".format(direction))
    
    # Only conquer when doable in a single move
    neighbour_site = game_map.getSite(location, direction)
    if neighbour_site.owner == bot_id:
        return Move(location, direction)
    elif neighbour_site.strength < site.strength:
        return Move(location, direction)
    else:
        return Move(location, STILL)

def main(bot_id, game_map):
    """Main logic of the bot"""

    # Initialize logging
    logging.config.fileConfig("logging_config.ini")

    # Get maps
    prod_map = []
    strength_map = []
    for y in range(game_map.height): # pylint: disable=C0103
        prod_row = [game_map.getSite(Location(x, y)).production for x in range(game_map.width)]
        prod_map.append(prod_row)
        strength_row = [game_map.getSite(Location(x, y)).strength for x in range(game_map.width)]
        strength_map.append(strength_row)
    logging.info("PRODUCTION MAP\r\n" + util.formatMatrix(prod_map))
    logging.info("STRENGTH MAP\r\n" + util.formatMatrix(strength_map))

    try:
        while True:
            game_map = getFrame()

            # Analyze map
            outer_perimeter_enemy = []
            outer_perimeter_noman = []
            players = {}
            for y in range(game_map.height): # pylint: disable=C0103
                for x in range(game_map.width): # pylint: disable=C0103
                    loc = Location(x, y)
                    site = game_map.getSite(loc)
                    if site.owner not in players:
                        players[site.owner] = {'locations':[], 'territory': 0, 'production':0, 'strength':0}
                    players[site.owner]['locations'].append(loc)
                    players[site.owner]['territory'] += 1
                    players[site.owner]['production'] += site.production
                    players[site.owner]['strength'] += site.strength

                    if site.owner == bot_id:
                        # Analyze perimeter
                        for direction in CARDINALS:
                            neighbour_loc = game_map.getLocation(loc, direction)
                            neighbour_site = game_map.getSite(loc, direction)
                            if neighbour_site.owner == 0:
                                outer_perimeter_noman.append((neighbour_loc, neighbour_site))
                            elif neighbour_site.owner != bot_id:
                                outer_perimeter_enemy.append((neighbour_loc, neighbour_site))

            # Determine moves
            moves = []
            for y in range(game_map.height): # pylint: disable=C0103
                for x in range(game_map.width): # pylint: disable=C0103
                    loc = Location(x, y)
                    if game_map.getSite(loc).owner == bot_id:
                        moves.append(move(loc, game_map, bot_id, outer_perimeter_noman, outer_perimeter_enemy))

            sendFrame(moves)
    except:
        logging.exception("Unexpected error")
        raise

MY_ID, GAME_MAP = getInit()
sendInit("alexvy86")

main(MY_ID, GAME_MAP)
