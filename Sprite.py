import os
import pygame
from Tilemap import Tilemap
import const


"""
Спрайты:
1. должны ЛИ? уметь себя рисовать на указанной поверхности
2. должны возвращать готовые ссылки с нужным разрешением (генерировать и кэшировать или храть подготовленные?)
3. текущее разрешение карты брать у GameEngine

"""
class SquareSprite:

    def __init__(self, filename=None):
        if filename is not None and os.path.exists(filename):
            self._image = pygame.image.load(filename).convert_alpha()
            assert self._image.get_width() == self._image.get_height()
            self.cache={self._image.get_width:self._image}

    def get_sprite(self, size):
        if size not in self.cache:
            self.cache[size] = pygame.transform.scale(self._image, (size, size))
        return self.cache[size]


class SpriteProvider:
    GRASS = 0
    WALL = 1
    FLOOR = 2
    BORDER = 3
    CHEST = 4
    STAIRS = 5

    def __init__(self, size=const.DEFAULT_SPRITE_SIZE):
        self.size = size
        #self.static = Tilemap(32, STATIC_TEXTURES) # Тут указываем реальный размер плитки в картинке (32)
        #self.hero = Tilemap(32, HERO_TILEMAP)
        self.ugly_images = True
        self.sprites = {
            True: {'hero':{}, 'map':{}, 'objects':{}, 'enemies':{}, 'ally':{}}, # tilemaps
            False:{'hero':{}, 'map':{}, 'objects':{}, 'enemies':{}, 'ally':{}} # old sprites
        }
    
    def load_ugly_sprites(self, objects):
        #FIXME загрузить тут убогие спрайты из шаблона проекта
        self.objects = objects
        rows = 10
        cols = 8
        for o in objects: cols = max(len(objects[o]), cols)
        
        _map = Tilemap(32, rows = rows, cols = cols)
        
        tile = _map.batch_load_tile_at(self.WALL, 0, os.path.join("texture","map", "wall.png"))
        [_map.batch_add_tile_at(self.WALL, i + 1, t) for i, t in enumerate([tile] * (cols - 1))]
        [_map.batch_add_tile_at(self.BORDER, i, t) for i, t in enumerate([tile] * cols)]
        g1 = _map.batch_load_tile_at(self.FLOOR, 0, os.path.join("texture","map", "Ground_1.png"))
        g2 = _map.batch_load_tile_at(self.FLOOR, 1, os.path.join("texture","map", "Ground_2.png"))
        g3 = _map.batch_load_tile_at(self.FLOOR, 2, os.path.join("texture","map", "Ground_3.png"))
        [_map.batch_add_tile_at(self.GRASS, i, t) for i, t in enumerate([g1, g2, g3] * 2 + [g1, g2] )]
        _map.update_tilemaps()
        #self.ugly['map'] = _map 

        def pack_sprites(obj_type):
            self.ugly[obj_type] = Tilemap(32, rows = 1, cols = max(5,len(objects[obj_type])))
            self.ugly_ids[obj_type] = {}
            objs = objects[obj_type]
            for i, name in enumerate(objs):
                print('pack', i, objs[name])
                self.ugly[obj_type].batch_load_tile_at(0, i, os.path.join("texture","map", obj_type, objs[name]['sprite'][0]))
                self.ugly_ids[obj_type][name] = i
            self.ugly[obj_type].update_tilemaps()
        
        # pack single sprites or list to tilemap 
        for obj_class in objects:
            pack_sprites(obj_class)

        self.ugly['hero'] = Tilemap(32, os.path.join("texture", "Hero.png"))

        pass
    
    def get_static(self, what, num, size):
        if self.ugly_images:
            return self.ugly['map'].get_sprite(what, num, size)
        else:
            return self.static.get_sprite(what, num, size)

    def get_grass(self, num):
        return self.static.get_sprite(SpriteProvider.GRASS, num, self.size)

    def get_hero(self, sprite_size):
        if self.ugly_images:
            return self.ugly['hero'].get_sprite(0, 0, sprite_size)
        else:
            return self.hero.get_sprite(2, 2, sprite_size)

    def get_object(self, obj_type, name, sprite_size):
        if self.ugly_images:
            print('get object: ', obj_type, name)
            return self.ugly[obj_type].get_sprite(0, self.ugly_ids[obj_type][name], sprite_size)
        else:
            #TODO возвращать красивых монстриков.
            return self.ugly[obj_type].get_sprite(0, self.ugly_ids[obj], sprite_size)
            pass
    
    def get_sprite(what, name, view, phase):
        return self.sprites[self.ugly][what][name][view][phase].get_sprite(self.size)


if __name__=='__main__':
    pygame.init()
    screen = pygame.display.set_mode((640, 640))
    sprite = SquareSprite("texture\\map\\wall.png")
    tiles = Tilemap(32, rows=10, cols=8)
    screen.fill((255, 255, 255))
    s = 64
    spr = sprite.get_sprite(s)
    import time
    t1 = time.monotonic()
    for i in range(10000):
        for r in range(10):
            for c in range(10):
                screen.blit(sprite.get_sprite(s), (c*s, r*s))
    print ("{}".format(time.monotonic() - t1))

    #screen.blit(tiles.tilemaps[32]['img'], (0,0))
    pygame.display.flip()
    while pygame.event.wait().type != pygame.locals.QUIT:
        pass