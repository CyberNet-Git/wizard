import os
import pygame

import const

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

    def clear_cache(self):
        self.size = self._image.get_size()
        cache_index = ((self.sprite_size,) + self.active_sprite)
        rect = (0, 0, self.sprite_size, self.sprite_size) # top left sprite is always default active
        img = self._image.subsurface(rect)
        self.cache= {cache_index: img}

    def get_sprite(self, size=None):
        size = size or self.sprite_size
        cache_index = ((size,) + self.active_sprite)
        if cache_index not in self.cache:
            rect = (self.active_sprite[1] * self.sprite_size, self.active_sprite[0] * self.sprite_size, 
                    self.sprite_size, self.sprite_size)
            img = self._image.subsurface(rect)
            self.cache[cache_index] = pygame.transform.scale(img, (size, size))
        return self.cache[cache_index]

    def set_active_sprite(self, active_sprite=None):
        if active_sprite is None:
            active_sprite = (0,0)
        else:
            active_sprite = (min(active_sprite[0], self.rows), min(active_sprite[1], self.cols))
        self.active_sprite = active_sprite

class AnimatedSprite(SquareMultiSprite):
    ROUNDTRIP = 0
    CIRCLE = 1
    TIMER = 0
    MANUAL = 1

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mode = self.ROUNDTRIP
        self.animation = self.TIMER
        self.timer = time.monotonic()
        self.step = 1

    def get_sprite(self, size=None):
        sprite = super().get_sprite(size)
        if self.animation == self.MANUAL:
            self.next_frame()
        elif self.animation == self.TIMER \
                and time.monotonic() - self.timer > 1/5: # hardcoded 0.2 sec timeframe
            self.next_frame()
            self.timer = time.monotonic()
        return sprite

    def next_frame(self):
        col = self.active_sprite[1] + self.step
        if col in (0, self.cols-1):
            if self.mode == self.ROUNDTRIP:
                self.step = -self.step
            else:
                col = 0
        self.set_active_sprite((self.active_sprite[0], col))

    def set_view(self, view=0):
        view = view % (self.rows)
        self.set_active_sprite((view, self.active_sprite[1]))


class SpriteProvider:
    """
        Класс обеспечивает игру всеми необходимыми графическими примитивами (спрайтаими)
    все они умеют по запросу вернуть объект pygame.Surface() для отрисовки образа
    нужного объекта или ячейки карты.

        У меня тут в модуле определено несколько типов спрайтов:

        Sprite - обычный спрайт из графического файла с произвольными размерами 
    по ширине и высоте.

        SquareSprite - спрайт, у которого высота и ширина равны, т.е. квадратный. 
    Если картинка не квадратная, то меньшую сторону растянем при загрузке.

        SuareMultiSprite - это такой набор спрайтов в одной картинке в виде сетки 
    с заданным размером квадрата. Подразумевается, что файл корректный, 
    иначе изображения съедут.

        AnimatedSprite - такой особый вид спрайта, который умеет меняться во времени 
    или по запросу. Содержит набор кадров. По строкам - вид (например, 
    спереди, справа,...) По столбцам - раскадровка движения.

        Иерархию наследования можно увидеть из исходного кода выше.
    """
    GRASS = 0
    WALL = 1
    FLOOR = 2
    BORDER = 3
    CHEST = 4
    STAIRS = 5
    
    NEW = True
    OLD = False

    def __init__(self, size=const.DEFAULT_SPRITE_SIZE):
        self.size = size
        self.look = False
        self.sprites = {
            self.NEW: {'hero':{}, 'map':{}, 'objects':{}, 'enemies':{}, 'ally':{}}, # tilemaps
            self.OLD:{'hero':{}, 'map':{}, 'objects':{}, 'enemies':{}, 'ally':{}} # old sprites
        }
    
    def load_ugly_sprites(self, objects):
        #FIXME загрузить тут убогие спрайты из шаблона проекта чтобы только показать, что мы это могём
        # - не могём, а мОгем, -- (С) Маэстро. "В бой идут одни старики" :)
        self.objects = objects
        
        # Герой + Внешний вид (с мечом, копьем, эффектом) + направление взгляда
        # Карта + Тип (трава, стена, вода, пол) + внешний вид
        # Объекты + Имя объекта (сундук, лестница) + состояние (закрыт, открыт)
        # Враги + Имя объекта (он же внешний вид) + направление взгляда
        # Союзники + Имя объекта (он же внешний вид) + направление взгляда
        self.sprites[self.OLD]['hero'][None] = {None: Sprite(os.path.join("texture","hero", "Hero.png"))}
        self.sprites[self.OLD]['map']['wall'] = {None: Sprite(os.path.join("texture","map", "wall.png"))}
        self.sprites[self.OLD]['map']['floor'] = {}
        self.sprites[self.OLD]['map']['floor'][0] = Sprite(os.path.join("texture","map", "Ground_1.png"))
        self.sprites[self.OLD]['map']['floor'][1] = Sprite(os.path.join("texture","map", "Ground_2.png"))
        self.sprites[self.OLD]['map']['floor'][2] = Sprite(os.path.join("texture","map", "Ground_3.png"))

        # загрузить спрайты объектов из YAML
        for t in objects: # [objects, enemies, ally]
            for name in objects[t]:
                # t - тип (ally, enemies) + objects[t] - Имя + состояние - всегда неопределено
                filename = objects[t][name]['sprite'][0]
                self.sprites[self.OLD][t][name] = {None: Sprite(os.path.join("texture", t, filename ))}

    def load_beauty_sprites(self):
        # load Hero
        with open(os.path.join("texture","hero","hero.yaml"), "r") as file:
            sprites = yaml.load(file.read())
        for t in sprites: # [objects, enemies, ally]
            for name in sprites[t]:
                # t - тип (ally, enemies) + objects[t] - Имя + состояние - всегда неопределено
                filename = sprites[t][name]['sprite'][0]
                self.sprites[self.NEW][t][name] = {None: Sprite(os.path.join("texture", t, filename ))}

        # load Map
        # load Objects
        # load Ally
        # load Enemies
        pass

    def get_sprite(self, what, name, view):
        try:
            return self.sprites[self.look][what][name][view]
        except:
            #FIXME нужно вернуть любой подходящий спрайт
            return None


if __name__=='__main__':

    import time, yaml

    pygame.init()
    screen = pygame.display.set_mode((640, 640))
    screen.fill((255, 255, 255))

    def ugly(s, sp):
        r = 0
        for i, t in enumerate(sp.sprites[False]):
            c = 4
            for j, name in enumerate(sp.sprites[False][t]):
                for k, view in enumerate(sp.sprites[False][t][name]):
                    sprite = sp.get_sprite(t, name, view)
                    screen.blit(sprite.get_sprite(s), ((c+k)*s, r*s))
                c += 1
            r += 1

    def anim(s):
        #walk_circle = [0,1,2,1]
        for r in range(4):
            for c in range(1):
                #sprite.set_active_sprite((1, walk_circle[i % 4]))
                for f in range(floor.cols):
                    floor.set_active_sprite((const.FLOOR,f))
                    screen.blit(floor.get_sprite(s), ((c+f) * s, (r)*s))
                chest.set_active_sprite((5,r+4))
                screen.blit(chest.get_sprite(s), ((c+1) * s , r*s))
                sprite.set_view( r + view )
                screen.blit(sprite.get_sprite(s), (c*s, r*s))
        ugly(sprite_size, sp)
        pygame.display.flip()
        #sprite.next_frame()
        #screen.fill((255, 255, 255))

    with open("objects.yml", "r") as file:
        objects = yaml.load(file.read())

    sp = SpriteProvider()
    sp.load_ugly_sprites(objects)
    sprite_size = 64

    
    t1 = ltime = rtime = time.monotonic()
    ldown = rdown = False
    floor = SquareMultiSprite(filename="texture\\map\\map.png")
    sprite = AnimatedSprite(size=64, filename="texture\\hero\\hero-6.png")
    chest = floor
    sprite.set_active_sprite((2, 0))
    sprite.animation = AnimatedSprite.TIMER
    shift = 0
    view = 0
    while True:
        if pygame.event.peek(eventtype=[pygame.QUIT, pygame.KEYDOWN, pygame.KEYUP], pump=True):
            
            for event in pygame.event.get(eventtype=[pygame.QUIT, pygame.KEYDOWN, pygame.KEYUP]):
                if event.type == pygame.QUIT:
                    exit(0)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        ldown = True
                        shift += 1
                        view = [const.FRONT, const.LEFT, const.BACK, const.RIGHT][shift % 4]
                        ltime = time.monotonic()
                    if event.key == pygame.K_RIGHT:
                        rdown = True
                        shift -= 1
                        view = [const.FRONT, const.LEFT, const.BACK, const.RIGHT][shift % 4]
                        rtime = time.monotonic()

                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_ESCAPE:
                        exit(0)
                    if event.key == pygame.K_LEFT:
                        ldown = False
                    if event.key == pygame.K_RIGHT:
                        rdown = False
        t = time.monotonic()
        if  t - ltime > 1/5 and ldown: 
            ltime = t
            shift += 1
            view = [const.FRONT, const.LEFT, const.BACK, const.RIGHT][shift % 4]
        if  t - rtime > 1/5 and rdown: 
            rtime = t
            shift -= 1
            view = [const.FRONT, const.LEFT, const.BACK, const.RIGHT][shift % 4]

        anim(sprite_size)

    print ("{}".format(time.monotonic() - t1))

