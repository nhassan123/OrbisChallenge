from PythonClientAPI.game.PointUtils import *
from PythonClientAPI.game.Entities import FriendlyUnit, EnemyUnit, Tile
from PythonClientAPI.game.Enums import Team
from PythonClientAPI.game.World import World
from PythonClientAPI.game.TileUtils import TileUtils

class PlayerAI:

    def __init__(self):
        ''' Initialize! '''
        self.turn_count = 0             # game turn count
        self.target = None              # target to send unit to!
        self.outbound = True            # is the unit leaving, or returning?
        self.point_addition = (1, 1)

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

        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        total_height = world.height
        total_width = world.width

        # increment turn count
        self.turn_count += 1

        if self.turn_count % 5 == 0:
            self.target = None
            self.outbound = False

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
            closest_enemy_body_tile = world.util.get_closest_enemy_body_from(friendly_unit.position, None)
            if closest_enemy_body_tile and closest_enemy_body_tile.position in [
                add_points(friendly_unit.position, directions[0]),
                add_points(friendly_unit.position, directions[1]),
                add_points(friendly_unit.position, directions[2]),
                add_points(friendly_unit.position, directions[3]),
            ]:
                print('target is closest enemy body')
                self.target = closest_enemy_body_tile
            else:
                edges = [tile for tile in world.util.get_friendly_territory_edges()]
                avoid = []
                for edge in edges:
                    avoid += [pos for pos in world.get_neighbours(edge.position).values()]

                self.target = world.util.get_closest_capturable_territory_from(friendly_unit.position, avoid)
                # for i in range(0, 5):
                #     self.target = world.util.get_closest_neutral_territory_from(self.target.position, avoid)
                print('target is closest neutral territory')

        # else if inbound and no target set, set target as the closest friendly tile
        elif not self.outbound and self.target is None:
            self.target = world.util.get_closest_friendly_territory_from(friendly_unit.position, None)

        # set next move as the next point in the path to target PLUS OUR OWN CODE
        elif self.target.position in list(friendly_unit.territory):
            print('inside')
            self.target = world.util.get_closest_capturable_territory_from(self.target, None)

        elif not self.outbound and self.turn_count % 5 == 0:
            self.target = world.util.get_closest_friendly_territory_from(friendly_unit.position, None)

        shortest_path = world.path.get_shortest_path(friendly_unit.position, self.target.position, friendly_unit.snake)
        if shortest_path:
            print('shortest path', friendly_unit.position, self.target.position, friendly_unit.snake)
            next_move = shortest_path[0]
        else:
            edges = [tile for tile in world.util.get_friendly_territory_edges()]
            avoid = []
            for edge in edges:
                avoid += [pos for pos in world.get_neighbours(edge.position).values()]
            print('no shortest path')
            next_move = world.util.get_closest_neutral_territory_from(friendly_unit.position, avoid).position

        # move!
        friendly_unit.move(next_move)

        # # set next move as the next point in the path to target
        # added_target = add_points(self.target.position, self.point_addition)
        # while world.is_within_bounds(added_target) == False or world.is_wall(added_target) or world.is_edge(added_target):
        #     print('added target is not within bounds')
        #     added_target = sub_points(added_target, (1, 1))
        #
        # if added_target[0] > total_width and added_target[1] > total_height:
        #     added_target = (total_width - 1, total_height - 1)
        # elif added_target[0] > total_width:
        #     added_target = (total_width - 1, added_target[1])
        # elif added_target[1] > total_height:
        #     added_target = (added_target[0], total_height - 1)
        #
        # print(added_target, 'ADDED TARGET', total_height, total_width)
        # print('get shortest path args', friendly_unit.position, added_target, friendly_unit.snake)
        # shortest_path = world.path.get_shortest_path(friendly_unit.position, added_target, friendly_unit.snake)
        # if shortest_path is None:
        #     direction = 0
        #     next_move = add_points(friendly_unit.position, directions[direction])
        #     while (world.is_within_bounds(next_move) == False or world.is_wall(next_move) or world.is_edge(next_move)) and direction < 4:
        #         direction += 1
        #         next_move = add_points(friendly_unit.position, directions[direction])
        # # else:
        # #     next_move = shortest_path[0]
        #
        # # move!
        # friendly_unit.move(next_move)
        print("Turn {0}: currently at {1}, making {2} move to {3}.".format(
            str(self.turn_count),
            str(friendly_unit.position),
            'outbound' if self.outbound else 'inbound',
            str(self.target.position)
        ))
