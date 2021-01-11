import Service


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
        self.sp = Service.SpriteProvider()

        self.hero = Objects.Hero(base_stats, self.sp.get_hero(sprite_size))
        self.hero.level = 1
        
        #FIXME зачем это все в сервисе? это чать игры
        Service.service_init(engine.sprite_size)

        #FIXME old service_init code
        file = open("objects.yml", "r")

        object_list = yaml.load(file.read())
        object_list_prob = object_list_tmp

        object_list_actions = {
            'reload_game': self.reload_game,
            'add_gold': self.add_gold,
            'apply_blessing': self.apply_blessing,
            'remove_effect': self.remove_effect,
            'restore_hp': self.restore_hp
        }

        for obj in object_list_prob['objects']:
            prop = object_list_prob['objects'][obj]
            prop_tmp = object_list['objects'][obj]
            prop['sprite'][0] = create_sprite(
                os.path.join(OBJECT_TEXTURE, prop_tmp['sprite'][0]), sprite_size)
            prop['action'] = object_list_actions[prop_tmp['action']]

        for ally in object_list_prob['ally']:
            prop = object_list_prob['ally'][ally]
            prop_tmp = object_list['ally'][ally]
            prop['sprite'][0] = create_sprite(
                os.path.join(ALLY_TEXTURE, prop_tmp['sprite'][0]), sprite_size)
            prop['action'] = object_list_actions[prop_tmp['action']]

        for enemy in object_list_prob['enemies']:
            prop = object_list_prob['enemies'][enemy]
            prop_tmp = object_list['enemies'][enemy]
            prop['sprite'][0] = create_sprite(
                os.path.join(ENEMY_TEXTURE, prop_tmp['sprite'][0]), sprite_size)

        file.close()
        #FIXME old service_init code

        # Load and create levels from YAML 
        file = open("levels.yml", "r")
        self.level_list = yaml.load(file.read())['levels']
        self.level_list.append({'map': EndMap.Map(), 'obj': EndMap.Objects()})
        file.close()


        self.reload_game()
        self.drawer = SE.GameSurface((640, 480), pygame.SRCALPHA, (0, 480),
                                SE.ProgressBar((640, 120), (640, 0),
                                                SE.InfoWindow((160, 480), (50, 50),
                                                                SE.HelpWindow((700, 500), pygame.SRCALPHA, (0, 0),
                                                                            SE.ScreenHandle(
                                                                                (0, 0))
                                                                            ))))



    def reload_game(self):
        self.level_list
        level_list_max = len(level_list) - 1
        self.level += 1
        self.hero.position = [1, 1]
        self.objects = []
        generator = level_list[min(engine.level, level_list_max)]
        _map = generator['map'] #.get_map()
        self.load_map(_map)
        self.add_objects(generator['obj'].get_objects(_map))
        #self.add_hero(hero)

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
        #TODO implement it
        pass
    
    def apply_blessing(self):
        #TODO implement it
        pass
    
    def remove_effect(self):
        #TODO implement it
        pass
    
    def restore_hp(self):
        #TODO implement it
        pass
