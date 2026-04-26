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

def play_sound_fx(sound):
    if config["soundfx"] == "on": 
        sound.play()

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
game_width = int(WIDTH * 2 / 3)

player = {
    "x": game_width // 2,
    "y": HEIGHT - 60,
    "speed": 300
}

game_surface = pygame.Surface((game_width, HEIGHT))

MUSIC = {
    "main_menu": "Midnight Siege.mp3",
    "stage_1_1": "Revolutions.mp3"
}

class State:
    def __init__(self):
        self.name = "main_menu"

        self.menu_selection = 0
        self.menu_offset = [0, 0, 0, 0, 0]
        self.pause_menu_selection = 0
        self.pause_menu_offset = [0, 0, 0, 0, 0]

        self.option_selection = 0
        self.option_offset = [0, 0, 0, 0, 0, 0]

        self.diff_selection = 0
        self.diff_scroll = 0.0
        self.diff_name = "easy"
        self.char_scroll = 0.0
        self.char_offset = [0, 0]
        self.char_entered = False
        self.char_selection = 0
        self.prev_state = "pause_menu" 
        self.track_playing = MUSIC["main_menu"]
        self.music_state = MUSIC["main_menu"]

    def go(self, next_state):
        self.name = next_state

state = State()

def play_music():
    global music_playing

    if config["music"] != "on":
        pygame.mixer.music.set_volume(0.0)
        return

    track = MUSIC.get(state.music_state)

    if not track:
        return

    if state.track_playing != state.music_state:
        pygame.mixer.music.load(f"assets/sound/bg/{track}")
        pygame.mixer.music.play(-1)
        state.track_playing = state.music_state
        music_playing = True

    pygame.mixer.music.set_volume(1.0)

def kick_offsets(offsets, dt, speed=0.0001):
    # this slides in things using powers
    # the powers make it slide in then slow down as it aproaches where its meant to be 
    for i in range(len(offsets)):
        offsets[i] *= speed ** dt
        if abs(offsets[i]) < 0.5: 
            offsets[i] = 0

def move_menu_item(offsets, value=-80):
    # this adruptly presets a offset value 
    try:
        for i in range(len(offsets)):
            offsets[i] = value
    except TypeError:
        offsets = value



def main_menu(events, dt):
    menu_labels = ["start story", "start endless", "high scores", "options", "quit"]
    state.music_state = "main_menu"
    
    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and state.menu_selection > 0:
                play_sound_fx(click_sound)
                state.menu_selection -= 1
                state.menu_offset[state.menu_selection] = -80
            elif event.key == pygame.K_DOWN and state.menu_selection < 4:
                play_sound_fx(click_sound)
                state.menu_selection += 1
                state.menu_offset[state.menu_selection] = -80
            elif event.key == pygame.K_RETURN:
                play_sound_fx(confirm_sound)
                if state.menu_selection == 0:
                    move_menu_item(state.diff_scroll)
                    state.diff_scroll = -120
                    return "difficulty_select"
                elif state.menu_selection == 1:
                    move_menu_item(state.option_offset)
                    state.diff_scroll = -120
                    return "difficulty_select"
                elif state.menu_selection == 2:
                    return "high_scores"
                elif state.menu_selection == 3:
                    move_menu_item(state.option_offset)
                    state.prev_state = "main_menu"
                    return "options"
                elif state.menu_selection == 4:
                    return "quit"
            elif event.key == pygame.K_ESCAPE:
                play_sound_fx(back_sound)
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
                play_sound_fx(click_sound)
                state.diff_selection -= 1
            elif event.key == pygame.K_RIGHT and state.diff_selection < len(DIFFICULTY) - 1:
                play_sound_fx(click_sound)
                state.diff_selection += 1
            elif event.key == pygame.K_RETURN:
                play_sound_fx(confirm_sound)
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
                play_sound_fx(back_sound)
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
                play_sound_fx(click_sound)
            elif event.key == pygame.K_RIGHT and state.char_selection < len(CHARS) - 1:
                play_sound_fx(click_sound)
                state.char_selection += 1
            elif event.key == pygame.K_RETURN:
                play_sound_fx(confirm_sound)
                return "game"
            elif event.key == pygame.K_ESCAPE:
                play_sound_fx(back_sound)
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
        f"soundfx: {config['soundfx']}",
        f"fullscreen: {config['fullscreen']}",
        f"discord rpc: {config['discordrpc']}",
        "back",
    ]

    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and state.option_selection > 0:
                play_sound_fx(click_sound)
                state.option_selection -= 1
                state.option_offset[state.option_selection] = -80

            elif event.key == pygame.K_DOWN and state.option_selection < len(labels) - 1:
                play_sound_fx(click_sound)
                state.option_selection += 1
                state.option_offset[state.option_selection] = -80

            elif event.key == pygame.K_LEFT:
                play_sound_fx(click_sound)
                if state.option_selection == 0 and config["lives"] > 1:
                    config["lives"] -= 1
                elif state.option_selection == 1:
                    config["music"] = "off"
                elif state.option_selection == 2:
                    config["soundfx"] = "off"
                elif state.option_selection == 3:
                    config["fullscreen"] = False
                elif state.option_selection == 4:
                    config["discordrpc"] = False

            elif event.key == pygame.K_RIGHT:
                play_sound_fx(click_sound)
                if state.option_selection == 0 and config["lives"] < 5:
                    config["lives"] += 1
                elif state.option_selection == 1:
                    config["music"] = "on"
                elif state.option_selection == 2:
                    config["soundfx"] = "on"
                elif state.option_selection == 3:
                    config["fullscreen"] = True
                elif state.option_selection == 4:
                    config["discordrpc"] = True

            elif event.key == pygame.K_RETURN:
                play_sound_fx(confirm_sound)
                if state.option_selection == 5:
                    save_file("saves/config.json", config)
                    global window, screen
                    window, screen = make_window()
                    move_menu_item(state.menu_offset)
                    return state.prev_state
            elif event.key == pygame.K_ESCAPE:
                play_sound_fx(back_sound)
                move_menu_item(state.menu_offset)
                return state.prev_state

    kick_offsets(state.option_offset, dt)

    if state.prev_state != "main_menu":
        screen.blit(game_surface, (0, 0))

        # this is a dimmed version of the last frame in the game
        overlay = pygame.Surface((game_width, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

    screen.blit(title_font.render("options", True, WHITE), (game_width // 4, 120))

    for i, label in enumerate(labels):
        color = SELECTED if state.option_selection == i else WHITE
        screen.blit(
            main_font.render(label, True, color),
            (200 + state.option_offset[i], 300 + i * 40)
        )

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
            play_sound_fx(back_sound)
            move_menu_item(state.menu_offset)
            return "main_menu"

    return "high_scores"


def game(events, dt):
    state.music_state = "stage_1_1"
    keys = pygame.key.get_pressed()

    if keys[pygame.K_LEFT]:
        player["x"] -= player["speed"] * dt
    if keys[pygame.K_RIGHT]:
        player["x"] += player["speed"] * dt
    if keys[pygame.K_UP]:
        player["y"] -= player["speed"] * dt
    if keys[pygame.K_DOWN]:
        player["y"] += player["speed"] * dt

    player["x"] = max(10, min(game_width - 10, player["x"]))
    player["y"] = max(10, min(HEIGHT - 10, player["y"]))

    game_surface.fill((67,67,67))
    pygame.draw.circle(game_surface, (255, 255, 255),
                       (int(player["x"]), int(player["y"])), 10)

    text = main_font.render(state.diff_name, True, (255, 255, 255))
    screen.blit(text, (game_width + 100, 100))
    screen.blit(game_surface, (0, 0))

    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "pause_menu"

    return "game"

def pause_menu(events, dt):
    menu_labels = ["resume", "options", "quit to menu"]

    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and state.menu_selection > 0:
                play_sound_fx(click_sound)
                state.menu_selection -= 1
                state.menu_offset[state.menu_selection] = -80

            elif event.key == pygame.K_DOWN and state.menu_selection < len(menu_labels) - 1:
                play_sound_fx(click_sound)
                state.menu_selection += 1
                state.menu_offset[state.menu_selection] = -80

            elif event.key == pygame.K_RETURN:
                play_sound_fx(confirm_sound)

                if state.menu_selection == 0:
                    return "game"
                elif state.menu_selection == 1:
                    move_menu_item(state.option_offset)
                    state.prev_state = "pause_menu"
                    return "options"
                elif state.menu_selection == 2:
                    return "main_menu"

            elif event.key == pygame.K_ESCAPE:
                play_sound_fx(back_sound)
                return "game"

    kick_offsets(state.menu_offset, dt)

    screen.blit(game_surface, (0, 0))

    overlay = pygame.Surface((game_width, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))

    screen.blit(title_font.render("paused", True, WHITE), (100, 100))

    for i, label in enumerate(menu_labels):
        color = SELECTED if state.menu_selection == i else WHITE
        screen.blit(
            main_font.render(label, True, color),
            (100 + state.menu_offset[i], 300 + i * 30)
        )

    return "pause_menu"

clock = pygame.time.Clock()
SCREENS = {
    "main_menu": main_menu,
    "options": options,
    "pause_menu": pause_menu,
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
    play_music()
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