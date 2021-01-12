import pygame
import pygame.locals
import os

import const

DEFAULT_TILE_SIZE = 32
DEFAULT_GRID_COLS = 3
DEFAULT_GRID_ROWS = 3

class Tilemap:
    """
    Tilemap is a single loaded or constructed image sliced into a grid of tiles
    +---+---+---+
    |   |   |   |
    +---+---+---+
    |   |   |   |
    +---+---+---+
    """
    def __init__(self, size = DEFAULT_TILE_SIZE, filename = None, rows = None, cols = None):
        self.size = size
        self.filename = filename
        self.tilemaps = {16:{'img':None}, 32:{'img':None}, 48:{'img':None}, 64:{'img':None}}

        if filename is not None and os.path.exists(filename):
            # load image from file
            self.image = pygame.image.load(filename).convert_alpha()
            self.image_width, self.image_height = self.image.get_size()
            self.grid_cols = cols or self.image_width // size
            self.grid_rows = rows or self.image_height // size
        else:
            # just make an empty tilemap
            self.grid_cols = cols or DEFAULT_GRID_COLS
            self.grid_rows = rows or DEFAULT_GRID_ROWS
            self.image_width = self.size * self.grid_cols
            self.image_height = self.size * self.grid_rows
            self.image = pygame.Surface((self.image_width, self.image_height), pygame.SRCALPHA)

        self.make_grid()

    def make_grid(self):
        self.update_tilemaps()

        for size in self.tilemaps:
            self.tilemaps[size]['table'] = []
            for tile_y in range(0, self.grid_rows):
                line = []
                self.tilemaps[size]['table'].append(line)
                for tile_x in range(0, self.grid_cols):
                    rect = (tile_x*size, tile_y*size, size, size)
                    line.append(self.tilemaps[size]['img'].subsurface(rect))
    
    def update_tilemaps(self):
        for size in self.tilemaps:
            temp_img = pygame.transform.scale(
                self.image, 
                (size * self.grid_cols, size * self.grid_rows)
            )
            if self.tilemaps[size]['img'] is None:
                self.tilemaps[size]['img'] = temp_img
            self.tilemaps[size]['img'].blit(temp_img, (0,0))

    def add_tile_at(self, row, col, tile):
        self.batch_add_tile_at(row, col, tile)
        self.update_tilemaps()

    def batch_add_tile_at(self, row, col, tile):
        if tile.get_size()[0] != self.size:
            tile = pygame.transform.scale( tile, (self.size, self.size))
        self.image.blit(tile, (col * self.size, row * self.size))

    def load_tile_at(self, row, col, filename):
        tile = self.batch_load_tile_at(row, col, filename)
        self.update_tilemaps()
        return tile

    def batch_load_tile_at(self, row, col, filename):
        print('batch_add_tile_at ', row, col)
        if filename is not None and os.path.exists(filename):
            tile = pygame.image.load(filename).convert_alpha()
            self.batch_add_tile_at(row, col, tile)
            return tile
        else:
            return None

    def get_tile(self, r, c, size):
        try:
            tile = self.tilemaps[size]['table'][r][c]
            return tile
        except:
            # in any problem just return a new empty tile
            return pygame.Surface((size, size), pygame.HWSURFACE)
    
    get_sprite = get_tile


class CharacterImage(TileMap,pygame.Surface):
    def __init__(self, size = DEFAULT_TILE_SIZE, filename = None, rows = 4, cols = 3):
        super().__init__(size, filename, rows, cols)

if __name__=='__main__':
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    tiles = Tilemap(32, "texture\\tilemap.png")
    tiles = Tilemap(32, rows=10, cols=8)
    tiles.batch_load_tile_at(0,1, "texture\\Ground_1.png")
    tiles.batch_load_tile_at(1,0, "texture\\Hero.png")
    tiles.update_tilemaps()
    screen = pygame.display.set_mode((64*tiles.grid_cols, 64*tiles.grid_rows))
    screen.fill((255, 255, 255))
    s = 64
    for r in range(tiles.grid_rows):
        for c in range(tiles.grid_cols):
            screen.blit(tiles.get_tile(r,c,s), (c*s, r*s))

    #screen.blit(tiles.tilemaps[32]['img'], (0,0))
    pygame.display.flip()
    while pygame.event.wait().type != pygame.locals.QUIT:
        pass