import pygame, sys

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
titleFont = pygame.font.Font("smash_hit/Smash Hit.ttf", size=67)
mainFont = pygame.font.Font("smash_hit/Smash Hit.ttf", size=20)
finish = False
WHITE = (255, 255, 255)
SELECTED = (255, 255, 0)
selected = 0
while finish != True:

    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                if selected > 0:
                    selected -= 1 
            elif event.key == pygame.K_DOWN:
                if selected < 4:
                    selected += 1
            elif event.key == pygame.K_ESCAPE:
                finish = True

        if event.type == pygame.QUIT:
            finish = True

    title = titleFont.render("liams game", True, WHITE)
    screen.blit(title, (100, 100))

    start = mainFont.render("start story", True, SELECTED if selected == 0 else WHITE)
    screen.blit(start, (100, 300))

    endless = mainFont.render("start endless", True, SELECTED if selected == 1 else WHITE)
    screen.blit(endless, (100, 320))
    
    highscore = mainFont.render("high scores", True, SELECTED if selected == 2 else WHITE)
    screen.blit(highscore, (100, 340))

    options = mainFont.render("options", True, SELECTED if selected == 3 else WHITE)
    screen.blit(options, (100, 360))

    quitpls = mainFont.render("quit", True, SELECTED if selected == 4 else WHITE)
    screen.blit(quitpls, (100, 380))

    pygame.display.flip()

pygame.quit()
sys.exit()
