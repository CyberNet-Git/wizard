import pygame
import collections
import math

colors = {
    "black": (0, 0, 0, 255),
    "white": (255, 255, 255, 255),
    "red": (255, 0, 0, 255),
    "green": (0, 255, 0, 255),
    "blue": (0, 0, 255, 255),
    "wooden": (153, 92, 0, 255),
}


class ScreenHandle(pygame.Surface):

    def __init__(self, *args, **kwargs):
        if len(args) > 1:
            self.successor = args[-1]
            self.next_coord = args[-2]
            args = args[:-2]
        else:
            self.successor = None
            self.next_coord = (0, 0)
        super().__init__(*args, **kwargs)
        self.fill(colors["wooden"])

    def draw(self, canvas):
        if self.successor is not None:
            canvas.blit(self.successor, self.next_coord)
            self.successor.draw(canvas)

    def connect_engine(self,engine):
        if self.successor is not None:
            self.successor.connect_engine(engine)


class GameSurface(ScreenHandle):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.map_left = 0
        self.map_top = 0

    def connect_engine(self, engine):
        self.game_engine = engine
        super().connect_engine(engine)

    def map_to_surface(self, coords):
        return ((coords[0] - self.map_left) * self.game_engine.sprite_size, 
                (coords[1] - self.map_top) * self.game_engine.sprite_size)

    def draw_background(self):
        #sprite = Service.sp.get_static(self.Map[0][0], self.Map.num)
        #for i in range(0,self.win_width+1):
        #    for j in range(0,self.win_height+1):
        #       self.blit(sprite, (i * self.game_engine.sprite_size, j * self.game_engine.sprite_size) )
        pass

    def draw_hero(self):
        self.game_engine.hero.draw(self)

    def draw_map(self):
        if self.game_engine.map:
            for i in range(self.map_left, self.map_left + self.win_width + 1):
                for j in range(self.map_top, self.map_top + self.win_height + 1):
                    try:
                        self.blit(self.game_engine.map[j][i][0], self.map_to_surface((i, j)) )
                    except:
                        #sprite = sp.get self.game_engine.map.Map[j][i]
                        self.blit(self.game_engine.map.Map[j][i], self.map_to_surface((i, j)) )
        else:
            self.fill(colors["white"])

    def draw_objects(self, sprite=None, coord=None):
        # Each object is being drawn by itself according to class hierarchy in Objects.py
        for obj in self.game_engine.objects:
            obj.draw(self)

    def draw(self, canvas):
        size = self.game_engine.sprite_size
        hero_pos = self.game_engine.hero.position

        win_width = self.get_width() / size
        win_height = self.get_height() / size
        half_win_width = self.get_width() / size // 2
        half_win_height = self.get_height() / size // 2
        map_width = len(self.game_engine.map.Map[0])
        map_height = len(self.game_engine.map.Map)

        left = hero_pos[0] - half_win_width if hero_pos[0] >= half_win_width else 0
        top = hero_pos[1] - half_win_height if hero_pos[1] >= half_win_height else 0
        left = map_width - half_win_width*2 if hero_pos[0] > map_width - half_win_width else left
        top = map_height - half_win_height*2 if hero_pos[1] > map_height - half_win_height else top
        self.map_left = int(round(left))
        self.map_top = int(round(top))
        self.win_width = int(round(win_width))
        self.win_height = int(round(win_height))

#        self.draw_map()
#        self.draw_background()
        self.game_engine.map.draw(self)
        self.draw_objects()
        self.draw_hero()
        super().draw(canvas)


class ProgressBar(ScreenHandle):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fill(colors["wooden"])

    def connect_engine(self, engine):
        self.engine = engine
        super().connect_engine(engine)

    def draw(self, canvas):
        self.fill(colors["wooden"])
        pygame.draw.rect(self, colors["black"], (50, 30, 200, 30), 2)
        pygame.draw.rect(self, colors["black"], (50, 70, 200, 30), 2)

        pygame.draw.rect(self, colors[
                         "red"], (50, 30, 200 * self.engine.hero.hp / self.engine.hero.max_hp, 30))
        pygame.draw.rect(self, colors["green"], (50, 70,
                                                 200 * self.engine.hero.exp / (100 * (2**(self.engine.hero.level - 1))), 30))

        font = pygame.font.SysFont("comicsansms", 20)
        self.blit(font.render(f'Hero at {self.engine.hero.position}', True, colors["black"]),
                  (250, 0))

        self.blit(font.render(f'{self.engine.level} floor', True, colors["black"]),
                  (10, 0))

        self.blit(font.render(f'HP', True, colors["black"]),
                  (10, 30))
        self.blit(font.render(f'Exp', True, colors["black"]),
                  (10, 70))

        self.blit(font.render(f'{self.engine.hero.hp}/{self.engine.hero.max_hp}', True, colors["black"]),
                  (60, 30))
        self.blit(font.render(f'{self.engine.hero.exp}/{(100*(2**(self.engine.hero.level-1)))}', True, colors["black"]),
                  (60, 70))

        self.blit(font.render(f'Level', True, colors["black"]),
                  (300, 30))
        self.blit(font.render(f'Gold', True, colors["black"]),
                  (300, 70))

        self.blit(font.render(f'{self.engine.hero.level}', True, colors["black"]),
                  (360, 30))
        self.blit(font.render(f'{self.engine.hero.gold}', True, colors["black"]),
                  (360, 70))

        self.blit(font.render(f'Str', True, colors["black"]),
                  (420, 30))
        self.blit(font.render(f'Luck', True, colors["black"]),
                  (420, 70))

        self.blit(font.render(f'{self.engine.hero.stats["strength"]}', True, colors["black"]),
                  (480, 30))
        self.blit(font.render(f'{self.engine.hero.stats["luck"]}', True, colors["black"]),
                  (480, 70))

        self.blit(font.render(f'SCORE', True, colors["black"]),
                  (550, 30))
        self.blit(font.render(f'{self.engine.score:.4f}', True, colors["black"]),
                  (550, 70))
        super().draw(canvas)


class InfoWindow(ScreenHandle):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.len = 30
        clear = []
        self.data = collections.deque(clear, maxlen=self.len)

    def update(self, value):
        self.data.append(f"> {str(value)}")

    def draw(self, canvas):
        self.fill(colors["wooden"])
        size = self.get_size()

        font = pygame.font.SysFont("comicsansms", 10)
        for i, text in enumerate(self.data):
            self.blit(font.render(text, True, colors["black"]),
                      (5, 20 + 18 * i))

        super().draw(canvas)


    def connect_engine(self, engine):
        self.engine = engine
        self.engine.subscribe(self)
        super().connect_engine(engine)


class HelpWindow(ScreenHandle):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.len = 30
        clear = []
        self.data = collections.deque(clear, maxlen=self.len)
        self.data.append([" →", "Move Right"])
        self.data.append([" ←", "Move Left"])
        self.data.append([" ↑ ", "Move Top"])
        self.data.append([" ↓ ", "Move Bottom"])
        self.data.append([" H ", "Show Help"])
        self.data.append(["Num+", "Zoom +"])
        self.data.append(["Num-", "Zoom -"])
        self.data.append([" R ", "Restart Game"])
    # FIXME You can add some help information

    def connect_engine(self, engine):
        self.engine = engine
        super().connect_engine(engine)

    def draw(self, canvas):
        alpha = 0
        if self.engine.show_help:
            alpha = 128
        self.fill((0, 0, 0, alpha))
        size = self.get_size()
        font1 = pygame.font.SysFont("courier", 24)
        font2 = pygame.font.SysFont("serif", 24)
        if self.engine.show_help:
            pygame.draw.lines(self, (255, 0, 0, 255), True, [
                              (0, 0), (700, 0), (700, 500), (0, 500)], 5)
            for i, text in enumerate(self.data):
                self.blit(font1.render(text[0], True, ((128, 128, 255))),
                          (50, 50 + 30 * i))
                self.blit(font2.render(text[1], True, ((128, 128, 255))),
                          (150, 50 + 30 * i))
        super().draw(canvas)
