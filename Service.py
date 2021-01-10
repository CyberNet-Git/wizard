import pygame
import random
import yaml
import os
import Objects
from abc import ABC, abstractmethod
from Tilemap import Tilemap

OBJECT_TEXTURE = os.path.join("texture", "objects")
ENEMY_TEXTURE = os.path.join("texture", "enemies")
ALLY_TEXTURE = os.path.join("texture", "ally")

DEFAULT_SPRITE_SIZE = 32
STATIC_TEXTURES = os.path.join("texture", "tilemap.png")

def create_sprite(img, sprite_size):
    icon = pygame.image.load(img).convert_alpha()
    icon = pygame.transform.scale(icon, (sprite_size, sprite_size))
    sprite = pygame.Surface((sprite_size, sprite_size), pygame.HWSURFACE)
    sprite.blit(icon, (0, 0))
    return sprite

def reload_game(engine, hero):
    global level_list
    level_list_max = len(level_list) - 1
    engine.level += 1
    hero.position = [1, 1]
    engine.objects = []
    generator = level_list[min(engine.level, level_list_max)]
    _map = generator['map'] #.get_map()
    engine.load_map(_map)
    engine.add_objects(generator['obj'].get_objects(_map))
    engine.add_hero(hero)


def restore_hp(engine, hero):
    engine.score += 0.1
    hero.hp = hero.max_hp
    engine.notify("HP restored")


def apply_blessing(engine, hero):
    if hero.gold >= int(20 * 1.5**engine.level) - 2 * hero.stats["intelligence"]:
        engine.score += 0.2
        hero.gold -= int(20 * 1.5**engine.level) - \
            2 * hero.stats["intelligence"]
        if random.randint(0, 1) == 0:
            engine.hero = Objects.Blessing(hero)
            engine.notify("Blessing applied")
        else:
            engine.hero = Objects.Berserk(hero)
            engine.notify("Berserk applied")
    else:
        engine.score -= 0.1


def remove_effect(engine, hero):
    if hero.gold >= int(10 * 1.5**engine.level) - 2 * hero.stats["intelligence"] and "base" in dir(hero):
        hero.gold -= int(10 * 1.5**engine.level) - \
            2 * hero.stats["intelligence"]
        engine.hero = hero.base
        engine.hero.calc_max_HP()
        engine.notify("Effect removed")


def add_gold(engine, hero):
    if random.randint(1, 10) == 1:
        engine.score -= 0.05
        engine.hero = Objects.Weakness(hero)
        engine.notify("You were cursed")
    else:
        engine.score += 0.1
        gold = int(random.randint(10, 1000) * (1.1**(engine.hero.level - 1)))
        hero.gold += gold
        engine.notify(f"{gold} gold added")


class SpriteProvider:
    GRASS = 0
    WALL = 1
    FLOOR = 2
    BORDER = 3
    CHEST = 4
    STAIRS = 5
    def __init__(self, size=DEFAULT_SPRITE_SIZE):
        self.size = size
        self.static = Tilemap(STATIC_TEXTURES, size)
    
    def get_static(self, what, num):
        return self.static.get_sprite(what, num, self.size)

    def get_grass(self, num):
        return self.static.get_sprite(SpriteProvider.GRASS, num, self.size)


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
                    i[j] = wall if i[j] == '0' else floor1
         
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


class EmptyMap(MapFactory):

    yaml_tag = "!empty_map"

    class Map(AbstractMap):
        def __init__(self):
            self.num = random.randint(0,7)# sprite template number from SpriteProvider
            self.Map = [[0 for _ in range(41)] for _ in range(41)]
            for i in range(41):
                for j in range(41):
                    if i == 0 or j == 0 or i == 40 or j == 40:
                        self.Map[j][i] = sp.BORDER
#                        self.Map[j][i] = sp.get_static(sp.BORDER,self.num)
                    else:
                        self.Map[j][i] = sp.FLOOR
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


wall = [0]
floor1 = [0]
floor2 = [0]
floor3 = [0]

#class Service:
##    sp = None
#
#    def __init__(self, sprite_size):
#        full = True
#        Service.sp = SpriteProvider()
#        file = open("levels.yml", "r")
#        level_list = yaml.load(file.read())['levels']
#        level_list.append({'map': EndMap.Map(), 'obj': EndMap.Objects()})
#        file.close()

def service_init(sprite_size, full=True):
    global object_list_prob, level_list, sp

    global wall
    global floor1
    global floor2
    global floor3

    wall[0] = create_sprite(os.path.join("texture", "wall.png"), sprite_size)
    floor1[0] = create_sprite(os.path.join("texture", "Ground_1.png"), sprite_size)
    floor2[0] = create_sprite(os.path.join("texture", "Ground_2.png"), sprite_size)
    floor3[0] = create_sprite(os.path.join("texture", "Ground_3.png"), sprite_size)

    if full:
        sp = SpriteProvider(sprite_size)
    else:
        sp.size = sprite_size

    file = open("objects.yml", "r")

    object_list_tmp = yaml.load(file.read())
    if full:
        object_list_prob = object_list_tmp

    object_list_actions = {'reload_game': reload_game,
                           'add_gold': add_gold,
                           'apply_blessing': apply_blessing,
                           'remove_effect': remove_effect,
                           'restore_hp': restore_hp}

    for obj in object_list_prob['objects']:
        prop = object_list_prob['objects'][obj]
        prop_tmp = object_list_tmp['objects'][obj]
        prop['sprite'][0] = create_sprite(
            os.path.join(OBJECT_TEXTURE, prop_tmp['sprite'][0]), sprite_size)
        prop['action'] = object_list_actions[prop_tmp['action']]

    for ally in object_list_prob['ally']:
        prop = object_list_prob['ally'][ally]
        prop_tmp = object_list_tmp['ally'][ally]
        prop['sprite'][0] = create_sprite(
            os.path.join(ALLY_TEXTURE, prop_tmp['sprite'][0]), sprite_size)
        prop['action'] = object_list_actions[prop_tmp['action']]

    for enemy in object_list_prob['enemies']:
        prop = object_list_prob['enemies'][enemy]
        prop_tmp = object_list_tmp['enemies'][enemy]
        prop['sprite'][0] = create_sprite(
            os.path.join(ENEMY_TEXTURE, prop_tmp['sprite'][0]), sprite_size)

    file.close()

    if full:
        file = open("levels.yml", "r")
        level_list = yaml.load(file.read())['levels']
        level_list.append({'map': EndMap.Map(), 'obj': EndMap.Objects()})
        file.close()
