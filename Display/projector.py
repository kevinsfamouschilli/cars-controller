import pygame

pygame.init()

display_width = 1600
display_height = 1200

gameDisplay = pygame.display.set_mode((display_width,display_height),pygame.FULLSCREEN)
pygame.display.set_caption('CARS')

black = (0,0,0)
white = (255,255,255)

clock = pygame.time.Clock()
crashed = False
carImg = pygame.image.load('map_image.jpg')

gameDisplay.fill(white)
gameDisplay.blit(carImg, (0,0))
pygame.mouse.set_visible(False)
pygame.display.update()

while not crashed:
    try:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                crashed = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    crashed = True
    except KeyboardInterrupt:
        crashed = True
        
    pygame.time.wait(1000)
    
pygame.quit()

quit()
