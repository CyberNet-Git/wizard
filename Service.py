import pygame
import random
import yaml
import os
from abc import ABC, abstractmethod

import const
import Objects
import Sprite

OBJECT_TEXTURE = os.path.join("texture", "objects")
ENEMY_TEXTURE = os.path.join("texture", "enemies")
ALLY_TEXTURE = os.path.join("texture", "ally")

DEFAULT_SPRITE_SIZE = 32
STATIC_TEXTURES = os.path.join("texture", "tilemap.png")
HERO_TILEMAP = os.path.join("texture", "Hero", "Soldier 06-1.png")

object_list =[]

class MapFactory(yaml.YAMLObject):

    @classmethod
    def from_yaml(cls, loader, node):
        _map = cls.Map()
        config = loader.construct_mapping(node)
        config = config if config != {} else None
        _obj = cls.Objects(config)
        return {'map': _map, 'obj': _obj}


class AbstractMap(ABC):
    def __init__(self):
        # TODO generate map using "@life" 
        # https://gamedevelopment.tutsplus.com/tutorials/generate-random-cave-levels-using-cellular-automata--gamedev-9664
        self.num = random.randint(0,7)# sprite template number from SpriteProvider
        self.chanceToStartAlive = 0.35
        self.death_limit = 3
        self.birth_limit = 4

        self.generateMap()

        #self.Map = [[const.FLOOR + self.num for _ in range(41)] for _ in range(41)]
        for i in range(41):
            for j in range(41):
                if i == 0 or j == 0 or i == 40 or j == 40:
                    self.Map[j][i] = const.BORDER + self.num
                elif self.Map[j][i] == 0:
                    self.Map[j][i] = const.FLOOR + self.num
                else:
                    self.Map[j][i] = const.WALL + self.num
    
    def map_init(self):
        for i, r in enumerate(self.Map):
            for j, c in enumerate(r):
                self.Map[i][j] = 1 if random.random() < self.chanceToStartAlive else 0

    def generateMap(self):
        #Create a new map
        self.Map = [[0 for _ in range(41)] for _ in range(41)]
        self.map_init()
        # And now run the simulation for a set number of steps
        for i in range(3):
            self.Map = self.doSimulationStep()

    def doSimulationStep(self):
        new_map = self.Map.copy()
        # Loop over each row and column of the map
        for i, x in enumerate(self.Map):
            for j, y in enumerate(x):
                nbs = self.countAliveNeighbours(i, j)
                # The new value is based on our simulation rules
                # First, if a cell is alive but has too few neighbours, kill it.
                if self.Map[i][j]:
                    if nbs < self.death_limit:
                        new_map[i][j] = 0
                    else:
                        new_map[i][j] = 1
                # Otherwise, if the cell is dead now, check if it has the right number of neighbours to be 'born'
                else:
                    if nbs > self.birth_limit:
                        new_map[i][j] = 1
                    else:
                        new_map[i][j] = 0
        return new_map

    # Returns the number of cells in a ring around (x,y) that are alive.
    def countAliveNeighbours(self, x, y):
        count = 0
        for i in [-1, 0, 1]:
            for j in [-1, 0, 1]:
                neighbour_x = x + i
                neighbour_y = y + j
                # If we're looking at the middle point
                if i == 0 and j == 0:
                    # Do nothing, we don't want to add ourselves in!
                    pass
                # In case the index we're looking at it off the edge of the map
                elif neighbour_x < 0 or neighbour_y < 0 or neighbour_y >= len(self.Map) or neighbour_x >= len(self.Map[0]):
                    count += 1
                # Otherwise, a normal check of the neighbour
                elif self.Map[neighbour_x][neighbour_y]:
                    count += 1
        return count

    def get_map(self):
        return self.Map

    def draw(self, game_surface):
        if self.Map:
            for i in range(game_surface.map_left, game_surface.map_left + game_surface.win_width ): # +1
                for j in range(game_surface.map_top, game_surface.map_top + game_surface.win_height ): # +1 removed
                    try:
                        sprite = Sprite.provider.get_sprite('map', self.Map[j][i] - self.Map[j][i] % 10, self.Map[j][i] % 10 )
                        img = sprite.get_sprite(game_surface.sprite_size)
                        game_surface.blit(img, game_surface.map_to_surface((i, j)) )
                    except:
                        pass
        else:
            self.fill(colors["white"])
    
    def can_move(self, x, y):
        return self.Map[x][y] - self.Map[x][y] % 10 not in (const.WALL, const.BORDER)


class AbstractObjects(ABC):
    def __init__(self, config={}):
        self.objects = []
        self.config = {}
        self.config['enemies'] = config

    @abstractmethod
    def get_objects(self, _map):
        return self.objects

    def make_config(self, obj_type, config=None):
        if config is None:
            self.config[obj_type] = self.get_defaults(obj_type)
        else:
            self.config[obj_type] = config

    def add_objects(self, config=None):
        self.make_config('objects', config)

    def add_ally(self, config=None):
        self.make_config('ally', config)

    def add_enemies(self, config=None):
        self.make_config('enemies', config)

    def get_coord(self, _map):
        coord = (random.randint(1, 39), random.randint(1, 39))
        intersect = True
        while intersect:
            intersect = False
            if _map.Map[coord[1]][coord[0]] // 10 * 10 != const.FLOOR :
                intersect = True
                coord = (random.randint(1, 39),
                            random.randint(1, 39))
                continue
            for obj in self.objects:
                if coord == obj.position or coord == (1, 1):
                    intersect = True
                    coord = (random.randint(1, 39),
                                random.randint(1, 39))
        return coord

    def get_defaults(self, object_type):
        _config = {}
        #FIXME генерация объектов сломалась после рефактора
        for obj_name in object_list[object_type]:
            min_count = 0
            max_count = 5
            prop = object_list[object_type][obj_name]
            try:
                min_count = prop['min-count']
                max_count = prop['max-count']
            except:
                pass
            _config[obj_name] = random.randint(min_count, max_count)
        return _config

    def make_objects(self, _map):
        for object_type in self.config:
            for obj_name in self.config[object_type]: #  object_list_prob[]:
                count = self.config[object_type][obj_name]
                prop = object_list[object_type][obj_name]
                # prop[sprite] - это только имя файла.  СПРАЙТ нужно еще получить тут.
                for i in range(count):
                    sprite = Sprite.provider.get_sprite(object_type, obj_name, None)
                    if object_type == 'enemies':
                        self.objects.append(Objects.Enemy(
                            sprite, prop, prop['experience'], self.get_coord(_map)))
                    else:
                        self.objects.append(Objects.Ally(
                            sprite, prop['action'], self.get_coord(_map)))


class EndMap(MapFactory):

    yaml_tag = "!end_map"

    class Map(AbstractMap):
        def __init__(self):
            super().__init__()
            self.Map = ['000000000000000000000000000000000000000',
                        '0                                     0',
                        '0                                     0',
                        '0  #   #   ###   #   #  #####  #   #  0',
                        '0  #  #   #   #  #   #  #      #   #  0',
                        '0  ###    #   #  #####  ####   #   #  0',
                        '0  #  #   #   #  #   #  #      #   #  0',
                        '0  #   #   ###   #   #  #####  #####  0',
                        '0                                   # 0',
                        '0                                     0',
                        '000000000000000000000000000000000000000'
                        ]
            self.Map = list(map(list, self.Map))
            for i in self.Map:
                for j in range(len(i)):
                    if i[j] == '0':
                        i[j] = const.BORDER
                    elif i[j] == '#':
                        i[j] = const.WALL
                    else:
                        i[j] = const.FLOOR + random.randint(0,2)
         
        def get_map(self):
            return self.Map

    class Objects(AbstractObjects):

        def __init__(self, config = {}):
            super().__init__(config)

        def get_objects(self, _map):
            return self.objects


class RandomMap(MapFactory):
    yaml_tag = "!random_map"

    class Map(AbstractMap):

        def __init__(self):
            super().__init__()

        def get_map(self):
            return self.Map

    class Objects(AbstractObjects):

        def get_objects(self, _map):
            self.add_objects()
            self.add_ally()
            self.add_enemies()
            self.make_objects(_map)
            return self.objects

#####################################################################################################
##
##
#####################################################################################################
class EmptyMap(MapFactory):

    yaml_tag = "!empty_map"

    class Map(AbstractMap):
        def __init__(self):
            super().__init__()

        def get_map(self):
            return self.Map

    class Objects(AbstractObjects):
        
        def __init__(self, config={}):
            super().__init__(config)

        def get_objects(self, _map):
            self.add_objects()
            self.add_ally({})
            self.add_enemies({})
            self.make_objects(_map)
            return self.objects


#####################################################################################################
##
##
#####################################################################################################
class SpecialMap(MapFactory):

    yaml_tag = "!special_map"

    class Map(AbstractMap):
        def __init__(self):
            #TODO load special map from yaml
            self.Map = ['0000000000000000000000000000000000000000',
                        '0                                      0',
                        '0                                      0',
                        '0  00000  00000  00000  0    0         0',
                        '0  0      0   0  0      0    0         0',
                        '0  0      0   0  00000  0    0         0',
                        '0  0      0   0  0      0    0         0',
                        '0  00000  0   0  00000   00000         0',
                        '0                              0       0'] + \
                       ['0                                      0'] * 30 + \
                       ['0000000000000000000000000000000000000000']
                        
            self.Map = list(map(list, self.Map))
            for i in self.Map:
                for j in range(len(i)):
                    i[j] = const.WALL if i[j] == '0' else const.FLOOR
            super().__init__()
         
        def get_map(self):
            return self.Map

    class Objects(AbstractObjects):

        def __init__(self, config = {}):
            super().__init__(config)

        def get_objects(self, _map):
            self.add_objects()
            self.add_ally({})
            # enemies already added from config loaded with yaml
            self.make_objects(_map)
            return self.objects

