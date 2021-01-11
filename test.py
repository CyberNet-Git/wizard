import Tilemap
import Service
import pygame


if __name__=='__main__':
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    tiles = Tilemap("texture\\tilemap.png", 32)
    screen = pygame.display.set_mode((64*tiles.grid_cols, 64*tiles.grid_rows))
    screen.fill((255, 255, 255))
    s = 64
    for r in range(tiles.grid_rows):
        for c in range(tiles.grid_cols):
            screen.blit(tiles.get_tile(r,c,s), (c*s, r*s))
    pygame.display.flip()
    while pygame.event.wait().type != pygame.locals.QUIT:
        pass