import pygame, os, PygameShader

pygame.init()

WIDTH, HEIGHT = 1000, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

class Player:
    def __init__(self, x):
        self.x = x # where does it spawn initially
        self.y = 400
        self.vy = 0
        self.ground = True
        self.frame = 0
        self.state = "idle"
        self.face = "east"
        self.attack = 0

class State:
    def __init__(self):
        self.name = "game"
        self.anims = {}
        self.gamemode = "pvp"

state = State()

p1 = Player(300)
p2 = Player(500)
cam_x = 0

base = r"C:\Users\Liam\Documents\GitHub\Seihou\assets\pixel_art_sprite_street_fighter\animations"

bg = pygame.image.load(r"C:\Users\Liam\Documents\GitHub\Seihou\assets\img\Untitled.png").convert()
bg = pygame.transform.scale(bg, (2000, 720))

def load(path):
    a = []
    for f in sorted(os.listdir(path)):
        a.append(pygame.image.load(path + "\\" + f))
    return a

names = ["idle","walk","jump","kick","punch","hurt","fall"]
dirs = ["east","west"]

for n in names:
    state.anims[n] = {}
    for d in dirs:
        state.anims[n][d] = load(base + "\\" + n + "\\" + d)

def update(p, left, right, up, punch, kick):
    move = 0

    if left:
        move = -5
        p.face = "west"
    if right:
        move = 5
        p.face = "east"
    if up and p.ground:
        p.vy = -12
        p.ground = False
        p.state = "jump"
    if punch:
        p.state = "punch"
        p.frame = 0
    if kick:
        p.state = "kick"
        p.frame = 0
    p.x += move
    # make sure the player doesnt go off screen
    if p.x < 0:
        p.x = 0
    if p.x > WIDTH - 60:
        p.x = WIDTH - 60

    p.y += p.vy
    p.vy += 0.5 # gravity

    if p.y >= 400: 
        # make sure we dont sink into floor
        p.y = 400
        p.vy = 0
        p.ground = True

    if not p.ground:
        p.state = "jump"
    else:
        if move != 0:
            if p.state not in ("kick","punch"):
                p.state = "walk"
        else:
            if p.state not in ("kick","punch"):
                p.state = "idle"

def draw(p, p2=False):
    anim = state.anims[p.state][p.face]

    p.frame += 0.2
    if p.frame >= len(anim):
        p.frame = 0
        if p.state in ("kick","punch"):
            p.state = "idle"

    img = anim[int(p.frame)]
    img = pygame.transform.scale_by(img, 3)

    if p2:
        # making p2 green with hueshift
        PygameShader.hsl_effect(img, 0.3)

    screen.blit(img, (p.x - cam_x, p.y))

running = True
while running:
    dt = clock.tick(60) / 1000

    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed() # using get_pressed() instead of get_event cause we need to keep going left/right when held

    update(p1, keys[pygame.K_a], keys[pygame.K_d], keys[pygame.K_w], keys[pygame.K_t], keys[pygame.K_y])

    if state.gamemode == "pvp":
        update(p2, keys[pygame.K_LEFT], keys[pygame.K_RIGHT], keys[pygame.K_UP], keys[pygame.K_o], keys[pygame.K_p])

    cam_x += (p1.x - WIDTH//2 - cam_x) * 0.1
    cam_x = max(0, min(cam_x, bg.get_width() - WIDTH))

    screen.fill((67,67,67))
    screen.blit(bg, (-cam_x, 0))

    draw(p1)
    if state.gamemode == "pvp":
        draw(p2, p2=True)

    pygame.display.flip()

pygame.quit()