#!/usr/bin/python
## Course: OOP and patterns in Python PL
## Week: 5
## Programming task: final project is to make a game "Wizard in a cave"
## Student: v.v.panfilov@gmail.com
##          https://www.coursera.org/user/2b245f54c4482a14f06c1497686513b5
##
## Code repository at https://github.com/CyberNet-Git/wizard
##

import pygame
import os

import Objects
import ScreenEngine as SE
from Logic import GameEngine
import Service
import const

pygame.init()
gameDisplay = pygame.display.set_mode(const.SCREEN_DIM, pygame.NOFRAME)
pygame.display.set_caption("MyRPG")
KEYBOARD_CONTROL = True

if not KEYBOARD_CONTROL:
    import numpy as np
    answer = np.zeros(4, dtype=float)

closebtn = pygame.Rect(754, 2, 43, 43)
size = 32 # 60

engine = GameEngine(32)
movement= dict(zip(
        [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT],
        [engine.move_up, engine.move_down, engine.move_left, engine.move_right]
    ))
direction = dict(zip(
    [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT],
    [(0,-1),(0,1),(-1,0),(1,0)]
))

while engine.working:

    if KEYBOARD_CONTROL:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                engine.working = False

            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    if closebtn.collidepoint(event.pos):
                        engine.working = False
                elif event.button == 3:
                    pass


            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_h:
                    engine.show_help = not engine.show_help
                if event.key == pygame.K_KP_PLUS:
                    size = engine.sprite_size
                    size = size + 16 if size < 64 else size
                    #size = 64 if size == 48 else size
                    engine.set_sprite_size(size)
                if event.key == pygame.K_KP_MINUS:
                    size = engine.sprite_size
                    size = size - 16 if size > 16 else size
                    #size = 32 if size == 48 else size
                    engine.set_sprite_size(size)
                if event.key == pygame.K_r:
                    engine = GameEngine(size)
                if event.key == pygame.K_m:
                    engine.show_battle = not engine.show_battle
                    engine.active_button = 0
                if event.key == pygame.K_ESCAPE:
                    engine.working = False

                if engine.interaction:
                    if event.key in [pygame.K_LEFT, pygame.K_RIGHT]:
                        engine.active_button ^= 1
                    elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                        engine.user_choice = engine.active_button
                        engine.interact()

                # process Hero movement events
                elif engine.game_process:
                    if event.key in movement.keys():
                        if movement[event.key]():
                            pass
                        elif event.mod & pygame.KMOD_CTRL:
                            engine.break_wall(direction[event.key])

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

    gameDisplay.blit(engine.drawer, (5, 35))
    engine.drawer.draw(gameDisplay)

    pygame.display.flip()

pygame.display.quit()
pygame.quit()
exit(0)
