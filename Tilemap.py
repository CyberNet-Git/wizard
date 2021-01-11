import pygame
import pygame.locals
import os


class Tilemap:

    def __init__(self, size, filename=None, rows=None, cols=None):
        self.size = size
        self.filename = filename
        self.tilemaps = {16:{'img':None}, 32:{'img':None}, 48:{'img':None}, 64:{'img':None}}

        if filename is not None and os.path.exists(filename):
            self.image = pygame.image.load(filename).convert_alpha()
            self.image_width, self.image_height = self.image.get_size()
            self.grid_cols = cols or self.image_width // size
            self.grid_rows = rows or self.image_height // size
        else:
            # just make an empty tilemap
            self.grid_cols = cols
            self.grid_rows = rows
            self.image_width = self.size * self.grid_cols
            self.image_height = self.size * self.grid_rows
            self.image = pygame.Surface((self.image_width, self.image_height), pygame.SRCALPHA)

        self.make_grid()

    def make_grid(self):
        for size in self.tilemaps:
            self.tilemaps[size]['img'] = pygame.transform.scale(self.image, (size * self.grid_cols, size * self.grid_rows))
            self.tilemaps[size]['table'] = []
            for tile_y in range(0, self.grid_rows):
                line = []
                self.tilemaps[size]['table'].append(line)
                for tile_x in range(0, self.grid_cols):
                    rect = (tile_x*size, tile_y*size, size, size)
                    line.append(self.tilemaps[size]['img'].subsurface(rect))


    def get_tile(self, r, c, size):
        try:
            #print (f'Requested {r} {c} {size}')
            tile = self.tilemaps[size]['table'][r][c]
            return tile
        except:
            return pygame.Surface((size, size), pygame.HWSURFACE)
    
    get_sprite = get_tile

if __name__=='__main__':
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    tiles = Tilemap(32, "texture\\tilemap.png")
    tiles = Tilemap(32, rows=10, cols=8)
    screen = pygame.display.set_mode((64*tiles.grid_cols, 64*tiles.grid_rows))
    screen.fill((255, 255, 255))
    s = 64
    for r in range(tiles.grid_rows):
        for c in range(tiles.grid_cols):
            screen.blit(tiles.get_tile(r,c,s), (c*s, r*s))
    pygame.display.flip()
    while pygame.event.wait().type != pygame.locals.QUIT:
        pass