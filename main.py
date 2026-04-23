import pygame, sys, json

pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 1024, 768
screen = pygame.display.set_mode((WIDTH, HEIGHT))

titleFont = pygame.font.Font("smash_hit/Smash Hit light.ttf", 67)
mainFont = pygame.font.Font("smash_hit/Smash Hit.ttf", 40)

WHITE = (255, 255, 255)
SELECTED = (255, 255, 0)

selected = 0
options_selected = 0
state = "main_menu"
music_playing = False

menu_offsets = [0, 0, 0, 0, 0]
options_menu_offsets = [0, 0, 0]

def load_file(f):
    with open(f, "r") as f:
        return json.load(f)

def save_file(f, data):
    with open(f, "w") as f:
        json.dump(data, f)

config = load_file("config.json")

def should_music_be_on():
    global music_playing
    if config["music"] == "on":
        if not music_playing:
            pygame.mixer.music.load("music/Midnight Siege.mp3")
            pygame.mixer.music.play(-1)
            music_playing = True
        pygame.mixer.music.set_volume(1.0)
    else:
        pygame.mixer.music.set_volume(0.0)

should_music_be_on()

def main_menu(events):
    global selected

    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and selected > 0:
                selected -= 1
                menu_offsets[selected] = -80

            elif event.key == pygame.K_DOWN and selected < 4:
                selected += 1
                menu_offsets[selected] = -80

            elif event.key == pygame.K_RETURN:
                if selected == 0:
                    return "game"
                elif selected == 3:
                    return "options"
                elif selected == 4:
                    return "quit"

    for i in range(5):
        menu_offsets[i] *= 0.99

    title = titleFont.render("liams game", True, WHITE)
    screen.blit(title, (100, 100))

    start = mainFont.render("start story", True, SELECTED if selected == 0 else WHITE)
    screen.blit(start, (100 + menu_offsets[0], 300))

    endless = mainFont.render("start endless", True, SELECTED if selected == 1 else WHITE)
    screen.blit(endless, (100 + menu_offsets[1], 330))

    highscore = mainFont.render("high scores", True, SELECTED if selected == 2 else WHITE)
    screen.blit(highscore, (100 + menu_offsets[2], 360))

    options = mainFont.render("options", True, SELECTED if selected == 3 else WHITE)
    screen.blit(options, (100 + menu_offsets[3], 390))

    quitpls = mainFont.render("quit", True, SELECTED if selected == 4 else WHITE)
    screen.blit(quitpls, (100 + menu_offsets[4], 420))

    return "main_menu"

def options(events):
    global options_selected, config

    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and options_selected > 0:
                options_selected -= 1
                options_menu_offsets[options_selected] = -80

            elif event.key == pygame.K_DOWN and options_selected < 2:
                options_selected += 1
                options_menu_offsets[options_selected] = -80

            elif event.key == pygame.K_LEFT:
                if options_selected == 0 and config["lives"] > 1:
                    config["lives"] -= 1
                if options_selected == 1:
                    config["music"] = "off"

            elif event.key == pygame.K_RIGHT:
                if options_selected == 0 and config["lives"] < 5:
                    config["lives"] += 1
                if options_selected == 1:
                    config["music"] = "on"

            elif event.key == pygame.K_RETURN:
                if options_selected == 2:
                    save_file("config.json", config)
                    should_music_be_on()
                    return "main_menu"

    for i in range(3):
        options_menu_offsets[i] *= 0.99
    screen.blit(mainFont.render(f"lives: {config['lives']}", True, SELECTED if options_selected == 0 else WHITE), (200  + options_menu_offsets[0], 300))

    screen.blit(mainFont.render(f"music: {config['music']}", True, SELECTED if options_selected == 1 else WHITE), (200+ options_menu_offsets[1], 340))

    screen.blit(mainFont.render("back", True,SELECTED if options_selected == 2 else WHITE), (200+ options_menu_offsets[2], 380))

    return "options"

while True:
    events = pygame.event.get()

    for e in events:
        if e.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    screen.fill((0, 0, 0))

    if state == "main_menu":
        state = main_menu(events)

    elif state == "options":
        state = options(events)

    elif state == "quit":
        pygame.quit()
        sys.exit()

    else:
        state = "quit"

    pygame.display.flip()