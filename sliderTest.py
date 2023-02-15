import pygame, sys
pygame.init()
from graphics import Slider


screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()

while True:
	card_image1 = pygame.transform.scale(pygame.image.load(f"cards/2_of_spades.png"), (80, 128))
	card_image2 = pygame.transform.scale(pygame.image.load(f"cards/5_of_spades.png"), (80, 128))
	neon = pygame.transform.scale(pygame.image.load("neon.png"), (190, 190))
	slider = Slider(screen, 500, 500, 200, 50)

	clock.tick(30)
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			pygame.quit()
			sys.exit()

	pos = pygame.mouse.get_pos()

	slider.draw(50, 1000)
	screen.blit(card_image1, (500, 300))
	screen.blit(card_image2, (540, 300))
	screen.blit(neon, (500-35, 300-37))

	pygame.display.update()




