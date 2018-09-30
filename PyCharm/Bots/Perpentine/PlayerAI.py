from PythonClientAPI.game.PointUtils import *
from PythonClientAPI.game.Entities import FriendlyUnit, EnemyUnit, Tile
from PythonClientAPI.game.Enums import Direction
from PythonClientAPI.game.World import World
from PythonClientAPI.game.TileUtils import TileUtils
from PythonClientAPI.game.FloodFiller import FloodFiller

class PlayerAI:

    def __init__(self):
        ''' Initialize! '''
        self.turn_count = 0             # game turn count
        self.target = None              # target to send unit to!
        self.outbound = True            # is the unit leaving, or returning?

    def do_move(self, world, friendly_unit, enemy_units):
        '''
        This method is called every turn by the game engine.
        Make sure you call friendly_unit.move(target) somewhere here!

        Below, you'll find a very rudimentary strategy to get you started.
        Feel free to use, or delete any part of the provided code - Good luck!

        :param world: world object (more information on the documentation)
            - world: contains information about the game map.
            - world.path: contains various pathfinding helper methods.
            - world.util: contains various tile-finding helper methods.
            - world.fill: contains various flood-filling helper methods.

        :param friendly_unit: FriendlyUnit object
        :param enemy_units: list of EnemyUnit objects
        '''

        def get_score(point):
            if world.is_within_bounds(point) == False:
                return -1000

            score = 0
            next_tile = world.position_to_tile_map[(point)]
            if next_tile.is_neutral and next_tile.head is None:
                score += 2
            elif next_tile.is_enemy:
                score += 2
            elif next_tile.head != None:
                score -= 1000

            flood_filler = FloodFiller(world)
            score += flood_filler.flood_fill(friendly_unit.body, friendly_unit.territory, friendly_unit.position, point)
            return score



        def evaluation_function(world, friendly_unit, enemy_units):
            up_point = add_points(friendly_unit.position, (1, 0))
            right_point = add_points(friendly_unit.position, (0, 1))
            down_point = add_points(friendly_unit.position, (-1, 0))
            left_point = add_points(friendly_unit.position, (0, -1))

            points = [up_point, right_point, down_point, left_point]
            scores = [get_score(up_point), get_score(right_point), get_score(down_point), get_score(left_point)]
            max_score = max(scores)
            max_index = scores.index(max_score)
            print('NEXT POINT', points[max_index])
            return points[max_index]

        # increment turn count
        self.turn_count += 1

        # if unit is dead, stop making moves.
        if friendly_unit.status == 'DISABLED':
            print("Turn {0}: Disabled - skipping move.".format(str(self.turn_count)))
            self.target = None
            self.outbound = True
            return

        # if unit reaches the target point, reverse outbound boolean and set target back to None
        if self.target is not None and friendly_unit.position == self.target.position:
            self.outbound = not self.outbound
            self.target = None

        # if outbound and no target set, set target as the closest capturable tile at least 1 tile away from your territory's edge.
        if self.outbound and self.target is None:
            edges = [tile for tile in world.util.get_friendly_territory_edges()]
            avoid = []
            for edge in edges:
                avoid += [pos for pos in world.get_neighbours(edge.position).values()]
            self.target = world.util.get_closest_capturable_territory_from(friendly_unit.position, avoid)

        # else if inbound and no target set, set target as the closest friendly tile
        elif not self.outbound and self.target is None:
            self.target = world.util.get_closest_friendly_territory_from(friendly_unit.position, None)

        # set next move as the next point in the path to target

        next_move = evaluation_function(world, friendly_unit, enemy_units)
        # next_move = world.path.get_shortest_path(friendly_unit.position, self.target.position, friendly_unit.snake)[0]

        # move!
        friendly_unit.move(next_move)
        print("Turn {0}: currently at {1}, making {2} move to {3}.".format(
            str(self.turn_count),
            str(friendly_unit.position),
            'outbound' if self.outbound else 'inbound',
            str(self.target.position)
        ))
