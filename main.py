"""
    ___      ___     ( ) / __      ___            
  ((   ) ) //___) ) / / //   ) ) //   ) ) //   / /
   \ \    //       / / //   / / //   / / //   / / 
//   ) ) ((____   / / //   / / ((___/ / ((___( (  

Typhoonz0 | GitHub
"""

from __future__ import annotations # without this, i couldn't use the Player type as a type inside it's own method, see line 169
from typing import Optional # technically we could just write "type | None" but "Optional[T]" is more clean
from abc import ABC, abstractmethod # getting good grades

try:
    import pygame, sys, json, discordrpc, os, PygameShader, random # actually required modules to get the game working
except (ModuleNotFoundError, ImportError) as e:
    print(f"couldn't start game because {e}")
    print(f"you should read the manual")
    exit()

DIFFICULTY: list[dict[str, tuple[int, int, int] | str]] = [
    {"name": "easy", "color": (0, 255, 0), "desc": "AI doesn't move"},
    {"name": "normal", "color": (255, 255, 0), "desc": "a simple AI"},
    {"name": "hard", "color": (255, 140, 0), "desc": "you fight often?"},
    {"name": "extreme", "color": (255, 0, 0), "desc": "not fair..."},
]

CHARS: list[dict[str, tuple[int, int, int] | str]] = [
    {"name": "x", "color": (255, 0, 0), "class": "human", "desc": "regular guy"},
    {"name": "y", "color": (0, 255, 0), "class": "alien", "desc": "green guy"},
]

WHITE: tuple[int, int, int] = (255, 255, 255)
SELECTED: tuple[int, int, int] = (255, 255, 0)

WIDTH: int
HEIGHT: int
WIDTH, HEIGHT = 1000, 720
WINDOW_W: int = 1280
FPS: int = 100

pygame.init()
pygame.mixer.init()
pygame.display.set_caption("Seihou")

click_sound: pygame.mixer.Sound = pygame.mixer.Sound("assets/sound/mouseclick1.ogg") 
confirm_sound: pygame.mixer.Sound = pygame.mixer.Sound("assets/sound/click5.ogg") 
back_sound: pygame.mixer.Sound = pygame.mixer.Sound("assets/sound/mouserelease1.ogg") 

def play_sound_fx(sound: pygame.mixer.Sound) -> None:
    if config["soundfx"] == "on": 
        sound.play()

def load_file(f: str) -> dict:
    with open(f, "r") as f:
        return json.load(f)

def save_file(f: str, data: dict) -> None:
    with open(f, "w") as f:
        json.dump(data, f)
    
config: dict[str, object] = load_file("saves/config.json")

if config["discordrpc"]: 
    try:
        rpc: discordrpc.RPC = discordrpc.RPC(app_id=1497206637994315827)
        rpc.set_activity(state="fighting noobs", details="ezez")
    except discordrpc.exceptions.DiscordNotOpened:
        print("couldn't connect to discord")

def make_window() -> tuple[pygame.Surface, pygame.Surface]:
    """Create the pygame window and a centred subsurface to draw on.

    Note:
        Returns both the full window and the inner screen subsurface.
        The subsurface is all that we actually draw on (the "screen" below) because the game is in 4:3,
        and I wanted some decoration on the sides instead of black bars.
    """

    if config["fullscreen"]:
        window: pygame.Surface = pygame.display.set_mode((WINDOW_W, HEIGHT), pygame.FULLSCREEN) 
    else:
        window = pygame.display.set_mode((WINDOW_W, HEIGHT))

    offset: int = (WINDOW_W - WIDTH) // 2
    return window, window.subsurface((offset, 0, WIDTH, HEIGHT))

window: pygame.Surface
screen: pygame.Surface
window, screen = make_window()

title_font: pygame.font.Font = pygame.font.Font("assets/fonts/smash_hit/Smash Hit light.ttf", 67)
main_font: pygame.font.Font = pygame.font.Font("assets/fonts/smash_hit/Smash Hit.ttf", 40)
small_font: pygame.font.Font = pygame.font.Font("assets/fonts/smash_hit/Smash Hit.ttf", 30)

window_bg: pygame.Surface = pygame.transform.scale(pygame.image.load("assets/img/bg.jpg").convert(), (WINDOW_W, HEIGHT))
screen_bg: pygame.Surface = pygame.transform.scale(pygame.image.load("assets/img/mainbg.jpg").convert(), (WIDTH, HEIGHT))

music_playing: bool = False

MUSIC: dict[str, str] = {
    "main_menu": "Midnight Siege.mp3",
    "stage1": "Revolutions.mp3"
}

# the only reason why this is outside of the State object is to demonstrate inheritance
class Offsets(ABC):
    @abstractmethod # decorator to demonstrate the concept of abstraction: you cant make a Offsets class it can only be inherited from
    def __init__(self) -> None:
        self.menu_selection: int = 0
        self.menu_offset: list[int] = [0, 0, 0, 0, 0]
        self.pause_menu_selection: int = 0
        self.pause_menu_offset: list[int] = [0, 0, 0, 0, 0]

        self.option_selection: int = 0
        self.option_offset: list[int] = [0, 0, 0, 0, 0, 0]

        self.diff_selection: int = 0
        self.diff_scroll: float = 0.0
        self.diff_name: str = "n/a"
        self.char_scroll: float = 0.0
        self.char_offset: list[int] = [0, 0]
        self.char_entered: bool = False
        self.char_selection: int = 0

class State(Offsets):
    def __init__(self) -> None:
        super().__init__() # we need all the variables in the Offsets class above to be initialised
        self.name: str = "main_menu"

        self.prev_state: str = "pause_menu" 
        self.actual_prev_state: str = "main_menu"
        self.track_playing: str = MUSIC["main_menu"]
        self.music_state: str = MUSIC["main_menu"]

        self.anims: dict[str, dict[str, list[pygame.Surface]]] = {}
        self.gamemode: str = "pvp"
        self.gameover: bool = False


class Player:
    def __init__(self, x: int) -> None:
        self.wins: int = 0
        self.x: int = x
        self.y: int = 400
        self.vy: float = 0
        self.ground: bool = True
        self.frame: float = 0
        self.state: str = "idle"
        self.face: str = "east"
        self.hp: int = 100
        self.width: int = 60
        self.height: int = 120
        self.dead: bool = False
        self.attacking: bool = False
        self.was_hit: bool = False
        self.hit_registered: bool = False
        self.combo_hits: int = 0
        self.knocked: bool = False
        self.char: str = "x"
        # these are all in frames
        self.knock_timer: int = 0
        self.attack_timer: int = 0
        self.hitstun: int = 0 # how long player cant move
        self.invuln: int = 0  # invulnerability time so you cant just get spam killed
        self.post_invuln: int = 0 # invul after getting stunned/knocked
        self.combo_timer: int = 0

    def get_rect(self: Player) -> pygame.Rect:
        """Returns a hitbox rect that represents the players actual body."""
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def get_hitbox(self: Player) -> Optional[pygame.Rect]:
        """Returns a hitbox that is bigger because the player has their foot or hand out."""
        if not self.attacking:
            return None

        if self.face == "east":
            return pygame.Rect(self.x + self.width, self.y + 20, 40, 40)
        else:
            return pygame.Rect(self.x - 40, self.y + 20, 40, 40)

    def get_attack_damage(self) -> int:
        """This function only exists to demonstrate Polymorphism, same below in the other two classes."""
        return 5

class HumanPlayer(Player):
    def get_attack_damage(self) -> int:
        return 5

class AlienPlayer(Player):
    def get_attack_damage(self) -> float:
        return 5.1

state: State = State()

p1: Player = Player(300)
p2: Player = Player(500)
cam_x: float = 0
who_won_text: Optional[str] = None
base: str = r"assets\pixel_art_sprite_street_fighter\animations"

bg: pygame.Surface = pygame.image.load(r"assets\img\Untitled.png").convert()
bg = pygame.transform.scale(bg, (1400, 720))

def load(path: str) -> list[pygame.Surface]:
    """Load all images in a directory as surfaces, sorted by filename."""

    a: list[pygame.Surface] = []
    for f in sorted(os.listdir(path)):
        a.append(pygame.image.load(path + "/" + f))
    return a

names: list[str] = ["idle","walk","jump","kick","punch","hurt","fall","lying"]
dirs: list[str] = ["east","west"]

for n in names:
    state.anims[n] = {}
    for d in dirs:
        state.anims[n][d] = load(base + "/" + n + "/" + d)

def play_music() -> None:
    """Start, stop, or switch background music based on the current music_state and if its supposed to be playing in the first place."""

    global music_playing

    if config["music"] != "on":
        pygame.mixer.music.set_volume(0.0)
        return

    track: Optional[str] = MUSIC.get(state.music_state)

    if not track:
        return

    if state.track_playing != state.music_state:
        pygame.mixer.music.load(f"assets/sound/bg/{track}")
        pygame.mixer.music.play(-1)
        state.track_playing = state.music_state
        music_playing = True

    pygame.mixer.music.set_volume(1.0)

def kick_offsets(offsets: list[float], dt: float, speed: float = 0.0001) -> None:
    """Smoothly animate a list of menu offsets toward zero using powers.
    Note:
        The powers make it slide in then slow down as it aproaches where its meant to be.
    """
    for i in range(len(offsets)):
        offsets[i] *= speed ** dt
        if abs(offsets[i]) < 0.5: 
            offsets[i] = 0

def move_menu_item(offsets: list[int] | float, value: int = -80) -> None:
    """Instantly snap all offsets to a given value to prepare for a slide animation."""
    try:
        for i in range(len(offsets)):
            offsets[i] = value
    except TypeError:
        offsets = value

def reset_round() -> None:
    """Reset both players to their starting positions and clear all combat state."""

    p1.x, p1.y = 300, 400
    p2.x, p2.y = 500, 400

    for p in (p1, p2):
        p.hp = 100
        p.vy = 0
        p.ground = True
        p.state = "idle"
        p.frame = 0
        p.attacking = False
        p.was_hit = False
        p.hit_registered = False
        p.combo_hits = 0
        p.knocked = False
        p.knock_timer = 0
        p.attack_timer = 0
        p.hitstun = 0
        p.invuln = 0
        p.post_invuln = 0
        p.combo_timer = 0
        p.dead = False

def reset_match() -> None:
    """Resets wins and triggers a round reset."""
    p1.wins = 0
    p2.wins = 0

    state.gameover = False
    who_won_text = None

    reset_round()
    
def main_menu(events: list[pygame.event.Event], dt: float) -> str:
    """Render and handle inputs for the main menu screen."""
    menu_labels: list[str] = ["vs ai", "vs player", "high scores", "options", "quit"]
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
                    state.gamemode = "pve"
                    move_menu_item(state.diff_scroll)
                    state.actual_prev_state = "main_menu"
                    state.diff_scroll = -120
                    return "difficulty_select"
                elif state.menu_selection == 1:
                    state.gamemode = "pvp"
                    move_menu_item(state.option_offset)
                    state.char_scroll = -120
                    state.actual_prev_state = "main_menu"
                    return "char_select"
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
        color: tuple[int, int, int] = SELECTED if state.menu_selection == i else WHITE
        screen.blit(main_font.render(label, True, color), (100 + state.menu_offset[i], 300 + i * 30))

    return "main_menu"

def difficulty_select(events: list[pygame.event.Event], dt: float) -> str:
    """Render and handle inputs for the difficulty select screen."""

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
                state.actual_prev_state = "difficulty_select"
                return "char_select"
            elif event.key == pygame.K_ESCAPE:
                play_sound_fx(back_sound)
                move_menu_item(state.menu_offset)
                return "main_menu"

    spacing: int = 350
    target: float = state.diff_selection * spacing
    state.diff_scroll += (target - state.diff_scroll) * (1 - pow(0.001, dt * 2)) 

    screen.blit(title_font.render("select difficulty", True, WHITE), (WIDTH // 4, 120))

    cx: int = WIDTH // 2
    cy: int = HEIGHT // 2

    for i, d in enumerate(DIFFICULTY):
        x: float = cx + (i * spacing) - state.diff_scroll
        color: tuple[int, int, int] = d["color"] if state.diff_selection == i else (150, 150, 150)
        name_s: pygame.Surface = main_font.render(d["name"], True, color)
        desc_s: pygame.Surface = small_font.render(d["desc"], True, (200, 200, 200))
        screen.blit(name_s, (x - name_s.get_width() // 2, cy - 20))
        screen.blit(desc_s, (x - desc_s.get_width() // 2, cy + 25))

    return "difficulty_select"

def char_select(events: list[pygame.event.Event], dt: float) -> str:
    """Render and handle input for the character selection screen."""
    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT and state.char_selection > 0:
                state.char_selection -= 1
                play_sound_fx(click_sound)
            elif event.key == pygame.K_RIGHT and state.char_selection < len(CHARS) - 1:
                play_sound_fx(click_sound)
                state.char_selection += 1
            elif event.key == pygame.K_RETURN:
                if state.char_selection == 0:
                    state.char = "x"
                else:
                    state.char = "y"
                reset_match()
                play_sound_fx(confirm_sound)
                return "game"
            elif event.key == pygame.K_ESCAPE:
                play_sound_fx(back_sound)
                # could be main menu or difficulty lets just do both
                move_menu_item(state.diff_scroll)
                state.diff_scroll = -120
                move_menu_item(state.menu_offset)
                return state.actual_prev_state

    state.char_scroll += (state.char_selection * WIDTH - state.char_scroll) * (1 - pow(0.001, dt * 2))
    kick_offsets(state.char_offset, dt)
    screen.blit(title_font.render("select character", True, WHITE), (WIDTH // 4, 120))
    if state.gamemode == "pvp":
        screen.blit(main_font.render("player 2 will get the other character", True, WHITE), (WIDTH // 4, 200))
    else:
        screen.blit(small_font.render(f"difficulty: {state.diff_name}", True, WHITE), (WIDTH // 4, HEIGHT - 60))

    cy: int = HEIGHT // 2

    for i, c in enumerate(CHARS):
        x: float = i * WIDTH - state.char_scroll + state.char_offset[i]
        color: tuple[int, int, int] = c["color"]

        # loading a box with the sprite inside it
        # just doing some positioning calculations
        box_w: int
        box_h: int
        box_w, box_h = 280, 340
        box_x: float = x + WIDTH // 2 + 20
        box_y: int = cy - box_h // 3
        pygame.draw.rect(screen, color, pygame.Rect(box_x, box_y, box_w, box_h), 2) # outline

        img: pygame.Surface = pygame.image.load("assets/pixel_art_sprite_street_fighter/rotations/south.png").convert_alpha()

        img_w: int
        img_h: int
        img_w, img_h = img.get_size()
        scale: float = min(box_w / img_w, box_h / img_h)
        new_size: tuple[int, int] = (int(img_w * scale), int(img_h * scale))

        img_scaled: pygame.Surface = pygame.transform.scale_by(img, 4)
        img_x: int = box_x + (box_w - new_size[0]) // 2
        img_y: int = box_y + (box_h - new_size[1]) // 2

        if i == 0: # character named x
            screen.blit(img_scaled, (img_x, img_y))

        elif i == 1: # character named y
            PygameShader.hsl_effect(img_scaled, 0.3)
            screen.blit(img_scaled, (img_x, img_y))
            
        name_s: pygame.Surface = main_font.render(c["name"],  True, color)
        class_s: pygame.Surface = small_font.render(c["class"], True, (200, 200, 200))
        desc_s: pygame.Surface = small_font.render(c["desc"],  True, (200, 200, 200))

        text_x: float = x + WIDTH // 2 - 60
        screen.blit(name_s, (text_x - name_s.get_width(),  cy - 50))
        screen.blit(class_s,(text_x - class_s.get_width(), cy))
        screen.blit(desc_s, (text_x - desc_s.get_width(),  cy + 30))

    return "char_select"

def options(events: list[pygame.event.Event], dt: float) -> str:
    """Render and handle input for the options screen.

    Note:
        Changes are only saved to disk when the player confirms by pressing enter on 'back', however the music and sound effects are affected immediately.
    """
    labels: list[str] = [
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
                    state.menu_selection = 0
                    return state.prev_state
            elif event.key == pygame.K_ESCAPE:
                play_sound_fx(back_sound)
                move_menu_item(state.menu_offset)
                state.menu_selection = 0
                return state.prev_state

    kick_offsets(state.option_offset, dt)

    if state.prev_state != "main_menu":
        # this is a dimmed version of the last frame in the game
        overlay: pygame.Surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

    screen.blit(title_font.render("options", True, WHITE), (WIDTH // 4, 120))

    for i, label in enumerate(labels):
        color: tuple[int, int, int] = SELECTED if state.option_selection == i else WHITE
        screen.blit(
            main_font.render(label, True, color),
            (200 + state.option_offset[i], 300 + i * 40)
        )

    return "options"

def high_scores(events: list[pygame.event.Event], dt: float) -> str:
    """Renders the high scores screen."""
    screen.blit(title_font.render("highscores", True, WHITE), (WIDTH // 4, 120))

    try:
        scores: list = load_file("saves/highscosres.json")
        j: int = 0
        for k, v in enumerate(scores):
            screen.blit(small_font.render(f"{k}: {v}", True, WHITE), (WIDTH // 4, 200 + j))
            j += 40
    except FileNotFoundError:
        screen.blit(small_font.render(f"No highscores", True, WHITE), (WIDTH // 4, 200))

    for event in events:
        if event.type == pygame.KEYDOWN: 
            if event.key == pygame.K_ESCAPE:
                play_sound_fx(back_sound)
                move_menu_item(state.menu_offset)
                return "main_menu"

    return "high_scores"

def ai_update(ai: Player, enemy: Player) -> tuple[bool, bool, bool, bool, bool]:
    # very basic ai 
    move_left: bool = False
    move_right: bool = False
    up: bool = False
    punch: bool = False
    kick: bool = False
    dx: int = enemy.x - ai.x

    if abs(dx) > 80: # move toward player
        if dx < 0:
            move_left = True
        else:
            move_right = True

    if state.diff_name == "easy": # ai doesnt move in easy mode
        return False, False, False, False, False           

    # attack if close enough
    if abs(dx) < 90 and ai.attack_timer <= 0 and not ai.attacking:
        handicap_chance = random.random()
        # ai chooses to randomly attack, harder the difficulty, the more likely it happens
        if (state.diff_name == "normal" and handicap_chance > 0.98) or (state.diff_name == "hard" and handicap_chance > 0.97):
            if random.random() < 0.6:
                punch = True
            else:
                kick = True

    if ai.ground and random.random() < 0.01: # occasional jump
        up = True

    return move_left, move_right, up, punch, kick

def round_has_ended(winner: Player) -> None:
    """Give a point to the winner and either reset or end the match.

    Note:
    This was originally in reset_round() but since it was called the wrong amount of times,
    it meant that the winner of the first match will have 1 extra round win forever
    """

    global who_won_text

    winner.wins += 1

    if winner.wins >= config["lives"]:
        state.gameover = True
        who_won_text = "player 1 wins!" if winner == p1 else "player 2 wins!"
    else:
        reset_round()

def game_over(events: list[pygame.event.Event], dt: float) -> str:
    """Render and handle input for the game over screen."""

    menu_labels: list[str] = ["rematch", "main menu"]

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
                    p1.wins = 0
                    p2.wins = 0
                    state.gameover = False
                    reset_match()
                    return "game"

                elif state.menu_selection == 1:
                    p1.wins = 0
                    p2.wins = 0
                    state.gameover = False
                    state.menu_selection = 0
                    play_sound_fx(back_sound)
                    kick_offsets(state.menu_offset, dt)
                    return "main_menu"

    kick_offsets(state.menu_offset, dt)

    overlay: pygame.Surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))

    screen.blit(title_font.render("game over", True, WHITE), (100, 100))
    screen.blit(main_font.render(who_won_text, True, WHITE), (100, 180))

    for i, label in enumerate(menu_labels):
        color: tuple[int, int, int] = SELECTED if state.menu_selection == i else WHITE
        screen.blit(
            main_font.render(label, True, color),
            (100 + state.menu_offset[i], 300 + i * 30)
        )

    return "game_over"

def do_combat(a: Player, b: Player) -> None:
    """Check for and apply hits from player a onto player b, then check for death.

    Note:
        Player a is the attacker and player b is the one being attacked.
        5 hits in a short time span triggers a knockdown with temporary invulnerability.
    """
    b.combo_timer = 0
    atk: Optional[pygame.Rect] = a.get_hitbox()

    if atk and not a.hit_registered: # make sure u cant just spam hits over and over
        # if hitboxes are touching and defending player hasnt been attacked very recently
        if atk.colliderect(b.get_rect()) and b.invuln <= 0 and b.post_invuln <= 0 and not b.was_hit:
            b.hp -= a.get_attack_damage() 

            b.hitstun = 20
            b.state = "hurt"
            b.combo_hits += 1

            if b.combo_hits >= 5:
                b.knocked = True
                b.knock_timer = 120
                b.invuln = 120
                b.state = "fall"
                b.frame = 0
                b.combo_hits = 0

            a.hit_registered = True
            b.was_hit = True

            a.attacking = False
            a.attack_timer = 0
            a.state = "idle"
            a.frame = 0
    
    # if one player is dead
    if p1.hp <= 0 and not p1.knocked:
        p1.knocked = True
        p1.dead = True
        p1.knock_timer = 10
        print(p1.knock_timer)
    if p2.hp <= 0 and not p2.knocked:
        p2.knocked = True
        p2.dead = True
        p2.knock_timer = 10

def update(p: Player, left: bool, right: bool, up: bool, punch: bool, kick: bool) -> None:
    """Updates a player's physics, state, and combat times for this frame."""

    move: int = 0
    # invulnerability countdown
    if p.invuln > 0:
        p.invuln -= 1
    if p.knocked:
        p.knock_timer -= 1
        if p.state != "lying" and p.state != "fall":
            p.state = "fall"
        if p.knock_timer <= 0:
            p.knocked = False
            p.state = "idle"
        return # if u knocked u cant move so no need to update

    # same with hitstunned
    if p.hitstun > 0:
        p.hitstun -= 1
        p.state = "hurt"

        #when hitstun ends immediately recover
        if p.hitstun == 0:
            if p.ground:
                p.state = "idle"
            else:
                p.state = "jump"
        p.post_invuln = 10
        return

    if p.post_invuln > 0:
        p.post_invuln -= 1

    # move and p.vy move the player that amount of pixels 
    if left:
        move = -5
        p.face = "west"
    if right:
        move = 5
        p.face = "east"
    if up and p.ground:
        p.vy = -12  # -12 is 12 pixels up
        p.ground = False
        p.state = "jump"

    if punch and not p.attacking: # make sure players cant spam
        p.state = "punch"
        p.frame = 0
        p.attacking = True
        p.attack_timer = 15
        p.hit_registered = False
    if kick and not p.attacking:
        p.state = "kick"
        p.frame = 0
        p.attacking = True
        p.attack_timer = 20
        p.hit_registered = False

    p.x += move
    # make sure the player doesnt go off screen 
    if p.x < 0:
        p.x = 0
    
    if p.x > bg.get_width() - 120:
        p.x = bg.get_width() - 120

    p.y += p.vy
    p.vy += 0.5 # gravity

    if p.y >= 400: 
        # make sure we dont sink into floor
        p.y = 400
        p.vy = 0
        p.ground = True

    if p.attacking:
        p.attack_timer -= 1
        if p.attack_timer <= 0:
            p.attacking = False
            p.hit_registered = False

    if not p.ground:
        p.state = "jump"
    else:
        if move != 0:
            if p.state not in ("kick","punch","hurt"):
                p.state = "walk"
        else:
            if p.state not in ("kick","punch","hurt"):
                p.state = "idle"

    # reset combo if not recently hit
    if p.hitstun == 0 and not p.attacking and not p.knocked:
        p.combo_timer += 1
        if p.combo_timer > 120:  
            p.combo_hits = 0
    else:
        p.combo_timer = 0

    if p.hitstun == 0:
        p.was_hit = False

def draw_hud(p: Player, x: int, y: int) -> None:
    """Draw the health bar for a player and both players' win counts. """
    pygame.draw.rect(screen, (255,0,0), (x, y, 200, 20))
    pygame.draw.rect(screen, (0,255,0), (x, y, 200 * (p.hp / 100), 20))

    w1: pygame.Surface = main_font.render(f"p1 wins: {p1.wins}/{config['lives']}", True, (255,255,255))
    w2: pygame.Surface = main_font.render(f"p2 wins: {p2.wins}/{config['lives']}", True, (255,255,255))

    screen.blit(w1, (50, 20))
    screen.blit(w2, (750, 20))


def draw_player(p: Player, p2: bool = False) -> None:
    """Draws the current animation frame for a player."""
    anim: list[pygame.Surface] = state.anims[p.state][p.face]
    p.frame += 0.2

    if p.state == "fall": # play falling only once then switch to lying
        if p.frame >= len(anim):
            p.frame = len(anim) - 1
            p.state = "lying"
            p.frame = 0
    else:
        if p.frame >= len(anim):
            p.frame = 0
            if p.state in ("kick", "punch"):
                p.state = "idle"

    img: pygame.Surface = anim[int(p.frame)]
    img = pygame.transform.scale_by(img, 4)

    # colour switching the other player
    if state.char == "y" and not p2:
        # making us green with hueshift
        PygameShader.hsl_effect(img, 0.3)

    elif state.char == "x" and p2:
        PygameShader.hsl_effect(img, 0.3)

    screen.blit(img, (p.x - cam_x, p.y))

def between_death() -> None:
    """Checks if a player has died between rounds."""
    if p1.dead:
        round_has_ended(p2) 
    if p2.dead:
        round_has_ended(p1) 
            
def game(events: list[pygame.event.Event], dt: float) -> str:
    """Render and update the main gameplay state for one frame.

    Note:
        In pve mode, p2 is driven by ai_update instead of keyboard input.
    """
    global cam_x
    state.music_state = "stage1"
    for e in events:
        if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
            return "pause_menu"

    keys: pygame.key = pygame.key.get_pressed() # using get_pressed() instead of get_event cause we need to keep going left/right when held

    if not state.gameover:
        update(p1, keys[pygame.K_a], keys[pygame.K_d], keys[pygame.K_w], keys[pygame.K_t], keys[pygame.K_y])

        if state.gamemode == "pve":
            l, r, u, p, k = ai_update(p2, p1) # ai inputs
            update(p2, l, r, u, p, k)
        else:
            update(p2,
                keys[pygame.K_LEFT],
                keys[pygame.K_RIGHT],
                keys[pygame.K_UP],
                keys[pygame.K_o],
                keys[pygame.K_p])

    do_combat(p1, p2)
    do_combat(p2, p1)

    cam_x += (p1.x - WIDTH//2 - cam_x) * 0.1 # move camera toward p1 slowly 
    cam_x = max(0, min(cam_x, bg.get_width() - WIDTH)) # make sure the map cant go off screen

    screen.fill((67,67,67))
    screen.blit(bg, (-cam_x, 0))

    draw_hud(p1, 50, 50)
    draw_hud(p2, 750, 50)
    between_death()
    if state.gameover:
        return "game_over"
    draw_player(p1)
    draw_player(p2, p2=True)
        
    return "game"

def pause_menu(events: list[pygame.event.Event], dt: float) -> str:
    """Render and handle input for the pause menu."""

    menu_labels: list[str] = ["resume", "options", "quit to menu"]

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
                    reset_match()
                    state.menu_selection = 0
                    move_menu_item(state.menu_offset)
                    return "main_menu"

            elif event.key == pygame.K_ESCAPE:
                play_sound_fx(back_sound)
                return "game"

    kick_offsets(state.menu_offset, dt)

    overlay: pygame.Surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))

    screen.blit(title_font.render("paused", True, WHITE), (100, 100))

    for i, label in enumerate(menu_labels):
        color: tuple[int, int, int] = SELECTED if state.menu_selection == i else WHITE
        screen.blit(
            main_font.render(label, True, color),
            (100 + state.menu_offset[i], 300 + i * 30)
        )

    return "pause_menu"

clock: pygame.time.Clock = pygame.time.Clock()
SCREENS: dict[str, callable] = {
    "main_menu": main_menu,
    "options": options,
    "pause_menu": pause_menu,
    "difficulty_select": difficulty_select,
    "char_select": char_select,
    "high_scores": high_scores,
    "game_over": game_over,
    "game": game,
}

while True:
    dt: float = clock.tick(FPS) / 1000

    events: list[pygame.event.Event] = pygame.event.get()

    for e in events:
        if e.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    window.blit(window_bg, (0, 0))
    screen.blit(screen_bg, (0, 0))
    play_music()
    fps: str = str(int(clock.get_fps()))
    fps_t: pygame.Surface = small_font.render(fps, 1, (200, 200, 200))
    screen.blit(fps_t, (WIDTH - 40, HEIGHT - 20))

    handler: Optional[callable] = SCREENS.get(state.name)
    if handler:
        state.name = handler(events, dt)
    else:
        state.name = "quit"

    if state.name == "quit":
        pygame.quit()
        sys.exit()

    pygame.display.flip()