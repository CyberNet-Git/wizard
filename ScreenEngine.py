import pygame
import collections
import math
import os

import Sprite
import const

colors = {
    "black": (215, 134, 0, 255),
    "white": (255, 255, 255, 255),
    "red": (160, 0, 0, 255),
    "green": (0, 100, 0, 255),
    "blue": (0, 0, 255, 255),
    "wooden": (65, 32, 2, 255),
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
        self.sprite_size = 32
        #self.fill(colors["white"])

    def connect_engine(self, engine):
        self.game_engine = engine
        super().connect_engine(engine)

    def map_to_surface(self, coords):
        """
        Converts game map coords to screen coords 
        """
        return ((coords[0] - self.map_left) * self.sprite_size, 
                (coords[1] - self.map_top) * self.sprite_size)

    def draw_background(self):
        """
        Draws the game surface background. Source - leftmost corner of map (border sprite)
        """
        sprite = Sprite.provider.get_sprite('map', self.game_engine.map.Map[0][0], self.game_engine.map.num)
        for i in range(0,self.win_width+1):
            for j in range(0,self.win_height+1):
               self.blit(sprite.get_sprite(), (i * self.sprite_size, j * self.sprite_size) )

    def draw_hero(self):
        # hero draws itself on top of game surface
        self.game_engine.hero.sprite.animation = Sprite.AnimatedSprite.TIMER
        self.game_engine.hero.draw(self)

    def draw_map(self):
        # map draws itself on top of game surface
        self.game_engine.map.draw(self)

    def draw_objects(self, sprite=None, coord=None):
        # Each object is being drawn by itself according to class hierarchy in Objects.py
        for obj in self.game_engine.objects:
            obj.draw(self)

    def draw(self, canvas):
        """
        Draw contents of game surface.
        """
        size = self.sprite_size
        hero_pos = self.game_engine.hero.position

        win_width = self.get_width() / size
        win_height = self.get_height() / size
        half_win_width = self.get_width() / size // 2
        half_win_height = self.get_height() / size // 2
        map_width = len(self.game_engine.map.Map[0])
        map_height = len(self.game_engine.map.Map)

        # calculate left and top offsets for visible part of the game map
        left = hero_pos[0] - half_win_width if hero_pos[0] >= half_win_width else 0
        top = hero_pos[1] - half_win_height if hero_pos[1] >= half_win_height else 0
        left = max(0,map_width - half_win_width*2) if hero_pos[0] > map_width - half_win_width else left
        top = max(0, map_height - half_win_height*2) if hero_pos[1] > map_height - half_win_height else top

        # win_width and win_height measured in game map cells
        self.map_left = int(round(left))
        self.map_top = int(round(top))
        self.win_width = int(round(win_width))
        self.win_height = int(round(win_height))

        # draw window contents
        self.draw_background()
        self.draw_map()
        self.draw_objects()
        self.draw_hero()

        super().draw(canvas)


class ProgressBar(ScreenHandle):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def connect_engine(self, engine):
        self.engine = engine
        super().connect_engine(engine)

    def draw(self, canvas):
        self.fill((0, 0, 0, 0))
        pygame.draw.rect(self, colors["black"], (55, 480+30, 200, 30), 2)
        pygame.draw.rect(self, colors["black"], (55, 480+70, 200, 30), 2)

        pygame.draw.rect(self, colors[
                         "red"], (58, 480+33, 195 * self.engine.hero.hp / self.engine.hero.max_hp, 25))
        pygame.draw.rect(self, colors["green"], (58, 480+73,
                                                 195 * self.engine.hero.exp / (100 * (2**(self.engine.hero.level - 1))), 25))

        font = pygame.font.SysFont("comicsansms", 20)
        self.blit(font.render(f'Hero at {self.engine.hero.position}', True, colors["black"]),
                  (160, 5))

        self.blit(font.render(f'SCORE {self.engine.score:.4f}', True, colors["black"]),
                  (400, 5))

        self.blit(font.render(f'{self.engine.level} floor', True, colors["black"]),
                  (60, 5))

        self.blit(font.render(f'HP', True, colors["black"]),
                  (20, 480+30))
        self.blit(font.render(f'Exp', True, colors["black"]),
                  (20, 480+70))

        self.blit(font.render(f'{self.engine.hero.hp}/{self.engine.hero.max_hp}', True, colors["black"]),
                  (70, 480 + 30))
        self.blit(font.render(f'{self.engine.hero.exp}/{(100*(2**(self.engine.hero.level-1)))}', True, colors["black"]),
                  (70, 480 + 70))

        self.blit(font.render(f'Str', True, colors["black"]),
                  (265, 480+30))
        self.blit(font.render(f'Endr', True, colors["black"]),
                  (265, 480+70))

        self.blit(font.render(f'{self.engine.hero.stats["strength"]}', True, colors["black"]),
                  (320, 480+30))
        self.blit(font.render(f'{self.engine.hero.stats["endurance"]}', True, colors["black"]),
                  (320, 480+70))

        self.blit(font.render(f'Int', True, colors["black"]),
                  (390, 480+30))
        self.blit(font.render(f'Luck', True, colors["black"]),
                  (390, 480+70))

        self.blit(font.render(f'{self.engine.hero.stats["intelligence"]}', True, colors["black"]),
                  (445, 480+30))
        self.blit(font.render(f'{self.engine.hero.stats["luck"]}', True, colors["black"]),
                  (445, 480+70))

        self.blit(font.render(f'Level', True, colors["black"]),
                  (500, 480+30))
        self.blit(font.render(f'Gold', True, colors["black"]),
                  (500, 480+70))

        self.blit(font.render(f'{self.engine.hero.level}', True, colors["black"]),
                  (570, 480+30))
        self.blit(font.render(f'{self.engine.hero.gold}', True, colors["black"]),
                  (570, 480+70))

        super().draw(canvas)


class InfoWindow(ScreenHandle):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.len = 23
        clear = []
        self.data = collections.deque(clear, maxlen=self.len)

    def update(self, value):
        self.data.append(f"> {str(value)}")

    def draw(self, canvas):
        self.fill((0, 0, 0, 0))
        size = self.get_size()

        font = pygame.font.SysFont("comicsansms", 10)
        for i, text in enumerate(self.data):
            self.blit(font.render(text, False, colors["black"]),
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


class DialogWindow(ScreenHandle):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.btn_hl = pygame.Surface((168,47), pygame.SRCALPHA)
        self.btn_hl.fill((60,40,20,255))
        self.font1 = pygame.font.SysFont("comicsansms", 18)
        self.font2 = pygame.font.SysFont("comicsansms", 24)
        self.text_color = (215, 134, 0)
        self.stat_color = (128, 128, 255)
        self.dtype = -1

    def connect_engine(self, engine):
        self.engine = engine
        super().connect_engine(engine)

    def draw(self, canvas):
        alpha = 255 if self.engine.interaction == self.dtype else 0
        self.fill((0, 0, 0, alpha))

        if self.engine.interaction == self.dtype:
            self.blit(self.decor.get_sprite(), (0, 0))
            self.draw_content()
            self.btn_highlight()

        super().draw(canvas)

    def draw_centered(self, surf, offx, offy):
        self.blit( surf, ((self.get_width() - surf.get_width())//2 + offx, offy))

    def btn_highlight(self):
        buttxy0 = [(78,262), (263,262)]
        self.blit(self.btn_hl,buttxy0[self.engine.active_button], special_flags=pygame.BLEND_RGB_ADD)

    def draw_text(self, text, font, offs_x, offs_y, color):
        for i,t in enumerate(text):
            image = font.render(t, True, color)
            self.draw_centered(image, offs_x, offs_y + font.size('M')[1] * i)
    
    def draw_content(self):
        pass



class BattleWindow(DialogWindow):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.decor = Sprite.Sprite(os.path.join("texture","dlg.png"))
        self.dtype = const.UI_BATTLE

    def draw_content(self):
        stats_off = 90
        text = ['HP', 'Strength', 'Endurance', 'Intellect', 'Luck' ]
        self.draw_text(text, self.font1, 0, 120, self.text_color)

        # Hero stats
        text = self.engine.hero.get_stats()
        self.draw_text(text, self.font1, -stats_off, 120, self.stat_color)

        # Interactee stats
        text = self.engine.interactee.get_stats()
        self.draw_text(text, self.font1, stats_off, 120, self.stat_color)

        # draw icons of Hero & Interactee
        self.engine.hero.heading = const.RIGHT
        self.engine.interactee.heading = const.LEFT 
        self.engine.interactee.sprite.animation = Sprite.AnimatedSprite.TIMER
        self.blit(self.engine.hero.sprite.get_sprite(74),(37, 107))
        self.blit(self.engine.interactee.sprite.get_sprite(74),(self.get_width() - 112, 107))
        self.engine.interactee.sprite.animation = Sprite.AnimatedSprite.MANUAL



class DealWindow(DialogWindow):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.decor = Sprite.Sprite(os.path.join("texture","deal.png"))
        self.dtype = const.UI_DEAL

    def draw_content(self):
        text = ['']
        i = 0
        for w in self.engine.interactee.descr.split():
            if len(text[i]) + len(w) < 30:
                text[i] = ' '.join([text[i], w])
            else:
                text.append(w)
                i += 1
        text.append( 'Buy it for' )
        self.draw_text(text, self.font1, 0, 90, self.text_color)
        self.draw_text(
            [str(self.engine.calc_price(self.engine.interactee.action)) + ' GP'],
            self.font2, 0, 90 + self.font1.size('M')[1]*len(text), self.text_color)

        # draw icons of Hero & Interactee
        self.engine.hero.heading = const.RIGHT
        self.engine.interactee.heading = const.LEFT
        self.engine.interactee.sprite.animation = Sprite.AnimatedSprite.TIMER
        self.blit(self.engine.hero.sprite.get_sprite(74),(37, 107))
        self.blit(self.engine.interactee.sprite.get_sprite(74),(self.get_width() - 112, 107))
        self.engine.interactee.sprite.animation = Sprite.AnimatedSprite.MANUAL


class DecorWindow(ScreenHandle):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.image = pygame.image.load(os.path.join("texture","bg.png")).convert_alpha()

    def connect_engine(self, engine):
        self.engine = engine
        super().connect_engine(engine)

    def draw(self, canvas):
        self.blit(self.image, (0,0))
        super().draw(canvas)


class MinimapWindow(GameSurface):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sprite_size = 8

    def draw_background(self):
        self.fill((0, 0, 0, 0))

