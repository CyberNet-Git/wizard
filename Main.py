import pygame
import os

import Objects
import ScreenEngine as SE
from Logic import GameEngine
import Service
import const


pygame.init()
gameDisplay = pygame.display.set_mode(const.SCREEN_DIM)
pygame.display.set_caption("MyRPG")
KEYBOARD_CONTROL = True

if not KEYBOARD_CONTROL:
    import numpy as np
    answer = np.zeros(4, dtype=float)


size = 32 # 60

engine = GameEngine(32)

while engine.working:

    if KEYBOARD_CONTROL:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                engine.working = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_h:
                    engine.show_help = not engine.show_help
                if event.key == pygame.K_KP_PLUS:
                    size = engine.sprite_size
                    size = size + 16 if size < 64 else size
                    size = 64 if size == 48 else size
                    engine.set_sprite_size(size)
                if event.key == pygame.K_KP_MINUS:
                    size = engine.sprite_size
                    size = size - 16 if size > 16 else size
                    size = 32 if size == 48 else size
                    engine.set_sprite_size(size)
                if event.key == pygame.K_r:
                    engine = GameEngine(size)
                if event.key == pygame.K_m:
                    engine.show_battle = not engine.show_battle
                    engine.active_button = 0
                if event.key == pygame.K_ESCAPE:
                    engine.working = False

                if engine.show_battle:
                    if event.key in [pygame.K_LEFT, pygame.K_RIGHT]:
                        engine.active_button ^= 1
                    elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                        engine.show_battle = not engine.show_battle
                        #iteration += 1
                elif engine.game_process:
                    if event.key == pygame.K_UP:
                        engine.move_up()
                        #iteration += 1
                    elif event.key == pygame.K_DOWN:
                        engine.move_down()
                        #iteration += 1
                    elif event.key == pygame.K_LEFT:
                        engine.move_left()
                        #iteration += 1
                    elif event.key == pygame.K_RIGHT:
                        engine.move_right()
                        #iteration += 1

                    if event.key == pygame.K_RETURN:
                        #create_game()
                        pass
    else:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                engine.working = False
        if engine.game_process:
            actions = [
                engine.move_right,
                engine.move_left,
                engine.move_up,
                engine.move_down,
            ]
            answer = np.random.randint(0, 100, 4)
            prev_score = engine.score
            move = actions[np.argmax(answer)]()
            state = pygame.surfarray.array3d(gameDisplay)
            reward = engine.score - prev_score
            print(reward)
        else:
            #create_game()
            pass

    gameDisplay.blit(engine.drawer, (0, 0))
    engine.drawer.draw(gameDisplay)

    pygame.display.flip()

pygame.display.quit()
pygame.quit()
exit(0)
