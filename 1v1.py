import pygame
import random
import os

pygame.init()
clock = pygame.time.Clock()
fenetre = pygame.display.set_mode((1000, 500))
pygame.display.set_caption("GALAXI")

arial48 = pygame.font.SysFont("arial", 48)
arial36 = pygame.font.SysFont("arial", 36)

rect1 = pygame.Rect(180, 300, 160, 70)        
rect2 = pygame.Rect(680, 300, 160, 70)         
rect_rejouer = pygame.Rect(400, 250, 200, 60)  
rect_menu = pygame.Rect(400, 330, 200, 60)     

croix = None

etoiles = [(random.randint(0, 1000), random.randint(0, 500)) for _ in range(100)]
etoiles1 = [(random.randint(0, 1000), random.randint(0, 500)) for _ in range(100)]

fonds_l = ["fond.png", "fond1.jpg", "fond2.jpg", "fond3.jpg", "fond4.jpg"]
fonds = []
for f in fonds_l:
    try:
        img = pygame.transform.scale(pygame.image.load(f), (1000, 500))
    except:
        img = pygame.Surface((1000, 500))
        img.fill((0, 0, 0))
    fonds.append(img)

v1 = None
v1_retourne = None
v2 = None
bot_image_gauche = None
bot_image_droite = None

pause = False

try:
    v1 = pygame.transform.scale(pygame.image.load("vaisseau1.png"), (60, 60))
    v1_retourne = pygame.transform.flip(v1, True, False)
except:
    v1 = pygame.Surface((60, 60))
    v1.fill((0, 200, 200))
    v1_retourne = pygame.transform.flip(v1, True, False)

try:
    v2 = pygame.transform.scale(pygame.image.load("vaisseau2.png"), (60, 60))
    bot_image_gauche = v2
    bot_image_droite = pygame.transform.flip(v2, True, False)
except:
    v2 = pygame.Surface((60, 60))
    v2.fill((200, 200, 0))
    bot_image_gauche = v2
    bot_image_droite = pygame.transform.flip(v2, True, False)

def charger_son(nom_fichier):
    try:
        return pygame.mixer.Sound(nom_fichier)
    except:
        return None

tir = charger_son("tir.mp3")
impact = charger_son("impact.wav")
explosion = charger_son("explosion.ogg")
vie = charger_son("life.flac")
try:
    pygame.mixer.music.load("fond.mp3")
    pygame.mixer.music.set_volume(0.7)
    pygame.mixer.music.play(loops=6)
except:
    pass

projectiles1 = []
projectiles2 = []
projectiles_bot = []

appui1 = False
appui2 = False
mode_bot = False
en_jeu = False
mort = False

h1, h2 = 100, 200
h3, h4 = 800, 200
vie1 = 100
vie2 = 100
retourne = False
niveau = 1
fond_choisi = None
fond_index = -1

if os.path.exists("record.txt"):
    try:
        with open("record.txt", "r") as f:
            record = int(f.read())
    except:
        record = 0
else:
    record = 0

souris = None  

class Croix:
    def __init__(self):
        self.x = random.randint(50, 950)
        self.y = random.randint(50, 450)
        self.timer = 0

    def dessiner(self, surface):
        pygame.draw.line(surface, (0, 255, 0), (self.x - 8, self.y), (self.x + 8, self.y), 3)
        pygame.draw.line(surface, (0, 255, 0), (self.x, self.y - 8), (self.x, self.y + 8), 3)

class Bot:
    def __init__(self, x, y, intervalle):
        self.x = x
        self.y = y
        self.intervalle = intervalle
        self.timer = 0
        self.direction_y = random.choice([-1, 1])
        self.direction_x = random.choice([-1, 1])
        self.vie = 3
        self.dir_droite = True

    def deplacer(self):
        if random.random() < 0.05:
            self.direction_y = random.choice([-1, 1])
        if random.random() < 0.05:
            self.direction_x = random.choice([-1, 1])
        self.y += self.direction_y * 2
        self.x += self.direction_x * 2
        self.y = max(20, min(450, self.y))
        self.x = max(0, min(950, self.x))
        self.dir_droite = self.x < h1

    def tirer(self):
        self.timer += 1
        if self.timer >= self.intervalle:
            self.timer = 0
            dx = 5 if self.dir_droite else -5
            return [self.x + 25, self.y + 25, dx, 0]
        return None

def creer_bots(n):
    liste_bots = []
    for _ in range(n):
        x = random.randint(600, 900)
        y = random.randint(50, 400)
        intervalle = random.randint(30, 90)
        bot = Bot(x, y, intervalle)
        liste_bots.append(bot)
    return liste_bots

def annuler_projectiles(liste1, liste2):
    resultat1, resultat2 = [], []
    for p1 in liste1:
        rect_p1 = pygame.Rect(p1[0]-4, p1[1]-4, 8, 8)
        collision = False
        for p2 in liste2:
            rect_p2 = pygame.Rect(p2[0]-4, p2[1]-4, 8, 8)
            if rect_p1.colliderect(rect_p2):
                liste2.remove(p2)
                collision = True
                break
        if not collision:
            resultat1.append(p1)
    resultat2.extend(liste2)
    return resultat1, resultat2

bots = []

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        souris_pos = pygame.mouse.get_pos()

        if not en_jeu and not mort:
            if rect1.collidepoint(souris_pos):
                souris = '1v1'
            elif rect2.collidepoint(souris_pos):
                souris = 'bot'
            else:
                souris = None

        if mort:
            if rect_rejouer.collidepoint(souris_pos):
                souris = 'rejouer'
            elif rect_menu.collidepoint(souris_pos):
                souris = 'menu'
            else:
                souris = None

        if not en_jeu and not mort and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if souris == '1v1':
                en_jeu = True
                mode_bot = False
                vie1 = 100
                vie2 = 100
                projectiles1 = []
                projectiles2 = []
                projectiles_bot.clear()
                bots = []
                h1, h2 = 100, 200
                h3, h4 = 800, 200
                retourne = False
                niveau = 1
                fond_index = random.randint(0, len(fonds) - 1)
                fond_choisi = fonds[fond_index]

            elif souris == 'bot':
                en_jeu = True
                mode_bot = True
                vie1 = 100
                vie2 = 100
                projectiles1 = []
                projectiles2 = []
                projectiles_bot = []
                bots = creer_bots(niveau)
                h1, h2 = 100, 200
                h3, h4 = 800, 200
                retourne = False
                niveau = 1
                fond_index = random.randint(0, len(fonds) - 1)
                fond_choisi = fonds[fond_index]

        if mort and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if souris == 'rejouer':
                en_jeu = True
                mort = False
                projectiles1 = []
                projectiles2 = []
                projectiles_bot = []
                if mode_bot:
                    niveau = 1
                    bots = creer_bots(niveau)
                else:
                    bots = []
                vie1 = 100
                vie2 = 100
                h1, h2 = 100, 200
                h3, h4 = 800, 200
                retourne = False
                fond_index = random.randint(0, len(fonds) - 1)
                fond_choisi = fonds[fond_index]
            elif souris == 'menu':
                mort = False
                en_jeu = False
                mode_bot = False
                niveau = 1
                vie1 = 100
                vie2 = 100
                retourne = False

    if not en_jeu and not mort:
        fenetre.fill((0, 0, 0))
        titre = arial48.render("WELCOME TO GALAXI !", True, (0, 255, 255))
        fenetre.blit(titre, (220, 100))

        if souris == '1v1':
            pygame.draw.rect(fenetre, (255, 0, 0), rect1)  
            
        else:
            pygame.draw.rect(fenetre, (0, 255, 255), rect1)  
        pygame.draw.rect(fenetre, (0, 0, 0), rect1.inflate(-20, -20))

        if souris == 'bot':
            pygame.draw.rect(fenetre, (255, 0, 0), rect2)
        else:
            pygame.draw.rect(fenetre, (0, 255, 255), rect2)  
        pygame.draw.rect(fenetre, (0, 0, 0), rect2.inflate(-20, -20))

        fenetre.blit(arial48.render("1v1", True, (0, 255, 255)), (220, 310))
        fenetre.blit(arial48.render("bot", True, (0, 255, 255)), (720, 310))

        for etoile in etoiles:
            pygame.draw.circle(fenetre, (255, 255, 255), etoile, 2)
        for k in range(len(etoiles)):
            etoiles[k] = (etoiles[k][0], (etoiles[k][1] + 2) % 500)
        pygame.display.flip()

    elif mort:
        fenetre.fill((0, 0, 0))
        titre = arial48.render("Tu as perdu ! ", True, (255, 0, 0))
        niveau_text = arial36.render(f"Niveau atteint : {niveau}", True, (0, 255, 255))
        record_text = arial36.render(f"Record : {record}", True, (0, 255, 255))
        fenetre.blit(titre, (500 - titre.get_width() // 2, 25))
        fenetre.blit(niveau_text, (300 - niveau_text.get_width() // 2, 120))
        fenetre.blit(record_text, (700 - record_text.get_width() // 2, 120))

        if souris == 'rejouer':
            pygame.draw.rect(fenetre, (255, 0, 0), rect_rejouer, border_radius=5)
            fenetre.blit(arial36.render("Rejouer", True, (255, 0, 0)), (435, 255))  
        else:
            pygame.draw.rect(fenetre, (0, 255, 255), rect_rejouer, border_radius=5)  
        pygame.draw.rect(fenetre, (0, 0, 0), rect_rejouer.inflate(-20, -20), border_radius=5)

        if souris == 'menu':
            pygame.draw.rect(fenetre, (255, 0, 0), rect_menu, border_radius=10)  
            fenetre.blit(arial36.render("Menu", True, (255, 0, 0)), (455, 340))
        else:
            pygame.draw.rect(fenetre, (0, 255, 255), rect_menu, border_radius=10)  
        pygame.draw.rect(fenetre, (0, 0, 0), rect_menu.inflate(-20, -20), border_radius=10)

        fenetre.blit(arial36.render("Rejouer", True, (0, 255, 255)), (435, 255))
        fenetre.blit(arial36.render("Menu", True, (0, 255, 255)), (455, 340))

        for etoile1 in etoiles1:
            pygame.draw.circle(fenetre, (255, 255, 255), etoile1, 2)
        for k in range(len(etoiles1)):
            etoiles1[k] = (etoiles1[k][0], (etoiles1[k][1] + 2) % 500)
        pygame.display.flip()

    else:
        if en_jeu:
            if fond_choisi:
                fenetre.blit(fond_choisi, (0, 0))

            if not pause:
                touches = pygame.key.get_pressed()

                couleur_projectile = (255, 255, 255)
                if fond_index == 1:
                    couleur_projectile = (0, 0, 0)

                if mode_bot:
                    if touches[pygame.K_z] and h2 > 0:
                        h2 -= 3
                    if touches[pygame.K_s] and h2 < 450:
                        h2 += 3
                    if touches[pygame.K_q] and h1 > 0:
                        h1 -= 3
                    if touches[pygame.K_d] and h1 < 950:
                        h1 += 3

                    if not touches[pygame.K_SPACE]:
                        appui1 = False
                    if touches[pygame.K_SPACE] and not appui1:
                        projectiles1.append([h1 + 25, h2 + 25, 5, 0])
                        if tir:
                            tir.play()
                        appui1 = True

                    for p in projectiles1[:]:
                        p[0] += p[2]
                        p[1] += p[3]
                        if p[0] > 1000 or p[0] < 0 or p[1] < 0 or p[1] > 500:
                            projectiles1.remove(p)

                    for p in projectiles_bot[:]:
                        p[0] += p[2]
                        p[1] += p[3]
                        if p[0] > 1000 or p[0] < 0 or p[1] < 0 or p[1] > 500:
                            projectiles_bot.remove(p)

                    for bot in bots:
                        bot.deplacer()
                        tir_bot = bot.tirer()
                        if tir_bot:
                            projectiles_bot.append(tir_bot)
                            if tir:
                                tir.play()

                    projectiles1, projectiles_bot = annuler_projectiles(projectiles1, projectiles_bot)

                    for p in projectiles_bot[:]:
                        if pygame.Rect(h1, h2, 50, 50).collidepoint(p[0], p[1]):
                            vie1 -= 10
                            if impact:
                                impact.play()
                            projectiles_bot.remove(p)

                    for bot in bots[:]:
                        for p in projectiles1[:]:
                            if pygame.Rect(bot.x, bot.y, 50, 50).colliderect(p[0], p[1], 8, 8):
                                bot.vie -= 1
                                projectiles1.remove(p)
                                if impact:
                                    impact.play()
                                if bot.vie <= 0:
                                    if explosion:
                                        explosion.play()
                                    bots.remove(bot)
                                break

                    if vie1 <= 0:
                        en_jeu = False
                        mort = True
                        if niveau > record:
                            record = niveau
                            try:
                                with open("record.txt", "w") as f:
                                    f.write(str(record))
                            except:
                                pass

                    if not bots:
                        niveau += 1
                        bots = creer_bots(niveau)

                    fenetre.blit(v1_retourne if retourne else v1, (h1, h2))

                    for bot in bots:
                        img = bot_image_droite if bot.dir_droite else bot_image_gauche
                        fenetre.blit(img, (bot.x, bot.y))
                        pygame.draw.rect(fenetre, (255, 0, 0), (bot.x, bot.y - 10, 50, 5))
                        pygame.draw.rect(fenetre, (0, 255, 0), (bot.x, bot.y - 10, bot.vie / 3 * 50, 5))

                    for p in projectiles1:
                        pygame.draw.circle(fenetre, couleur_projectile, (int(p[0]), int(p[1])), 5)
                    for p in projectiles_bot:
                        pygame.draw.circle(fenetre, couleur_projectile, (int(p[0]), int(p[1])), 5)

                    pygame.draw.rect(fenetre, (255, 0, 0), (20, 20, 100, 10))
                    pygame.draw.rect(fenetre, (0, 255, 0), (20, 20, vie1, 10))

                    if croix is None and random.random() < 0.1:
                        croix = Croix()
                    elif croix:
                        croix.timer += 1
                        if croix.timer > 1000:
                            croix = None

                    if croix:
                        joueur1_rect = pygame.Rect(h1, h2, 50, 50)
                        joueur2_rect = None
                        if mode_bot:
                            if bots:
                                mx = sum(bot.x for bot in bots) // len(bots)
                                my = sum(bot.y for bot in bots) // len(bots)
                                joueur2_rect = pygame.Rect(mx, my, 50, 50)
                        else:
                            joueur2_rect = pygame.Rect(h3, h4, 50, 50)
                        croix_rect = pygame.Rect(croix.x - 5, croix.y - 5, 10, 10)

                        if joueur1_rect.colliderect(croix_rect):
                            vie1 = min(100, vie1 + 20)
                            if vie:
                                vie.play()
                            croix = None
                        elif joueur2_rect and joueur2_rect.colliderect(croix_rect):
                            vie2 = min(100, vie2 + 20)
                            if vie:
                                vie.play()
                            croix = None

                    if croix:
                        croix.dessiner(fenetre)

                else:
                    touches = pygame.key.get_pressed()

                    if touches[pygame.K_z] and h2 > 0:
                        h2 -= 3
                    if touches[pygame.K_s] and h2 < 450:
                        h2 += 3
                    if touches[pygame.K_q] and h1 > 0:
                        h1 -= 3
                    if touches[pygame.K_d] and h1 < 950:
                        h1 += 3

                    if not touches[pygame.K_SPACE]:
                        appui1 = False
                    if touches[pygame.K_SPACE] and not appui1:
                        projectiles1.append([h1 + 25, h2 + 25, 5, 0])
                        if tir:
                            tir.play()
                        appui1 = True

                    if touches[pygame.K_UP] and h4 > 0:
                        h4 -= 3
                    if touches[pygame.K_DOWN] and h4 < 450:
                        h4 += 3
                    if touches[pygame.K_LEFT] and h3 > 0:
                        h3 -= 3
                    if touches[pygame.K_RIGHT] and h3 < 950:
                        h3 += 3

                    if not touches[pygame.K_m]:
                        appui2 = False
                    if touches[pygame.K_m] and not appui2:
                        projectiles2.append([h3 - 25, h4 + 25, -5, 0])
                        if tir:
                            tir.play()
                        appui2 = True

                    for p in projectiles1[:]:
                        p[0] += p[2]
                        p[1] += p[3]
                        if p[0] > 1000 or p[0] < 0 or p[1] < 0 or p[1] > 500:
                            projectiles1.remove(p)

                    for p in projectiles2[:]:
                        p[0] += p[2]
                        p[1] += p[3]
                        if p[0] > 1000 or p[0] < 0 or p[1] < 0 or p[1] > 500:
                            projectiles2.remove(p)

                    projectiles1, projectiles2 = annuler_projectiles(projectiles1, projectiles2)

                    for p in projectiles2[:]:
                        if pygame.Rect(h1, h2, 50, 50).collidepoint(p[0], p[1]):
                            vie1 -= 10
                            if impact:
                                impact.play()
                            projectiles2.remove(p)

                    for p in projectiles1[:]:
                        if pygame.Rect(h3, h4, 50, 50).collidepoint(p[0], p[1]):
                            vie2 -= 10
                            if impact:
                                impact.play()
                            projectiles1.remove(p)

                    if vie1 <= 0 or vie2 <= 0:
                        en_jeu = False
                        mort = True
                        if niveau > record:
                            record = niveau
                            try:
                                with open("record.txt", "w") as f:
                                    f.write(str(record))
                            except:
                                pass

                    fenetre.blit(v1_retourne if retourne else v1, (h1, h2))
                    fenetre.blit(v2, (h3, h4))

                    for p in projectiles1:
                        pygame.draw.circle(fenetre, couleur_projectile, (int(p[0]), int(p[1])), 5)
                    for p in projectiles2:
                        pygame.draw.circle(fenetre, couleur_projectile, (int(p[0]), int(p[1])), 5)

                    pygame.draw.rect(fenetre, (255, 0, 0), (20, 20, 100, 10))
                    pygame.draw.rect(fenetre, (0, 255, 0), (20, 20, vie1, 10))
                    pygame.draw.rect(fenetre, (255, 0, 0), (880, 20, 100, 10))
                    pygame.draw.rect(fenetre, (0, 255, 0), (880, 20, vie2, 10))

                    if croix:
                        croix.dessiner(fenetre)

            pygame.display.flip()

    clock.tick(60)

