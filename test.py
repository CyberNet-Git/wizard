import Tilemap
import Service
import pygame
import yaml


if __name__=='__main__':
    file = open("objects.yml", "r")
    object_list = yaml.load(file.read())
    file.close()

    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    #screen = pygame.display.set_mode((64*tiles.grid_cols, 64*tiles.grid_rows))
    screen.fill((255, 255, 255))

    sp = Service.SpriteProvider()
    sp.load_ugly_sprites(object_list)

    size=32


    for i, ot in enumerate(['objects','ally','enemies']):
        #print(i, ot)
        for j, obj in enumerate(sp.ugly_ids[ot]):
            print('\t', j, obj)
            screen.blit(sp.get_object(ot,obj,size),(j*size, i*size))

    for i in range(4):
        for j in range(8):
            screen.blit(sp.get_static(i,j,size), (j*size, (i+3)*size))

    screen.blit( sp.get_hero(size),(8*size, 0*size))


    pygame.display.flip()
    while pygame.event.wait().type != pygame.locals.QUIT:
        pass