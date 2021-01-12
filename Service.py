import pygame
import random
import yaml
import os
from abc import ABC, abstractmethod

import Objects
from Tilemap import Tilemap


OBJECT_TEXTURE = os.path.join("texture", "objects")
ENEMY_TEXTURE = os.path.join("texture", "enemies")
ALLY_TEXTURE = os.path.join("texture", "ally")

DEFAULT_SPRITE_SIZE = 32
STATIC_TEXTURES = os.path.join("texture", "tilemap.png")
HERO_TILEMAP = os.path.join("texture", "Hero", "Soldier 06-1.png")




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
        pass

    def get_map(self):
        return self.Map

    def draw(self, game_surface):
        if self.Map:
            for i in range(game_surface.map_left, game_surface.map_left + game_surface.win_width ): # +1
                for j in range(game_surface.map_top, game_surface.map_top + game_surface.win_height ): # +1 removed
                    try:
                        sprite = sp.get_static(self.Map[j][i], self.num)
                        #sp.size = game_surface.engine.size
                        sprite = sp.get_static(2, 3)
                        game_surface.blit(sprite, game_surface.map_to_surface((i, j)) )
                    except:
                        pass
        else:
            self.fill(colors["white"])
    
    def can_move(self, x, y):
        return self.Map[x][y] not in (sp.WALL, sp.BORDER)


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
            if _map.Map[coord[1]][coord[0]] != sp.FLOOR:
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
        for obj_name in object_list_prob[object_type]:
            min_count = 0
            max_count = 5
            prop = object_list_prob[object_type][obj_name]
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
                prop = object_list_prob[object_type][obj_name]
                for i in range(count):
                    if object_type == 'enemies':
                        self.objects.append(Objects.Enemy(
                            prop['sprite'], prop, prop['experience'], self.get_coord(_map)))
                    else:
                        self.objects.append(Objects.Ally(
                            prop['sprite'], prop['action'], self.get_coord(_map)))


class EndMap(MapFactory):

    yaml_tag = "!end_map"

    class Map(AbstractMap):
        def __init__(self):
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
                        i[j] = SpriteProvider.BORDER
                    elif i[j] == '#':
                        i[j] = SpriteProvider.WALL
                    else:
                        i[j] = SpriteProvider.FLOOR
         
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
            self.Map = [[0 for _ in range(41)] for _ in range(41)]
            for i in range(41):
                for j in range(41):
                    if i == 0 or j == 0 or i == 40 or j == 40:
                        self.Map[j][i] = wall
                    else:
                        self.Map[j][i] = ([wall] + [floor1, floor2, floor3] * 3)[random.randint(0, 8)]

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
            self.num = random.randint(0,7)# sprite template number from SpriteProvider
            self.Map = [[0 for _ in range(41)] for _ in range(41)]
            for i in range(41):
                for j in range(41):
                    if i == 0 or j == 0 or i == 40 or j == 40:
                        self.Map[j][i] = SpriteProvider.BORDER
#                        self.Map[j][i] = sp.get_static(sp.BORDER,self.num)
                    else:
                        self.Map[j][i] = SpriteProvider.FLOOR
#                        self.Map[j][i] = self.Map[j][i] = sp.get_static(sp.FLOOR,self.num)
                        #([floor1, floor2, floor3] * 3)[random.randint(0, 8)]

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
                    i[j] = wall if i[j] == '0' else floor1
         
        def get_map(self):
            return self.Map

    class Objects(AbstractObjects):

        def __init__(self, config = {}):
            super().__init__(config)

        def get_objects(self, _map):
            self.add_objects()
            self.add_ally({})
            #self.add_enemies(_map, self.config['enemies'])
            # enemies already added from config loaded with yaml
            self.make_objects(_map)
            return self.objects

