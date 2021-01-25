import yaml
import pygame
import random

import const
import Service
import Objects
import Sprite
import ScreenEngine as SE


class GameEngine:
    objects = []
    map = None
    hero = None
    level = -1
    working = True
    subscribers = set()
    score = 0.
    game_process = True
    show_help = False
    show_battle = False

    def __init__(self, sprite_size):
        self.sprite_size = sprite_size

        with open("objects.yml", "r") as file:
            Service.object_list = yaml.load(file.read())

        Sprite.provider = Sprite.SpriteProvider()

        #FIXME возможно лучше создание объектов вынести в отдельный метод
        Sprite.provider.load_ugly_sprites(Service.object_list)
        Sprite.provider.load_beauty_sprites()

        self.hero = Objects.Hero(Objects.Hero.BASE_STATS, Sprite.provider.get_sprite('hero', 'level1', const.FRONT))
        self.hero.level = 1
        
        object_list_actions = {
            'reload_game': self.reload_game,
            'add_gold': self.add_gold,
            'apply_blessing': self.apply_blessing,
            'remove_effect': self.remove_effect,
            'restore_hp': self.restore_hp,
            'academic': self.teach_academic
        }

        object_list_descriptions = {
            'reload_game': 'Exits to next level',
            'add_gold': 'Chest of gold. May be you have to be reacher or cured',
            'apply_blessing': 'Blessing adds you some strength and endurance. Be careful, you can become a berserk!',
            'remove_effect': 'Remove last applied effect.',
            'restore_hp': 'Restores hero hit points (HP).',
            'academic': 'Graduate to academic. Increses intelligence.'
        }

        self.static = Service.object_list['objects']
        for name in self.static:
            obj = self.static[name]
            obj['descr'] = object_list_descriptions[obj['action']]
            obj['action'] = object_list_actions[obj['action']]
            obj['name'] = name

        self.ally = Service.object_list['ally']
        for name in self.ally:
            obj = self.ally[name]
            obj['descr'] = object_list_descriptions[obj['action']]
            obj['action'] = object_list_actions[obj['action']]
            obj['name'] = name

        self.enemies = Service.object_list['enemies']
        for name in self.enemies:
            obj = self.enemies[name]
            obj['name'] = name
            obj['descr'] = name

        # Load and create levels from YAML 
        with open("levels.yml", "r") as file:
            self.level_list = yaml.load(file.read())['levels']
            self.level_list.append({'map': Service.EndMap.Map(), 'obj': Service.EndMap.Objects()})

        self.drawer = \
                        SE.GameSurface((640, 480), pygame.SRCALPHA, (650, 500),
                            SE.MinimapWindow((136, 96), pygame.SRCALPHA, (0, 0),
                                SE.DecorWindow((800, 600), pygame.SRCALPHA, (0, 0),
                                    SE.ProgressBar((640, 600), pygame.SRCALPHA, (660, 30),
                                        SE.InfoWindow((140, 440), pygame.SRCALPHA, (0, 0),
                                            SE.HelpWindow((800, 600), pygame.SRCALPHA, (80, 100),
                                                SE.BattleWindow((511, 358), pygame.SRCALPHA, (80, 100),
                                                    SE.DealWindow((511, 358), pygame.SRCALPHA, (0, 0),
                                                        SE.ScreenHandle(
                                                            (0, 0))
                        ))))))))
        self.drawer.connect_engine(self)
        self.reload_game()

    def set_sprite_size(self, sprite_size):
        self.sprite_size = sprite_size
        self.drawer.sprite_size = sprite_size
        self.notify(f'Sprite size set to {sprite_size}')


    def reload_game(self):
        level_list_max = len(self.level_list) - 1
        self.level += 1
        self.show_battle = False
        self.user_choice = const.NO_CHOICE
        self.interaction = const.UI_NONE

        generator = self.level_list[min(self.level, level_list_max)]
        _map = generator['map']
        self.load_map(_map)

        self.objects = []
        self.add_objects(generator['obj'].get_objects(_map))
        self.hero.position = list(generator['obj'].get_coord(_map))
        try:
            self.hero.sprite.set_view(const.FRONT)
        except:
            # plain sprites have not this method
            pass
        self.notify(f'Level {self.level} started')

    # OBSERVER methods
    def subscribe(self, obj):
        self.subscribers.add(obj)

    def unsubscribe(self, obj):
        if obj in self.subscribers:
            self.subscribers.remove(obj)

    def notify(self, message):
        for i in self.subscribers:
            i.update(message)

    # HERO
    def interact(self):
        for obj in self.objects:
            if list(obj.position) == self.hero.position:
                self.interactee = obj

                if isinstance(obj, Objects.Enemy):
                    if self.interaction == const.UI_BATTLE:
                        if self.user_choice == const.NO_CHOICE:
                            return
                        elif self.user_choice == const.ATTACK:
                            obj.interact(self)
                            if obj.hp <= 0:
                                self.hero.exp += obj.xp
                                self.score += obj.xp // 10
                                self.interactee = None
                                self.delete_object(obj)
                                self.interaction = const.UI_NONE
                                self.user_choice = const.NO_CHOICE
                            if self.hero.hp <= 0:
                                self.hero.hp = 1
                                self.hero.position = self.last_position.copy()
                                self.interactee = None
                                self.interaction = const.UI_NONE
                                self.user_choice = const.NO_CHOICE
                        elif self.user_choice == const.LEAVE:
                            self.hero.position = self.last_position.copy()
                            self.interaction = const.UI_NONE
                            self.user_choice = const.NO_CHOICE
                    else:
                        self.interaction = const.UI_BATTLE
                        self.active_button = const.ATTACK

                if isinstance(obj, Objects.Ally) and obj.action not in (self.reload_game, self.add_gold):
                    if self.interaction == const.UI_DEAL:
                        if self.user_choice == const.NO_CHOICE:
                            return
                        elif self.user_choice == const.DEAL:
                            obj.interact(self)
                            self.interactee = None
                            self.delete_object(obj)
                            self.score += 100
                        elif self.user_choice == const.LEAVE:
                            self.hero.position = self.last_position.copy()
                            #self.hero.stats['endurance'] -= 1
                        self.interaction = const.UI_NONE
                        self.user_choice = const.NO_CHOICE
                    else:
                        self.interaction = const.UI_DEAL
                        self.active_button = const.DEAL
                elif isinstance(obj, Objects.Ally) and obj.action in (self.reload_game, self.add_gold):
                    obj.interact(self)
                    self.delete_object(obj)

    def break_wall(self, direction):
        x = self.hero.position[0] + direction[0]
        y = self.hero.position[1] + direction[1]
        if self.map.Map[y][x] - self.map.Map[y][x] % 10 == const.WALL:
            self.map.Map[y][x] = self.map.Map[self.hero.position[1]][self.hero.position[0]]

        # if self.interaction == const.UI_WALL:
        #     if self.user_choice == const.NO_CHOICE:
        #         return
        #     elif self.user_choice == const.ATTACK:
        #         obj.interact(self)
        #         if obj.hp <= 0:
        #             self.hero.exp += obj.xp
        #             self.score += obj.xp // 10
        #             self.interactee = None
        #             self.delete_object(obj)
        #             self.interaction = const.UI_NONE
        #             self.user_choice = const.NO_CHOICE
        #         if self.hero.hp <= 0:
        #             self.hero.hp = 1
        #             self.hero.position = self.last_position.copy()
        #             self.interactee = None
        #             self.interaction = const.UI_NONE
        #             self.user_choice = const.NO_CHOICE
        #     elif self.user_choice == const.LEAVE:
        #         self.hero.position = self.last_position.copy()
        #         self.interaction = const.UI_NONE
        #         self.user_choice = const.NO_CHOICE
        # else:
        #     self.interaction = const.UI_WALL
        #     self.active_button = const.BREACH



    # MOVEMENT
    def move_up(self):
        self.score -= 0.02
        if not self.map.can_move(self.hero.position[1] - 1, self.hero.position[0]):
            return False
        self.last_position = self.hero.position.copy()
        self.hero.position[1] -= 1
        self.hero.heading = const.BACK
        self.interact()
        return True

    def move_down(self):
        self.score -= 0.02
        if not self.map.can_move(self.hero.position[1] + 1,self.hero.position[0]):
            return False
        self.last_position = self.hero.position.copy()
        self.hero.position[1] += 1
        self.hero.heading = const.FRONT
        self.interact()
        return True

    def move_left(self):
        self.score -= 0.02
        if not self.map.can_move(self.hero.position[1], self.hero.position[0] - 1):
            return False
        self.last_position = self.hero.position.copy()
        self.hero.position[0] -= 1
        self.hero.heading = const.LEFT
        self.interact()
        return True
        
    def move_right(self):
        self.score -= 0.02
        if not self.map.can_move(self.hero.position[1], self.hero.position[0] + 1):
            return False
        self.last_position = self.hero.position.copy()
        self.hero.position[0] += 1
        self.hero.heading = const.RIGHT
        self.interact()
        return True

    # MAP
    def load_map(self, game_map):
        self.map = game_map

    # OBJECTS
    def add_object(self, obj):
        self.objects.append(obj)

    def add_objects(self, objects):
        self.objects.extend(objects)

    def delete_object(self, obj):
        try:
            self.objects.remove(obj)
        except:
            pass

    # ACTIONS
    def add_gold(self):
        if random.randint(1, 10) == 1:
            self.score -= 0.05
            self.hero = [Objects.Weakness, Objects.GoInsane][random.randint(0,1)](self.hero)
            self.notify("You were cursed")
        else:
            self.score += 1
            gold = int(random.randint(10, 1000) * (1.1**(self.hero.level - 1)))
            self.hero.gold += gold
            self.notify(f"{gold} gold added")

    def calc_price(self, action):
        if action == self.apply_blessing:
            return int(20 * 1.5**self.level) - 2 * self.hero.stats["intelligence"]
        if action == self.remove_effect:
            return int(10 * 1.5**self.level) - 2 * self.hero.stats["intelligence"]
        return 0
        

    def apply_blessing(self):
        #TODO implement it
        if self.hero.gold >= self.calc_price(self.apply_blessing):
            self.score += 20
            self.hero.gold -= self.calc_price(self.apply_blessing)
            if random.randint(0, 1) == 0:
                self.hero = Objects.Blessing(self.hero)
                self.notify("Blessing applied")
            else:
                self.hero = Objects.Berserk(self.hero)
                self.notify("Berserk applied")
        else:
            self.notify('Not enougth gold')
            self.score -= 0.1
    
    def remove_effect(self):
        #TODO implement it
        if self.hero.gold >= self.calc_price(self.remove_effect) and "base" in dir(self.hero):
            self.hero.gold -= self.calc_price(self.remove_effect)
            self.hero = self.hero.base
            self.hero.calc_max_HP()
            self.notify("Effect removed")
            self.score += 10
        else:
            self.notify('Not enougth gold')
            self.score -= 0.5
    
    def restore_hp(self):
        self.score += 50
        self.hero.hp = self.hero.max_hp
        self.notify("HP restored")

    def teach_academic(self):
        #TODO implement it
        if self.hero.gold >= self.calc_price(self.teach_academic) and "base" in dir(self.hero):
            self.hero.gold -= self.calc_price(self.teach_academic)
            self.hero = Objects.Academic(self.hero)
            self.notify("Academic graduated!")
            self.score += 10
        else:
            self.notify('Not enougth gold')
            self.score -= 0.5
