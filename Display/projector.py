import pygame
from core import common

def start_projection():
    # Set display running flag to true
    common.display_running = True
    
    # Initialise Pygame
    pygame.init()

    # Create display
    display = pygame.display.set_mode((common.display_width,common.display_height),pygame.FULLSCREEN)
    #pygame.display.set_caption('CARS')
    
    # Load background image image
    background_image = pygame.image.load('config/map_image.jpg')

    # Work out scale factor using width to resize image to screen - assumes aspect ratio of background is correct
    image_width = background_image.get_rect().size[0]
    scale_factor = common.display_width / image_width

    # Scale image to projector size - image should have same aspect ratio to avoid cropping image
    # Rotozoom gives nicer result than using scale
    background_image = pygame.transform.rotozoom(background_image, 0 , scale_factor)
    
    # Show image on display
    display.blit(background_image, (0,0))

    # Hide mouse
    pygame.mouse.set_visible(False)

    # Refresh display
    pygame.display.update()

def stop_projection():
    # Set display running flag to false
    common.display_running = False
    
    # Quit pygame
    pygame.quit()
