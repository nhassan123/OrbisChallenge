from PythonClientAPI.game.PointUtils import *
from PythonClientAPI.game.Entities import FriendlyUnit, EnemyUnit, Tile
from PythonClientAPI.game.Enums import Team
from PythonClientAPI.game.World import World


class PlayerAI:

    def __init__(self):
        ''' Initialize! '''
        self.turn_count = 0             # game turn count
        self.target = None              # target to send unit to!
        self.outbound = True            # is the unit leaving, or returning?
        self.returnposition = None
        self.default = (5,2)

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
        :param enemy_units: list of EnemyUnit objectb
         '''       
        directions = [(0,1), (1,0), (0,-1),(-1,0)]
        enemybodies = []
        enemyheads = []
        for enemy in enemy_units:
            enemybodies.append(enemy.body)
            enemyheads.append(enemy.position)
   
        def outboundCall(point):
             friendly_unit.move(point)
            
        # increment turn count
        self.turn_count += 1

        '''if self.turn_count<=1:
           if friendly_unit.position == (3,3):
                self.default=(5,-2)
           elif friendly_unit.position == (3,26):
                self.default=(2,5)
           elif friendly_unit.position == (26,3):
                self.default=(-5,-2)
           elif friendly_unit.position == (26,26):
                self.default=(-2,5)
           else:
                self.default=(-2,5)'''

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
        if self.outbound and self.target is None and self.turn_count<=100:
            edges = [tile for tile in world.util.get_friendly_territory_edges()]
            avoid = []
            for edge in edges:
                avoid += [pos for pos in world.get_neighbours(edge.position).values()]
            point = add_points(friendly_unit.position, self.default)
            if world.is_within_bounds(point) and world.is_edge(point)==False:
                self.target = world.util.get_closest_capturable_territory_from(point, avoid) 
            else:
                self.target = world.util.get_closest_capturable_territory_from(friendly_unit.position, avoid)
            if self.target.is_edge:
                self.target = world.util.get_closest_capturable_territory_from(friendly_unit.position, avoid)
            self.returnposition = friendly_unit.position




        if self.outbound and self.target is None and self.turn_count > 100:
           dictDir = []
           dirScore = []

           edges = [tile for tile in world.util.get_friendly_territory_edges()]
           avoid = []
           for edge in edges:
                avoid += [pos for pos in world.get_neighbours(edge.position).values()]
           self.returnposition = friendly_unit.position
           for i in range(0,4):
               score = 0
               newpoint = add_points(directions[i], friendly_unit.position)
               dictDir.append(newpoint)
               self.target = world.util.get_closest_capturable_territory_from(newpoint, avoid)
               
               if newpoint in enemybodies:
                     score += 10
               if newpoint == self.target.position:
                     score += 10
               if newpoint in world.neutral_points:
                     score += 15
               if newpoint in enemyheads:
                     score -= 20
               if world.is_within_bounds(newpoint) == False:
                     score = -10000
               if world.is_within_bounds(newpoint) == True:
                  if world.is_wall(newpoint) == True:
                     score = -10000
               if world.is_edge(newpoint) == True:
                     score = -10000
               dirScore.append(score)
           bestScore = max(dirScore)
           bestScoreIndex = dirScore.index(bestScore)
           bestPoint = dictDir[bestScoreIndex]
           self.target = world.util.get_closest_capturable_territory_from(bestPoint, avoid)
           outboundCall(bestPoint)


            

        # else if inbound and no target set, set target as the closest friendly tile
        elif not self.outbound and self.target is None:
            flag = 0 
            
            for i in range(0,4):
                newpoint=add_points(friendly_unit.position, directions[i])
                self.target = world.util.get_closest_friendly_territory_from(newpoint, None)
                if self.target.is_friendly:
                    flag = 1
                    break
            if flag != 1:
            #self.target = corners[0]
                point = add_points(friendly_unit.position, (-3,1))
            #self.target = world.util.get_closest_friendly_territory_from(point, None)
                if world.is_within_bounds(point):
                      self.target = world.util.get_closest_friendly_territory_from(self.point, None)
                else:
                      self.target = world.util.get_closest_friendly_territory_from(self.returnposition, None)
                      

        # set next move as the next point in the path to target
        next_move = world.path.get_shortest_path(friendly_unit.position, self.target.position, friendly_unit.snake)[0]

        # move!
        friendly_unit.move(next_move)
        print("Turn {0}: currently at {1}, making {2} move to {3}.".format(
            str(self.turn_count),
            str(friendly_unit.position),
            'outbound' if self.outbound else 'inbound',
            str(self.target.position)
        ))
