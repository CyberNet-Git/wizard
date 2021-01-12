import yaml

import Service
import Objects
import Sprite


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

    def __init__(self, sprite_size):
        self.sprite_size = sprite_size

        with open("objects.yml", "r") as file:
            object_list = yaml.load(file.read())

        self.sp = Sprite.SpriteProvider()

        #FIXME возможно лучше создание объектов вынести в отдельный метод
        self.sp.load_ugly_sprites(object_list)

        self.hero = Objects.Hero(Objects.Hero.BASE_STATS, self.sp.get_hero(sprite_size))
        self.hero.level = 1
        
        object_list_actions = {
            'reload_game': self.reload_game,
            'add_gold': self.add_gold,
            'apply_blessing': self.apply_blessing,
            'remove_effect': self.remove_effect,
            'restore_hp': self.restore_hp
        }

        self.static = object_list['objects']
        for name in self.static:
            obj = self.static[name]
            obj['action'] = object_list_actions[obj['action']]

        self.ally = object_list['ally']
        for name in self.ally:
            obj = self.ally[name]
            obj['action'] = object_list_actions[obj['action']]

        self.enemies = object_list['enemies']
        for name in self.enemies:
            obj = self.enemies[name]
            #obj['action'] = object_list_actions[obj['action']]

        # Load and create levels from YAML 
        file = open("levels.yml", "r")
        self.level_list = yaml.load(file.read())['levels']
        self.level_list.append({'map': Service.EndMap.Map(), 'obj': Service.EndMap.Objects()})
        file.close()


        self.reload_game()
        self.drawer = SE.GameSurface((640, 480), pygame.SRCALPHA, (0, 480),
                                SE.ProgressBar((640, 120), (640, 0),
                                                SE.InfoWindow((160, 480), (50, 50),
                                                                SE.HelpWindow((700, 500), pygame.SRCALPHA, (0, 0),
                                                                            SE.ScreenHandle(
                                                                                (0, 0))
                                                                            ))))
    def set_sprite_size(self, sprite_size):
        self.sprite_size = sprite_size


    def reload_game(self):
        level_list_max = len(self.level_list) - 1
        self.level += 1
        self.hero.position = [1, 1]

        generator = self.level_list[min(self.level, level_list_max)]
        _map = generator['map'] #.get_map()
        self.load_map(_map)

        self.objects = []
        self.add_objects(generator['obj'].get_objects(_map))

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
    def add_hero(self, hero):
        self.hero = hero

    def interact(self):
        for obj in self.objects:
            if list(obj.position) == self.hero.position:
                self.delete_object(obj)
                obj.interact(self, self.hero)

    # MOVEMENT
    def move_up(self):
        self.score -= 0.02
        if not self.map.can_move(self.hero.position[1] - 1, self.hero.position[0]):
            return
        self.hero.position[1] -= 1
        self.interact()

    def move_down(self):
        self.score -= 0.02
        if not self.map.can_move(self.hero.position[1] + 1,self.hero.position[0]):
            return
        self.hero.position[1] += 1
        self.interact()

    def move_left(self):
        self.score -= 0.02
        if not self.map.can_move(self.hero.position[1], self.hero.position[0] - 1):
            return
        self.hero.position[0] -= 1
        self.interact()

    def move_right(self):
        self.score -= 0.02
        if not self.map.can_move(self.hero.position[1], self.hero.position[0] + 1):
            return
        self.hero.position[0] += 1
        self.interact()

    # MAP
    def load_map(self, game_map):
        self.map = game_map

    # OBJECTS
    def add_object(self, obj):
        self.objects.append(obj)

    def add_objects(self, objects):
        self.objects.extend(objects)

    def delete_object(self, obj):
        self.objects.remove(obj)

    # ACTIONS
    def add_gold(self):
        if random.randint(1, 10) == 1:
            self.score -= 0.05
            self.hero = Objects.Weakness(self.hero)
            self.notify("You were cursed")
        else:
            self.score += 0.1
            gold = int(random.randint(10, 1000) * (1.1**(self.hero.level - 1)))
            self.hero.gold += gold
            self.notify(f"{gold} gold added")
    
    def apply_blessing(self):
        #TODO implement it
        if self.hero.gold >= int(20 * 1.5**self.level) - 2 * self.hero.stats["intelligence"]:
            self.score += 0.2
            self.hero.gold -= int(20 * 1.5**self.level) - \
                2 * self.hero.stats["intelligence"]
            if random.randint(0, 1) == 0:
                self.hero = Objects.Blessing(self.hero)
                self.notify("Blessing applied")
            else:
                self.hero = Objects.Berserk(self.hero)
                self.notify("Berserk applied")
        else:
            self.score -= 0.1
        pass
    
    def remove_effect(self):
        #TODO implement it
        if self.hero.gold >= int(10 * 1.5**self.level) - 2 * self.hero.stats["intelligence"] and "base" in dir(self.hero):
            self.hero.gold -= int(10 * 1.5**self.level) - \
                2 * self.hero.stats["intelligence"]
            self.hero = self.hero.base
            self.hero.calc_max_HP()
            self.notify("Effect removed")
        pass
    
    def restore_hp(self):
        self.score += 0.1
        self.hero.hp = self.hero.max_hp
        self.notify("HP restored")
