"""My Halite Bot"""

import logging, logging.config
import hlt
from hlt import NORTH, EAST, SOUTH, WEST, STILL, Move, Square
import util
import itertools
import operator

def determineDirection(source_square, target_square, game_map):
    dif_x = target_square.x - source_square.x
    dif_y = target_square.y - source_square.y
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

def move(square, game_map, bot_id, outer_perimeter_noman, outer_perimeter_enemy):
    """Defines the move logic for the bot"""
    
    # Stay still until strength is 5 times the site's production
    if square.strength < square.production * 5:
        return Move(square, STILL)

    #sorted_noman = sorted([x for x in outer_perimeter_noman], key=(lambda y: y.strength))
    #sorted_battle = sorted([x for x in outer_perimeter_enemy], key=(lambda y: y.strength))
    #choke_points = sorted_noman[0:4] # + sorted_battle[0:3]
    
    perimeter = outer_perimeter_enemy + outer_perimeter_noman
    perimeter = [(game_map.get_distance(p, square), p) for p in perimeter]
    logging.debug("Location: {0}".format((square.x,square.y)))
    logging.debug("Perimeter: {0}".format([(p[1].x,p[1].y) for p in perimeter]))
    
    min_dist_to_perimeter = min(x[0] for x in perimeter)
    perimeter = [p[1] for p in perimeter if p[0] == min_dist_to_perimeter]

    target_point = sorted(perimeter, key=lambda perimeter_point: perimeter_point.strength)[0]
    
    logging.debug("Determined target_point {0} from Location {1}".format(str(target_point), square))
    direction = determineDirection(square, target_point, game_map)
    logging.debug("Determined direction {0}".format(direction))
    
    # Only conquer when doable in a single move
    neighbour = game_map.get_target(square, direction)
    if neighbour.owner == bot_id:
        return Move(square, direction)
    elif neighbour.strength < square.strength:
        return Move(square, direction)
    else:
        return Move(square, STILL)

def main(bot_id, game_map):
    """Main logic of the bot"""

    # Initialize logging
    logging.config.fileConfig("logging_config.ini")

    # Get maps
    prod_map = []
    strength_map = []
    matrix_map = []
    for k, g in itertools.groupby(game_map, key=operator.attrgetter('y')):
        matrix_map.append(g)
    prod_map = [map(operator.attrgetter('production'), row) for row in matrix_map]
    strength_map = [map(operator.attrgetter('strength'), row) for row in matrix_map]    
    logging.info("PRODUCTION MAP\r\n" + util.formatMatrix(prod_map))
    logging.info("STRENGTH MAP\r\n" + util.formatMatrix(strength_map))

    try:
        while True:
            game_map.get_frame()

            # Analyze map
            outer_perimeter_enemy = []
            outer_perimeter_noman = []
            players = {}

            # Analyze map
            for square in game_map:
                if square.owner == bot_id:
                    # Determine perimeter
                    for neighbour in game_map.neighbors(square):
                        if neighbour.owner == 0:
                            outer_perimeter_noman.append(neighbour)
                        elif neighbour.owner != bot_id:
                            outer_perimeter_enemy.append(neighbour)

            # Determine moves
            moves = []
            for square in game_map:
                if square.owner == bot_id:
                    moves.append(move(square, game_map, bot_id, outer_perimeter_noman, outer_perimeter_enemy))

            hlt.send_frame(moves)
    except:
        logging.exception("Unexpected error")
        raise

MY_ID, GAME_MAP = hlt.get_init()
hlt.send_init("alexvy86")

main(MY_ID, GAME_MAP)
