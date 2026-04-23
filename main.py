import pygame, sys

pygame.init()

WIDTH, HEIGHT = 1024, 768
screen = pygame.display.set_mode((WIDTH, HEIGHT))
titleFont = pygame.font.Font("smash_hit/Smash Hit light.ttf", size=67)
mainFont = pygame.font.Font("smash_hit/Smash Hit.ttf", size=40)

WHITE = (255, 255, 255)
SELECTED = (255, 255, 0)
selected = 0

def main_menu(events) -> str:
    global selected

    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                if selected > 0:
                    selected -= 1 
            elif event.key == pygame.K_DOWN:
                if selected < 4:
                    selected += 1
            elif event.key == pygame.K_RETURN:
                if selected == 0:
                    return "game"
                elif selected == 4:
                    return "quit"

    title = titleFont.render("liams game", True, WHITE)
    screen.blit(title, (100, 100))

    start = mainFont.render("start story", True, SELECTED if selected == 0 else WHITE)
    screen.blit(start, (100, 300))

    endless = mainFont.render("start endless", True, SELECTED if selected == 1 else WHITE)
    screen.blit(endless, (100, 330))
    
    highscore = mainFont.render("high scores", True, SELECTED if selected == 2 else WHITE)
    screen.blit(highscore, (100, 360))

    options = mainFont.render("options", True, SELECTED if selected == 3 else WHITE)
    screen.blit(options, (100, 390))

    quitpls = mainFont.render("quit", True, SELECTED if selected == 4 else WHITE)
    screen.blit(quitpls, (100, 420))

    return "main_menu"


state = "main_menu"

while True:
    events = pygame.event.get()
    for i in events:
        if i.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    if state == "main_menu":
        state = main_menu(events)
    elif state == "quit":
        pygame.quit()
        sys.exit()
    else:
        print("implementing later")
        state = "quit"

    pygame.display.flip()
