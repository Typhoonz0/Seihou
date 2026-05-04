"""
    ___      ___     ( ) / __      ___            
  ((   ) ) //___) ) / / //   ) ) //   ) ) //   / /
   \ \    //       / / //   / / //   / / //   / / 
//   ) ) ((____   / / //   / / ((___/ / ((___( (  

            ~~~ seihou main game ~~~
"""

import pygame, os, PygameShader

pygame.init()

WIDTH, HEIGHT = 1000, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

class Player:
    def __init__(self, x):
        self.x = x
        self.y = 400
        self.vy = 0
        self.ground = True
        self.frame = 0
        self.state = "idle"
        self.face = "east"
        self.hp = 100
        self.width = 60
        self.height = 120
        self.attacking = False
        self.was_hit = False
        self.hit_registered = False
        self.combo_hits = 0
        self.knocked = False
        # these are all in frames
        self.knock_timer = 0
        self.attack_timer = 0
        self.hitstun = 0 # how long player cant move
        self.invuln = 0  # invulnerability time so you cant just get spam killed
        self.post_invuln = 0 # invul after getting stunned/knocked
        self.combo_timer = 0

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

names = ["idle","walk","jump","kick","punch","hurt","fall","lying"]
dirs = ["east","west"]

for n in names:
    state.anims[n] = {}
    for d in dirs:
        state.anims[n][d] = load(base + "\\" + n + "\\" + d)

def get_rect(p):
    return pygame.Rect(p.x, p.y, p.width, p.height)

def get_attack_rect(p):
    # gives player hitbox
    if not p.attacking:
        return None

    if p.face == "east":
        return pygame.Rect(p.x + p.width, p.y + 20, 40, 40)
    else:
        return pygame.Rect(p.x - 40, p.y + 20, 40, 40)

def docombat(a, b):
    b.combo_timer = 0
    atk = get_attack_rect(a)

    if atk and not a.hit_registered:
        if atk.colliderect(get_rect(b)) and b.invuln <= 0 and b.post_invuln <= 0 and not b.was_hit:
            b.hp -= 5

            b.hitstun = 20
            b.state = "hurt"
            b.combo_hits += 1

            if b.combo_hits >= 3:
                b.knocked = True
                b.knock_timer = 120
                b.invuln = 120
                b.state = "fall"
                b.frame = 0
                b.combo_hits = 0

            # marking both sides
            a.hit_registered = True
            b.was_hit = True

            a.attacking = False
            a.attack_timer = 0
            a.state = "idle"
            a.frame = 0

def update(p, left, right, up, punch, kick):
    move = 0
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

    if punch and not p.attacking: #make sure players cant spam
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

def temphpbar(p, x, y):
    #TODO: change the hud to be nice
    pygame.draw.rect(screen, (255,0,0), (x, y, 200, 20))
    pygame.draw.rect(screen, (0,255,0), (x, y, 200 * (p.hp / 100), 20))

def draw(p, p2=False):
    anim = state.anims[p.state][p.face]
    p.frame += 0.2

    if p.state == "fall":
        # play falling only once then switch to lying
        if p.frame >= len(anim):
            p.frame = len(anim) - 1
            p.state = "lying"
            p.frame = 0
    else:
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

    docombat(p1, p2)
    docombat(p2, p1)

    cam_x += (p1.x - WIDTH//2 - cam_x) * 0.1 # move camera toward p1 slowly 
    cam_x = max(0, min(cam_x, bg.get_width() - WIDTH)) # make sure the map cant go off screen

    screen.fill((67,67,67))
    screen.blit(bg, (-cam_x, 0))

    temphpbar(p1, 50, 50)
    temphpbar(p2, 750, 50)
    draw(p1)
    if state.gamemode == "pvp":
        draw(p2, p2=True)

    pygame.display.flip()

pygame.quit()