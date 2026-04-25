"""
    ___      ___     ( ) / __      ___            
  ((   ) ) //___) ) / / //   ) ) //   ) ) //   / /
   \ \    //       / / //   / / //   / / //   / / 
//   ) ) ((____   / / //   / / ((___/ / ((___( (  
"""

import pygame, sys, json, discordrpc

DIFFICULTY = [
    {"name": "easy", "color": (0, 255, 0), "desc": "never played a stg"},
    {"name": "normal", "color": (255, 255, 0), "desc": "played a stg before!"},
    {"name": "hard", "color": (255, 140, 0), "desc": "you play stgs often?"},
    {"name": "extreme", "color": (255, 0, 0), "desc": "not fair..."},
]

CHARS = [
    {"name": "x", "color": (255, 0, 255), "class": "human",  "desc": "more stable"},
    {"name": "y", "color": (0, 255, 255), "class": "youkai", "desc": "more powerful"},
]

WHITE = (255, 255, 255)
SELECTED = (255, 255, 0)

WIDTH, HEIGHT = 1000, 720
WINDOW_W = 1280

pygame.init()
pygame.mixer.init()
pygame.display.set_caption("Seihou")

click_sound = pygame.mixer.Sound("assets/sound/mouseclick1.ogg") 
confirm_sound = pygame.mixer.Sound("assets/sound/click5.ogg") 
back_sound = pygame.mixer.Sound("assets/sound/mouserelease1.ogg") 

def load_file(f):
    with open(f, "r") as f:
        return json.load(f)

def save_file(f, data):
    with open(f, "w") as f:
        json.dump(data, f)

config = load_file("saves/config.json")

if config["discordrpc"]:
    try:
        rpc = discordrpc.RPC(app_id=1497206637994315827)
        rpc.set_activity(state="testing my game", details="ezez")
    except:
        pass

def make_window():
    if config["fullscreen"]:
        window = pygame.display.set_mode((WINDOW_W, HEIGHT), pygame.FULLSCREEN) 
    else:
        window = pygame.display.set_mode((WINDOW_W, HEIGHT))

    offset = (WINDOW_W - WIDTH) // 2
    return window, window.subsurface((offset, 0, WIDTH, HEIGHT))

window, screen = make_window()

title_font = pygame.font.Font("assets/fonts/smash_hit/Smash Hit light.ttf", 67)
main_font = pygame.font.Font("assets/fonts/smash_hit/Smash Hit.ttf", 40)
small_font = pygame.font.Font("assets/fonts/smash_hit/Smash Hit.ttf", 30)

window_bg = pygame.transform.scale(pygame.image.load("assets/img/bg.jpg").convert(), (WINDOW_W, HEIGHT))
screen_bg = pygame.transform.scale(pygame.image.load("assets/img/mainbg.jpg").convert(), (WIDTH, HEIGHT))

music_playing = False

def should_music_be_on():
    global music_playing
    if config["music"] == "on":
        if not music_playing:
            pygame.mixer.music.load("assets/sound/bg/Midnight Siege.mp3")
            pygame.mixer.music.play(-1)
            music_playing = True
        pygame.mixer.music.set_volume(1.0)
    else:
        pygame.mixer.music.set_volume(0.0)

should_music_be_on()

def kick_offsets(offsets, dt, speed=0.0001):
    for i in range(len(offsets)):
        offsets[i] *= speed ** dt
        if abs(offsets[i]) < 0.5:
            offsets[i] = 0

def move_menu_item(offsets, value=-80):
    try:
        for i in range(len(offsets)):
            offsets[i] = value
    except TypeError:
        offsets = value

class State:
    def __init__(self):
        self.name = "main_menu"

        self.menu_selection = 0
        self.menu_offset = [0, 0, 0, 0, 0]

        self.option_selection = 0
        self.option_offset = [0, 0, 0, 0, 0]

        self.diff_selection = 0
        self.diff_scroll = 0.0
        self.diff_name = "easy"
        self.char_scroll = 0.0
        self.char_offset = [0, 0]
        self.char_entered = False
        self.char_selection = 0

    def go(self, next_state):
        self.name = next_state

state = State()

def main_menu(events, dt):
    menu_labels = ["start story", "start endless", "high scores", "options", "quit"]

    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and state.menu_selection > 0:
                click_sound.play()
                state.menu_selection -= 1
                state.menu_offset[state.menu_selection] = -80
            elif event.key == pygame.K_DOWN and state.menu_selection < 4:
                click_sound.play()
                state.menu_selection += 1
                state.menu_offset[state.menu_selection] = -80
            elif event.key == pygame.K_RETURN:
                confirm_sound.play()
                if state.menu_selection == 0:
                    move_menu_item(state.diff_scroll)
                    state.diff_scroll = -120
                    return "difficulty_select"
                elif state.menu_selection == 1:
                    move_menu_item(state.option_offset)
                    return "difficulty_select"
                elif state.menu_selection == 2:
                    return "high_scores"
                elif state.menu_selection == 3:
                    move_menu_item(state.option_offset)
                    return "options"
                elif state.menu_selection == 4:
                    return "quit"
            elif event.key == pygame.K_ESCAPE:
                back_sound.play()
                if state.menu_selection != 4:
                    state.menu_selection = 4
                    state.menu_offset[4] = -80
                else:
                    return "quit"

    kick_offsets(state.menu_offset, dt)

    screen.blit(title_font.render("seihou", True, WHITE), (100, 100))
    for i, label in enumerate(menu_labels):
        color = SELECTED if state.menu_selection == i else WHITE
        screen.blit(main_font.render(label, True, color), (100 + state.menu_offset[i], 300 + i * 30))

    return "main_menu"

def difficulty_select(events, dt):
    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT and state.diff_selection > 0:
                click_sound.play()
                state.diff_selection -= 1
            elif event.key == pygame.K_RIGHT and state.diff_selection < len(DIFFICULTY) - 1:
                click_sound.play()
                state.diff_selection += 1
            elif event.key == pygame.K_RETURN:
                confirm_sound.play()
                if state.diff_selection == 0:
                    state.diff_name = "easy"
                elif state.diff_selection == 1:
                    state.diff_name = "normal"
                elif state.diff_selection == 2:
                    state.diff_name = "hard"
                elif state.diff_selection == 3:
                    state.diff_name = "extreme"
                move_menu_item(state.char_scroll)
                state.char_scroll = -120
                return "char_select"
            elif event.key == pygame.K_ESCAPE:
                back_sound.play()
                move_menu_item(state.menu_offset)
                return "main_menu"

    spacing = 350
    target = state.diff_selection * spacing
    state.diff_scroll += (target - state.diff_scroll) * (1 - pow(0.001, dt * 2))

    screen.blit(title_font.render("select difficulty", True, WHITE), (WIDTH // 4, 120))

    cx = WIDTH // 2
    cy = HEIGHT // 2

    for i, d in enumerate(DIFFICULTY):
        x = cx + (i * spacing) - state.diff_scroll
        color = d["color"] if state.diff_selection == i else (150, 150, 150)
        name_s = main_font.render(d["name"], True, color)
        desc_s = small_font.render(d["desc"], True, (200, 200, 200))
        screen.blit(name_s, (x - name_s.get_width() // 2, cy - 20))
        screen.blit(desc_s, (x - desc_s.get_width() // 2, cy + 25))

    return "difficulty_select"

def char_select(events, dt):
    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT and state.char_selection > 0:
                state.char_selection -= 1
                click_sound.play()
            elif event.key == pygame.K_RIGHT and state.char_selection < len(CHARS) - 1:
                click_sound.play()
                state.char_selection += 1
            elif event.key == pygame.K_RETURN:
                confirm_sound.play()
                return "game"
            elif event.key == pygame.K_ESCAPE:
                back_sound.play()
                move_menu_item(state.diff_scroll)
                state.diff_scroll = -120
                return "difficulty_select"

    state.char_scroll += (state.char_selection * WIDTH - state.char_scroll) * (1 - pow(0.001, dt * 2))
    kick_offsets(state.char_offset, dt)
    screen.blit(title_font.render("select character", True, WHITE), (WIDTH // 4, 120))
    screen.blit(small_font.render(f"difficulty: {state.diff_name}", True, WHITE), (WIDTH // 4, HEIGHT - 60))

    cy = HEIGHT // 2

    for i, c in enumerate(CHARS):
        x = i * WIDTH - state.char_scroll + state.char_offset[i]
        color = c["color"]

        box_w, box_h = 280, 340
        box_x = x + WIDTH // 2 + 20
        box_y = cy - box_h // 3
        pygame.draw.rect(screen, color, pygame.Rect(box_x, box_y, box_w, box_h), 2)

        name_s  = main_font.render(c["name"],  True, color)
        class_s = small_font.render(c["class"], True, (200, 200, 200))
        desc_s  = small_font.render(c["desc"],  True, (200, 200, 200))

        text_x = x + WIDTH // 2 - 60
        screen.blit(name_s, (text_x - name_s.get_width(),  cy - 50))
        screen.blit(class_s,(text_x - class_s.get_width(), cy))
        screen.blit(desc_s, (text_x - desc_s.get_width(),  cy + 30))

    return "char_select"

def options(events, dt):
    labels = [
        f"lives: {config['lives']}",
        f"music: {config['music']}",
        f"fullscreen: {config['fullscreen']}",
        f"discord rpc: {config['discordrpc']}",
        "back",
    ]

    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and state.option_selection > 0:
                click_sound.play()
                state.option_selection -= 1
                state.option_offset[state.option_selection] = -80
            elif event.key == pygame.K_DOWN and state.option_selection < 4:
                click_sound.play()
                state.option_selection += 1
                state.option_offset[state.option_selection] = -80
            elif event.key == pygame.K_LEFT:
                click_sound.play()
                if state.option_selection == 0 and config["lives"] > 1:
                    config["lives"] -= 1
                elif state.option_selection == 1:
                    config["music"] = "off"
                elif state.option_selection == 2:
                    config["fullscreen"] = False
                elif state.option_selection == 3:
                    config["discordrpc"] = False
            elif event.key == pygame.K_RIGHT:
                click_sound.play()
                if state.option_selection == 0 and config["lives"] < 5:
                    config["lives"] += 1
                elif state.option_selection == 1:
                    config["music"] = "on"
                elif state.option_selection == 2:
                    config["fullscreen"] = True
                elif state.option_selection == 3:
                    config["discordrpc"] = True
            elif event.key == pygame.K_RETURN:
                confirm_sound.play()
                if state.option_selection == 4:
                    save_file("saves/config.json", config)
                    should_music_be_on()
                    global window, screen
                    window, screen = make_window()
                    move_menu_item(state.menu_offset)
                    return "main_menu"
            elif event.key == pygame.K_ESCAPE:
                back_sound.play()
                move_menu_item(state.menu_offset)
                return "main_menu"

    kick_offsets(state.option_offset, dt)

    screen.blit(title_font.render("options", True, WHITE), (WIDTH // 4, 120))
    for i, label in enumerate(labels):
        color = SELECTED if state.option_selection == i else WHITE
        screen.blit(main_font.render(label, True, color), (200 + state.option_offset[i], 300 + i * 40))

    return "options"

def high_scores(events, dt):
    screen.blit(title_font.render("highscores", True, WHITE), (WIDTH // 4, 120))

    try:
        scores = load_file("saves/highscores.json")
        j = 0
        for k, v in enumerate(scores):
            screen.blit(small_font.render(f"{k}: {v}", True, WHITE), (WIDTH // 4, 200 + j))
            j += 40
    except:
        screen.blit(small_font.render(f"No highscores", True, WHITE), (WIDTH // 4, 200))

    for event in events:
        if event.key == pygame.K_ESCAPE:
            back_sound.play()
            move_menu_item(state.menu_offset)
            return "main_menu"

    return "high_scores"

def game(events, dt):
    print(config, state.diff_selection, state.char_selection)
    return "quit"

clock = pygame.time.Clock()
SCREENS = {
    "main_menu": main_menu,
    "options": options,
    "difficulty_select": difficulty_select,
    "char_select": char_select,
    "high_scores": high_scores,
    "game": game,
}

while True:
    dt = clock.tick(120) / 1000

    events = pygame.event.get()

    for e in events:
        if e.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    window.blit(window_bg, (0, 0))
    screen.blit(screen_bg, (0, 0))
    
    fps = str(int(clock.get_fps()))
    fps_t = small_font.render(fps, 1, (200, 200, 200))
    screen.blit(fps_t, (WIDTH - 40, HEIGHT - 20))

    handler = SCREENS.get(state.name)
    if handler:
        state.name = handler(events, dt)
    else:
        state.name = "quit"

    if state.name == "quit":
        pygame.quit()
        sys.exit()

    pygame.display.flip()