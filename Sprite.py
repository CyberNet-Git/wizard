import os
import pygame
from Tilemap import Tilemap
import const


"""
Спрайты:
1. должны ЛИ? уметь себя рисовать на указанной поверхности
2. должны возвращать готовые ссылки с нужным разрешением (генерировать и кэшировать или брать подготовленные?)
3. текущее разрешение карты брать у GameEngine

"""
class Sprite:

    def __init__(self, *args, **kwargs):
        print('Sprite: ', args, kwargs)
        if len(args) == 0:
            filename = kwargs['filename'] if 'filename' in kwargs else None
        else:
            filename = args[0]
        if filename is not None and os.path.exists(filename):
            self._image = pygame.image.load(filename).convert_alpha()
        else:
            self._image = pygame.Surface((const.DEFAULT_SPRITE_SIZE, const.DEFAULT_SPRITE_SIZE))
        self.clear_cache()

    def clear_cache(self):
        self.size = self._image.get_size()
        self.cache={self.size:self._image}

    def get_sprite(self, width=None, height=None):
        if (width or height) is None:
            width, height = self._image.get_size()
        elif height is None:
            w,h = self._image.get_size()
            height = round(width * h / w)
        else:
            w,h = self._image.get_size()
            width = round(height * w / h)
        size = (width, height)
        if size not in self.cache:
            self.cache[size] = pygame.transform.scale(self._image, (width, height))
        return self.cache[size]
    
class SquareSprite(Sprite):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.size[0] != self.size[1]:
            # transform to make image square
            size = max(self.size)
            self._image = pygame.transform.scale(self._image, (size, size))
            self.clear_cache()

    def get_sprite(self, size=None):
        size = size or self._image.get_width()
        return super().get_sprite(size, size)

class SquareMultiSprite(Sprite):

    def __init__(self, size=const.DEFAULT_SPRITE_SIZE, *args, **kwargs):
        self.sprite_size = size
        self.active_sprite = (0,0)
        super().__init__(*args, **kwargs)
        self.cols = self.size[0] // size
        self.rows = self.size[1] // size

    def get_sprite(self, size=None):
        size = size or self.sprite_size
        cache_index = ((size,) + self.active_sprite)
        if cache_index not in self.cache:
            rect = (self.active_sprite[1] * self.sprite_size, self.active_sprite[0] * self.sprite_size, 
                    self.sprite_size, self.sprite_size)
            img = self._image.subsurface(rect)
            self.cache[cache_index] = pygame.transform.scale(img, (size, size))
        return self.cache[cache_index]

    def clear_cache(self):
        self.size = self._image.get_size()
        cache_index = ((self.sprite_size,) + self.active_sprite)
        rect = (0, 0, self.sprite_size, self.sprite_size) # top left sprite is always default active
        img = self._image.subsurface(rect)
        self.cache= {cache_index: img}

    def set_active_sprite(self, active_sprite=None):
        if active_sprite is None:
            active_sprite = (0,0)
        else:
            active_sprite = (min(active_sprite[0], self.rows), min(active_sprite[1], self.cols))
        self.active_sprite = active_sprite

class AnimatedSprite(SquareMultiSprite):
    ROUNDTRIP=0
    CIRCLE=1

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mode = self.ROUNDTRIP
        self.step = 1

    def next_frame(self):
        col = self.active_sprite[1] + self.step
        if col in (0, self.cols-1):
            if self.mode == self.ROUNDTRIP:
                self.step = -self.step
            else:
                col = 0
        self.set_active_sprite((self.active_sprite[0], col))

    def set_view(self, view=0):
        view = view % (self.rows-1)
        self.set_active_sprite((view, self.active_sprite[1]))

    def get_sprite(self, size=None):
        sprite = super().get_sprite(size)
        self.next_frame()
        return sprite
        


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
    from copy import deepcopy
    pygame.init()
    screen = pygame.display.set_mode((640, 640))
    floor = SquareMultiSprite(filename="texture\\map\\map.png")
    sprite = AnimatedSprite(filename="texture\\hero\\Soldier 02-1.png")
    chest = floor
    tiles = Tilemap(32, rows=10, cols=8)
    screen.fill((255, 255, 255))
    s = 64
    spr = sprite.get_sprite(s)
    sprite.set_active_sprite((2, 0))
    print(spr.get_size())
    import time
    t1 = time.monotonic()
    walk_circle = [0,1,2,1]
    for i in range(20):
        for r in range(4):
            for c in range(1):
                #sprite.set_active_sprite((1, walk_circle[i % 4]))
                floor.set_active_sprite((2,r+4))
                screen.blit(floor.get_sprite(s), (c*s, r*s))
                screen.blit(floor.get_sprite(s), ((c+1) * s, r*s))
                chest.set_active_sprite((6,r))
                screen.blit(chest.get_sprite(s), ((c+1) * s , r*s))
                sprite.set_view(r)
                screen.blit(sprite.get_sprite(s), (c*s, r*s))
        pygame.display.flip()
        time.sleep(1/5)
        sprite.next_frame()
        screen.fill((255, 255, 255))
    print ("{}".format(time.monotonic() - t1))

    #screen.blit(tiles.tilemaps[32]['img'], (0,0))
    while pygame.event.wait().type != pygame.locals.QUIT:
        pass