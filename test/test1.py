import pygame #modules
from sys import exit # close codes once called

pygame.init()
screen = pygame.display.set_mode((800, 400)) # width,height 10 pixels every frame
pygame.display.set_caption('test1')
clock = pygame.time.Clock()
test_font = pygame.font.Font('Pixeltype.ttf' , 50) # font type, font size
game_active = True

#test_surface = pygame.Surface((100,200)) #width, height 
sky_surface = pygame.image.load('Sky.png').convert()
ground_surface = pygame.image.load('ground.png').convert()


score_surface = test_font.render('my game', False, (64,64,64)) #test,AntiAlixing(T/F),color
score_rect = score_surface.get_rect(center = (400,50))

#test_surface.fill('Red')

snail_surface = pygame.image.load('snail1.png').convert_alpha() # converts to pygame image 
snail_rect = snail_surface.get_rect(bottomright = (600,300))
                                                                # (alpha removes white box)
snail_end_pos = -100
snail_x_pos = 600

player_surface = pygame.image.load('player_walk_1.png').convert_alpha()
player_rect = player_surface.get_rect(midbottom = (80,300)) #takes surface and draws rectangle
player_gravity = 0


#jump_surface = pygame.image.load('jump.png').convert_alpha()
#jump_rect = jump_surface.get_rect(midbottom = (80,300))


while True:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			pygame.quit()
			exit()
			
		if event.type == pygame.K_SPACE and player_rect.bottom >= 300:
			if event.type == pygame.KEYUP and player_rect.bottom >= 300:	
				player_gravity = -20
			
	if game_active:			
		screen.blit(sky_surface,(00,00)) # block image transfer up (top left)
		screen.blit(ground_surface,(00,300))
		
		pygame.draw.rect(screen, '#c0e8ec', score_rect)
		pygame.draw.rect(screen, '#c0e8ec', score_rect,10)
		screen.blit(score_surface,score_rect)
		
		snail_rect.x -= 4
		if snail_rect.right <= 0: 
			snail_rect.left = 800
		screen.blit(snail_surface,snail_rect)
		
		#PLayer
		player_gravity += 10
		player_rect.y += player_gravity
		if player_rect.bottom >= 300: player_rect.bottom = 300
		screen.blit(player_surface,player_rect)
		
		# collison
		if snail_rect.colliderect(player_rect):
			game_active = False
	     else:
	      			screen.fill('Yellow')
	
	
	#keys = pygame.key.get_pressed()
	#if keys[pygame.K_SPACE]:	
	#	print('jump')
	
	
	pygame.display.update() # update display surface 
	clock.tick(60) #should now run faster then 60 fps
