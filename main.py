import pygame, sys, json

pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 1024, 768
screen = pygame.display.set_mode((WIDTH, HEIGHT))

titleFont = pygame.font.Font("smash_hit/Smash Hit light.ttf", 67)
mainFont = pygame.font.Font("smash_hit/Smash Hit.ttf", 40)
smallFont = pygame.font.Font("smash_hit/Smash Hit.ttf", 30)

WHITE = (255, 255, 255)
SELECTED = (255, 255, 0)

selected = 0
options_selected = 0
char_selected = 0
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

def kick_main():
    for i in range(len(menu_offsets)):
        menu_offsets[i] = -80

def kick_options():
    for i in range(len(options_menu_offsets)):
        options_menu_offsets[i] = -80

def main_menu(events, dt):
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
                    return "char_select"
                elif selected == 3:
                    kick_options()
                    return "options"
                elif selected == 4:
                    return "quit"

    for i in range(5):
        menu_offsets[i] *= (0.0001 ** dt)

    screen.blit(titleFont.render("liams game", True, WHITE), (100, 100))
    screen.blit(mainFont.render("start story", True, SELECTED if selected == 0 else WHITE), (100 + menu_offsets[0], 300))
    screen.blit(mainFont.render("start endless", True, SELECTED if selected == 1 else WHITE), (100 + menu_offsets[1], 330))
    screen.blit(mainFont.render("high scores", True, SELECTED if selected == 2 else WHITE), (100 + menu_offsets[2], 360))
    screen.blit(mainFont.render("options", True, SELECTED if selected == 3 else WHITE), (100 + menu_offsets[3], 390))
    screen.blit(mainFont.render("quit", True, SELECTED if selected == 4 else WHITE), (100 + menu_offsets[4], 420))

    return "main_menu"

def char_select(events, dt):
    global char_selected

    CHARS = [
        {"name": "x", "color": (255,0,255), "class": "human", "desc": "more stable"},
        {"name": "y",  "color": (0,255,255),  "class": "youkai", "desc": "more powerful"},
    ]

    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                char_selected = max(0, char_selected - 1)
            elif event.key == pygame.K_RIGHT:
                char_selected = min(len(CHARS) - 1, char_selected + 1)
            elif event.key == pygame.K_RETURN:
                return "game"
            elif event.key == pygame.K_ESCAPE:
                return "main_menu"

    box_w, box_h = 200, 300
    box_y = (768 - box_h) // 2
    gap = 40
    total_w = len(CHARS) * box_w + (len(CHARS) - 1) * gap
    start_x = (1024 - total_w) // 2

    k = 0
    while k < len(CHARS):
        char = CHARS[k]
        bx = start_x + k * (box_w + gap)
        selected = char_selected == k

        pygame.draw.rect(screen, (40, 40, 60), (bx, box_y, box_w, box_h), border_radius=8)
        if selected:
            pygame.draw.rect(screen, (255, 255, 255), (bx - 6, box_y - 6, box_w + 12, box_h + 12), width=2, border_radius=12)

        cx = bx + box_w // 2

        name_surf = mainFont.render(char["name"], True, WHITE)
        screen.blit(name_surf, (cx - name_surf.get_width() // 2, box_y + 30))

        class_surf = smallFont.render(char["class"], True, char["color"])
        screen.blit(class_surf, (cx - class_surf.get_width() // 2, box_y + 65))

        desc_surf = smallFont.render(char["desc"], True, (200, 200, 220))
        screen.blit(desc_surf, (cx - desc_surf.get_width() // 2, box_y + 110))

        k += 1

    return "char_select"

def options(events, dt):
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
                    kick_main()
                    return "main_menu"
            elif event.key == pygame.K_ESCAPE:
                return "main_menu"
    for i in range(3):
        options_menu_offsets[i] *= (0.0001 ** dt)

    screen.blit(mainFont.render(f"lives: {config['lives']}", True, SELECTED if options_selected == 0 else WHITE), (200 + options_menu_offsets[0], 300))
    screen.blit(mainFont.render(f"music: {config['music']}", True, SELECTED if options_selected == 1 else WHITE), (200 + options_menu_offsets[1], 340))
    screen.blit(mainFont.render("back", True, SELECTED if options_selected == 2 else WHITE), (200 + options_menu_offsets[2], 380))

    return "options"

clock = pygame.time.Clock()

while True:
    dt = clock.tick() / 1000

    events = pygame.event.get()

    for e in events:
        if e.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    screen.fill((0, 0, 0))

    if state == "main_menu":
        state = main_menu(events, dt)
    elif state == "options":
        state = options(events, dt)
    elif state == "char_select":
        state = char_select(events, dt)
    elif state == "quit":
        pygame.quit()
        sys.exit()
    else:
        state = "quit"

    pygame.display.flip()