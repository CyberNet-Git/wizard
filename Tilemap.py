import pygame
import pygame.locals


class Tilemap:
    tilemaps = {16:{'img':None}, 32:{'img':None}, 48:{'img':None}, 64:{'img':None}}

    def __init__(self, filename, size):
        image = pygame.image.load(filename).convert_alpha()
        self.image_width, self.image_height = image.get_size()
        self.filename = filename
        self.size = size
        self.grid_cols = self.image_width // size
        self.grid_rows = self.image_height // size

        for size in self.tilemaps:
            print(size)
            self.tilemaps[size]['img'] = pygame.transform.scale(image, (size * self.grid_cols, size * self.grid_rows))
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