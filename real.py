"""seihou game proto"""

import pygame,os

pygame.init()
WIDTH, HEIGHT = 1000, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

x = 300
y = 400
y_speed = 0
on_ground = True
frame = 0

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

        self.state = "idle"
        self.facing = "east"
        self.anims = {}

    def go(self, next_state):
        self.name = next_state

state = State()

base = r"C:\Users\Liam\Documents\GitHub\Seihou\assets\pixel_art_sprite_street_fighter\animations"

def load(path):
    imgs = []
    for f in sorted(os.listdir(path)):
        imgs.append(pygame.image.load(path + "\\" + f))
    return imgs

names = ["idle", "walk", "jump", "kick", "punch"]
dirs = ["east", "west"]

for n in names:
    state.anims[n] = {}
    for d in dirs:
        state.anims[n][d] = load(base + "\\" + n + "\\" + d) # TODO: make it work on not windows

running = True
while running:
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed() # using get_pressed() instead of get_event cause we need to keep going left/right when held
    move = 0

    if keys[pygame.K_a]:
        move = -5
        state.facing = "west"
    if keys[pygame.K_d]:
        move = 5
        state.facing = "east"
    if keys[pygame.K_w] and on_ground:
        y_speed = -12
        on_ground = False
        state.state = "jump"
    if keys[pygame.K_j]:
        state.state = "punch"
        frame = 0
    elif keys[pygame.K_k]:
        state.state = "kick"
        frame = 0

    x+= move
    y +=y_speed
    y_speed += 0.5

    if y >= 400:
        y = 400
        y_speed = 0
        on_ground = True

    if not on_ground:
            state.state = "jump"
    else:
        if move != 0:
            if state.state != "kick" and state.state != "punch":
                state.state = "walk"
        else:
            if state.state != "kick" and state.state != "punch":
                state.state ="idle"

    anim = state.anims[state.state][state.facing]
    frame += 0.2
    if frame >= len(anim):
        frame = 0
        if state.state == "kick" or state.state == "punch":
            state.state = "idle"

    img = anim[int(frame)]

    screen.fill((67, 67, 67))
    screen.blit(img, (x, y))
    pygame.display.flip()
    clock.tick()

pygame.quit()