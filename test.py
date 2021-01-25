if __name__=='__main__':

    import time
    import pygame
    from dumper import dump

    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    screen.fill((255, 255, 255))

    t0 = time.monotonic()

    while True:
        if pygame.event.get():
            
            for event in pygame.event.get():
                dump(event)
        else:
            print (time.monotonic())
        #t = time.monotonic()
        #print ("{}".format(time.monotonic() - t0))
