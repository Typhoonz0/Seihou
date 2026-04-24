import pygame, sys, json, discordrpc

try:
    rpc = discordrpc.RPC(app_id=1497206637994315827)
    rpc.set_activity( state="testing my game", details="ezez")
except:
    pass
    
def load_file(f):
    with open(f, "r") as f:
        return json.load(f)

def save_file(f, data):
    with open(f, "w") as f:
        json.dump(data, f)

config = load_file("config.json")

pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 1000, 720
WINDOW_W = 1280
screen_offset = (WINDOW_W - WIDTH) // 2

if config["fullscreen"]:
   window = pygame.display.set_mode((WINDOW_W, HEIGHT), pygame.FULLSCREEN) 
else:
    window = pygame.display.set_mode((WINDOW_W, HEIGHT))

def are_we_fs():
    global window, screen

    if config["fullscreen"]:
        window = pygame.display.set_mode((WINDOW_W, HEIGHT), pygame.FULLSCREEN)
    else:
        window = pygame.display.set_mode((WINDOW_W, HEIGHT))

    screen_offset = (WINDOW_W - WIDTH) // 2
    screen = window.subsurface((screen_offset, 0, WIDTH, HEIGHT))

screen = window.subsurface((screen_offset, 0, WIDTH, HEIGHT))

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
options_menu_offsets = [0, 0, 0, 0, 0]
char_select_offsets = [0, 0, 0]
char_select_entered = False
char_scroll = 0
diff_entered = False
diff_selected = 0
diff_scroll = 0


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

def kick_char_select():
    for i in range(len(char_select_offsets)):
        char_select_offsets[i] = -80

def kick_difficulty():
    global diff_scroll
    diff_scroll = -120

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
                    kick_difficulty()
                    return "difficulty_select"
                elif selected == 3:
                    kick_options()
                    return "options"
                elif selected == 4:
                    return "quit"
            elif event.key == pygame.K_ESCAPE:
                if selected != 4:
                    selected = 4
                    menu_offsets[4] = -80
                else:
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

def difficulty_select(events, dt):
    global diff_selected, diff_scroll

    DIFFICULTY = [
        {"name": "easy", "color": (0, 255, 0), "desc": "never played a stg"},
        {"name": "normal", "color": (255, 255, 0), "desc": "played a stg before!"},
        {"name": "hard", "color": (255, 140, 0), "desc": "you play stgs often?"},
        {"name": "extreme", "color": (255, 0, 0), "desc": "not fair..."},
    ]

    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT and diff_selected > 0:
                diff_selected -= 1

            elif event.key == pygame.K_RIGHT and diff_selected < len(DIFFICULTY) - 1:
                diff_selected += 1

            elif event.key == pygame.K_RETURN:
                kick_char_select()
                return "char_select"

            elif event.key == pygame.K_ESCAPE:
                kick_main()
                return "main_menu"

    spacing = 350
    target = diff_selected * spacing

    diff_scroll += (target - diff_scroll) * (1 - pow(0.001, dt * 2))

    screen.blit(titleFont.render("select difficulty", True, WHITE), (WIDTH // 4, 120))

    center_x = WIDTH // 2
    y = HEIGHT // 2

    k = 0
    while k < len(DIFFICULTY):
        d = DIFFICULTY[k]

        x = center_x + (k * spacing) - diff_scroll

        selected = diff_selected == k
        color = d["color"] if selected else (150, 150, 150)

        name_surf = mainFont.render(d["name"], True, color)
        desc_surf = smallFont.render(d["desc"], True, (200, 200, 200))

        screen.blit(name_surf, (x - name_surf.get_width() // 2, y - 20))
        screen.blit(desc_surf, (x - desc_surf.get_width() // 2, y + 25))

        k += 1

    return "difficulty_select"

def char_select(events, dt):
    global char_selected, char_scroll, char_select_entered

    CHARS = [
        {"name": "x", "color": (255,0,255), "class": "human", "desc": "more stable"},
        {"name": "y", "color": (0,255,255), "class": "youkai", "desc": "more powerful"},
    ]

    if not char_select_entered:
        kick_char_select()
        char_select_entered = True

    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                char_selected = max(0, char_selected - 1)

            elif event.key == pygame.K_RIGHT:
                char_selected = min(len(CHARS) - 1, char_selected + 1)

            elif event.key == pygame.K_RETURN:
                char_select_entered = False
                return "game"

            elif event.key == pygame.K_ESCAPE:
                char_select_entered = False
                kick_difficulty()
                return "difficulty_select"

    box_w, box_h = 200, 300
    gap = 40

    target = char_selected * (box_w + gap)
    char_scroll += (target - char_scroll) * (1 - pow(0.001, dt * 6))

    for i in range(len(char_select_offsets)):
        char_select_offsets[i] *= pow(0.001, dt * 6)
        if abs(char_select_offsets[i]) < 0.5:
            char_select_offsets[i] = 0
    screen.blit(titleFont.render("select agent", True, WHITE), (WIDTH // 4, 100))
    box_y = (HEIGHT - box_h) // 2
    total_w = len(CHARS) * box_w + (len(CHARS) - 1) * gap
    start_x = (WIDTH - total_w) // 2

    k = 0
    while k < len(CHARS):
        char = CHARS[k]

        bx = start_x + k * (box_w + gap) - char_scroll + char_select_offsets[k]
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
            elif event.key == pygame.K_DOWN and options_selected < 3:
                options_selected += 1
                options_menu_offsets[options_selected] = -80
            elif event.key == pygame.K_LEFT:
                if options_selected == 0 and config["lives"] > 1:
                    config["lives"] -= 1
                if options_selected == 1:
                    config["music"] = "off"
                if options_selected == 2:
                    config["fullscreen"] = False
            elif event.key == pygame.K_RIGHT:
                if options_selected == 0 and config["lives"] < 5:
                    config["lives"] += 1
                if options_selected == 1:
                    config["music"] = "on"
                if options_selected == 2:
                    config["fullscreen"] = True
            elif event.key == pygame.K_RETURN:
                if options_selected == 3:
                    save_file("config.json", config)
                    should_music_be_on()
                    are_we_fs()
                    kick_main()
                    return "main_menu"
            elif event.key == pygame.K_ESCAPE:
                kick_main()
                return "main_menu"
    for i in range(4):
        options_menu_offsets[i] *= (0.0001 ** dt)
    screen.blit(titleFont.render("options", True, WHITE), (WIDTH // 4, 120))
    screen.blit(mainFont.render(f"lives: {config['lives']}", True, SELECTED if options_selected == 0 else WHITE), (200 + options_menu_offsets[0], 300))
    screen.blit(mainFont.render(f"music: {config['music']}", True, SELECTED if options_selected == 1 else WHITE), (200 + options_menu_offsets[1], 340))
    screen.blit(mainFont.render(f"fullscreen: {config['fullscreen']}", True, SELECTED if options_selected == 2 else WHITE), (200 + options_menu_offsets[2], 380))
    screen.blit(mainFont.render("back", True, SELECTED if options_selected == 3 else WHITE), (200 + options_menu_offsets[3], 420))

    return "options"

def game(events, dt):
    global config, diff_selected, char_selected
    print( config, diff_selected, char_selected)
    return "quit"

clock = pygame.time.Clock()
window_bg = pygame.image.load("bg.jpg").convert()
screen_bg = pygame.image.load("mainbg.jpg").convert()
window_bg = pygame.transform.scale(window_bg, (WINDOW_W, HEIGHT))
screen_bg = pygame.transform.scale(screen_bg, (WIDTH, HEIGHT))

while True:
    dt = clock.tick() / 1000

    events = pygame.event.get()

    for e in events:
        if e.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    window.blit(window_bg, (0, 0))
    screen.blit(screen_bg, (0, 0))

    if state == "main_menu":
        state = main_menu(events, dt)
    elif state == "options":
        state = options(events, dt)
    elif state == "difficulty_select":
        state = difficulty_select(events, dt)
    elif state == "char_select":
        state = char_select(events, dt)
    elif state == "game":
        state = game(events, dt)
    elif state == "quit":
        pygame.quit()
        sys.exit()
    else:
        state = "quit"

    pygame.display.flip()