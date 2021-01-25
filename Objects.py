from abc import ABC, abstractmethod
import pygame
import random

import const


class Interactive(ABC):

    @abstractmethod
    def interact(self, engine, hero):
        pass


class AbstractObject(ABC):
    def __init__(self):
        self.sprite = None
        self.name = ''
        self.descr = ''

    def draw(self, game_surface):
        sprite = self.sprite.get_sprite(game_surface.sprite_size)
        game_surface.blit(sprite, game_surface.map_to_surface(self.position) )

class StaticObject(AbstractObject, Interactive):
    pass

class Ally(AbstractObject, Interactive):

    def __init__(self, icon, action, position):
        self.sprite = icon
        self.action = action
        self.position = position

    def interact(self, engine):
        self.action()


class Creature(AbstractObject):

    def __init__(self, icon, stats, position):
        self.sprite = icon
        self.stats = stats
        self.position = position
        self.calc_max_HP()
        self.hp = self.max_hp
        self._heading = const.FRONT

    @property
    def heading(self):
        return self._heading

    @heading.setter
    def heading(self, value):
        self._heading = value
        try:
            self.sprite.set_view(value)
        except:
            pass

    def calc_max_HP(self):
        self.max_hp = 5 + self.stats["endurance"] * 2

    def get_stats(self):
        return [
            str(self.hp),
            str(self.stats['strength']),
            str(self.stats['endurance']),
            str(self.stats['intelligence']),
            str(self.stats['luck'])
        ]


class Hero(Creature):
    BASE_STATS = {
        "strength": 20,
        "endurance": 20,
        "intelligence": 5,
        "luck": 5
    }

    def __init__(self, stats, icon):
        pos = [1, 1]
        self.level = 1
        self._exp = 0
        self.gold = 0
        super().__init__(icon, stats, pos)
    
    @property
    def exp(self):
        return self._exp

    @exp.setter
    def exp(self, value):
        self._exp = value
        self.level_up()

    def level_up(self):
        while self.exp >= 100 * (2 ** (self.level - 1)):
            #yield "level up!"
            self.level += 1
            self.stats["strength"] += 2
            self.stats["endurance"] += 2
            self.calc_max_HP()
            self.hp = self.max_hp



class Effect(Hero):

    def __init__(self, base):
        self.base = base
        self.stats = self.base.stats.copy()
        self.apply_effect()

    @property
    def position(self):
        return self.base.position

    @position.setter
    def position(self, value):
        self.base.position = value

    @property
    def level(self):
        return self.base.level

    @level.setter
    def level(self, value):
        self.base.level = value

    @property
    def gold(self):
        return self.base.gold

    @gold.setter
    def gold(self, value):
        self.base.gold = value

    @property
    def hp(self):
        return self.base.hp

    @hp.setter
    def hp(self, value):
        self.base.hp = value

    @property
    def max_hp(self):
        return self.base.max_hp

    @max_hp.setter
    def max_hp(self, value):
        self.base.max_hp = value

    @property
    def exp(self):
        return self.base.exp

    @exp.setter
    def exp(self, value):
        self.base.exp = value

    @property
    def sprite(self):
        return self.base.sprite

    @abstractmethod
    def apply_effect(self):
        pass


class Enemy(Interactive,Creature):
    def __init__(self, icon, stats, xp, position):
        super().__init__(icon, stats, position)
        self.xp = xp

    def interact(self,engine):
        # Урон врагу
        h = engine.hero.stats
        e = self.stats

        def calc_strike(a,b):
            d = a['strength'] / b['endurance']
            d = d if d < 1 else 1
            l = a['luck'] / b['luck']
            l = l if l < 1 else 1
            i = a['intelligence'] / b['intelligence']
            i = i if i < 1 else 1
            return a['strength'] * d * l * i


        # if d >= 0:
        #     u = d * engine.hero.stats['strength'] / max(engine.hero.stats['luck'], self.stats['luck']) \
        #           * engine.hero.stats['intelligence'] / max(engine.hero.stats['intelligence'], self.stats['intelligence'])
        #     # u = d * engine.hero.stats['luck'] / max(engine.hero.stats['luck'], self.stats['luck']) \
        #     #       * engine.hero.stats['intelligence'] / max(engine.hero.stats['intelligence'], self.stats['intelligence'])
        # else:
        #     u = abs(d) * engine.hero.stats['luck'] / max(engine.hero.stats['luck'], self.stats['luck']) \
        #           * engine.hero.stats['intelligence'] / max(engine.hero.stats['intelligence'], self.stats['intelligence']) \
        #           * engine.hero.stats['strength'] / self.stats['endurance']
        self.hp -= round(min(self.hp, calc_strike(h,e)))

        # Урон герою
        # d = (self.stats['endurance'] - engine.hero.stats['strength']) \
        #     / (engine.hero.stats['strength'] + self.stats['endurance'])
        # if d >= 0:
        #     u = d * self.stats['strength'] * self.stats['intelligence'] / max(engine.hero.stats['luck'], self.stats['luck'])
        #     # u = d * self.stats['luck'] / max(engine.hero.stats['luck'], self.stats['luck']) \
        #     #       * self.stats['intelligence'] / max(engine.hero.stats['intelligence'], self.stats['intelligence'])
        # else:
        #     u = abs(d) * self.stats['strength'] ** 2 * self.stats['luck'] / max(engine.hero.stats['luck'], self.stats['luck']) / engine.hero.stats['endurance']
        #     # u = abs(d) * self.stats['luck'] / max(engine.hero.stats['luck'], self.stats['luck']) \
        #     #       * self.stats['intelligence'] / max(engine.hero.stats['intelligence'], self.stats['intelligence']) \
        #     #       * self.stats['endurance'] / engine.hero.stats['strength']
        engine.hero.hp -= round(min(engine.hero.hp, calc_strike(e,h)))
#        engine.hero.level_up()

    def draw(self, game_surface):
        sign = lambda a: (a>0) - (a<0)
        h = game_surface.game_engine.hero.position
        s = self.position
        if abs(s[0] - h[0]) > abs(s[1] - h[1]):
            self.heading = [const.RIGHT, 0, const.LEFT][sign(s[0] - h[0]) + 1]
        else:
            self.heading = [const.FRONT, 0, const.BACK][sign(s[1] - h[1]) + 1]
        super().draw(game_surface)


class Berserk(Effect):
    def apply_effect(self):
        self.stats["strength"] *= 2
        self.stats["endurance"] += 2 * random.randint(0,self.stats["luck"])
        self.stats["intelligence"] -= 1


class Blessing(Effect):
    def apply_effect(self):
        self.stats["strength"] += round(self.stats["strength"] * random.random())
        self.stats["endurance"] += 2 * random.randint(0,self.stats["luck"])


class Weakness(Effect):
    def apply_effect(self):
        self.stats["strength"] -= round(self.stats["strength"] * random.random() / 2)
        self.stats["endurance"] -= round(self.stats["strength"] * random.random() / 2)

# Additional effects. Task #3
class GoInsane(Effect):
    def apply_effect(self):
        self.stats["intelligence"] -= round(self.stats["intelligence"] * random.random()/4)

class Academic(Effect):
    def apply_effect(self):
        self.stats["intelligence"] *= round(self.stats["intelligence"] \
            * (1 + random.random()/2 \
                 + random.random(0,self.stats["luck"])/self.stats["luck"]))
