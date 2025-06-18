import pygame
import sys
import math
import random
import os
from pygame.locals import *


pygame.init()
pygame.mixer.init()

KEZELO_SZELESSEG, KEZELO_MAGASSAG = 1000, 700
kepernyo = pygame.display.set_mode((KEZELO_SZELESSEG, KEZELO_MAGASSAG))
pygame.display.set_caption("Bug Dungeon - Debug Your Way to Victory")

HATTER = (20, 12, 36)
PANEL_HATTER = (30, 22, 46)
SZOVEG_SZIN = (220, 220, 255)
KIHANGSULY = (101, 223, 171)
GOMB_SZIN = (72, 52, 112)
GOMB_RAJTA = (92, 72, 142)
SZORNY_SZIN = (200, 60, 60)
KULCS_SZIN = (255, 215, 0)
FAL_SZIN = (60, 40, 80)
PADLO_SZIN = (90, 70, 110)
AJTO_SZIN = (150, 120, 80)
KURZOR_SZIN = (255, 255, 255)

cim_font = pygame.font.SysFont("Courier", 48, bold=True)
fejlec_font = pygame.font.SysFont("Courier", 32, bold=True)
fo_font = pygame.font.SysFont("Courier", 24)
kis_font = pygame.font.SysFont("Courier", 18)

MENU = 0
TORTENET = 1
TERKEP = 2
SZOBA = 3
REJTVENY = 4
GYOZELEM = 5
jelenlegi_allapot = MENU
jatekos_helyzete = [1, 1]
latogatott_szobak = set()
teljesitett_szobak = set()
szorny_eletero = 0
jatekos_kulcsok = 0
teljes_kepernyo = False
zene_mehet = False
jelenlegi_szam = None
tortenet_gorgeto_poz = 0
kurzor_latszik = True
kurzor_idozito = 0

# Fix image loading - use relative paths
szorny_kepek = {}
helyettesito = pygame.Surface((100, 100))
helyettesito.fill((200, 0, 0))
pygame.draw.circle(helyettesito, (0, 0, 200), (50, 50), 40)

monster_nevek = ["Syntax Serpent", "Infinite Loop Spider", "Null Pointer Gremlin", 
                "Memory Leak Ooze", "The Kernel Kraken"]
for nev in monster_nevek:
    szorny_kepek[nev] = helyettesito.copy()

barlang_terkep = [
    [0, 0, 0, 0, 0, 0, 0],
    [0, 1, 1, 2, 1, 3, 0],
    [0, 2, 0, 1, 0, 2, 0],
    [0, 1, 1, 2, 3, 1, 0],
    [0, 3, 0, 1, 0, 4, 0],
    [0, 1, 2, 1, 2, 1, 0],
    [0, 0, 0, 0, 0, 0, 0]
]

szoba_tipusok = {
    1: "Empty Chamber",
    2: "Monster Lair",
    3: "Treasure Vault",
    4: "Boss Arena"
}

szornyek = [
    {"name": "Syntax Serpent", "health": 3, "strength": "Caesar Cipher", "art": """
  /^\\/^\\
 _|_O|  |_     Syntax Serpent
\/     \/     Hiss... I'll wrap around your code!
 \     /      Weakness: Shift ciphers
  \   /
   \ /
"""},
    {"name": "Infinite Loop Spider", "health": 4, "strength": "Complex Logic", "art": """
   /\\ _ /\\
  /  ' '  \\   Infinite Loop Spider
 (   >.<   )  I'll trap you in my web!
  \\  =v=  /   Weakness: Loop breakers
   \\_____/
"""},
    {"name": "Null Pointer Gremlin", "health": 2, "strength": "Unexpected Errors", "art": """
   (o   o)
  (   ^   )  Null Pointer Gremlin
 (  <(_)> )  I'll crash your programs!
  (       )  Weakness: Defensive checks
"""},
    {"name": "Memory Leak Ooze", "health": 5, "strength": "Resource Drain", "art": """
   .-~~~~~-.
  {         }  Memory Leak Ooze
  |  o   o |   I'll consume your RAM!
  \   ---   /  Weakness: Garbage collection
   '~~~~~~~'
"""},
    {"name": "The Kernel Kraken", "health": 10, "strength": "System-Level Attacks", "art": """
    .-~~~-.
   {       }
   |  O O  |  The Kernel Kraken
   \   W   /  I control the depths!
    '-----'   Weakness: Root access
"""}
]

tortenet_szoveg = [
    "In the forgotten depths of the digital realm,",
    "lies the Bug Dungeon - home to malicious code",
    "creatures that corrupt programs and crash systems.",
    "",
    "You are a Debug Mage, armed with the arcane",
    "art of code manipulation. Your mission:",
    "",
    "1. Navigate the dungeon map",
    "2. Battle bug monsters with code puzzles",
    "3. Collect keys to access new areas",
    "4. Defeat the Kernel Kraken in the final chamber",
    "",
    "Each monster guards a cipher puzzle. Solve it",
    "by writing or fixing code to vanquish the creature.",
    "",
    "Game Controls:",
    "  - Arrow keys: Move on map",
    "  - SPACE: Interact with rooms",
    "  - ENTER: Test code in puzzles",
    "  - Mouse: Click buttons and select code lines",
    "  - F11: Toggle fullscreen",
    "  - Scroll wheel: Scroll through text",
    "",
    "Puzzle Solving Tips:",
    "  - Read the puzzle description carefully",
    "  - Look at the expected output format",
    "  - Test your code frequently with ENTER",
    "  - Successful solutions damage monsters",
    "",
    "Monster Weaknesses:",
    "  - Syntax Serpent: Caesar cipher shifts",
    "  - Infinite Loop Spider: Loop breakers",
    "  - Null Pointer Gremlin: Defensive checks",
    "  - Memory Leak Ooze: Garbage collection",
    "  - Kernel Kraken: Root access techniques",
    "",
    "Press any key to continue..."
]

rejtvenyek = [
    {
        "name": "Rot13 Cipher",
        "description": "A classic ROT13 cipher was used. Apply ROT13 again to decrypt it.",
        "ciphertext": "FRNCE",
        "expected": "SPEAR",
        "code": [
            "def decrypt(msg):",
            "    result = ''",
            "    for char in msg:",
            "        if char.isalpha():",
            "            base = ord('A') if char.isupper() else ord('a')",
            "            result += chr((ord(char) - base + 13) % 26 + base)",
            "        else:",
            "            result += char",
            "    return result"
        ],
        "error": "ROT13 decryption incorrect"
    },
    {
        "name": "Reverse Cipher",
        "description": "The message has been reversed. Flip it back to read the key name.",
        "ciphertext": "NREVAT",
        "expected": "TAVERN",
        "code": [
            "def decrypt(msg):",
            "    return msg[::-1]"
        ],
        "error": "String not reversed correctly"
    },
    {
        "name": "Number Substitution",
        "description": "Each letter has been substituted with its alphabetical index (A=1, B=2, ..., Z=26). Convert the numbers back to letters.",
        "ciphertext": "3 18 25 16 20",
        "expected": "CRYPT",
        "code": [
            "def decrypt(msg):",
            "    parts = msg.split()",
            "    result = ''",
            "    for num in parts:",
            "        result += chr(int(num) + 64)",
            "    return result"
        ],
        "error": "Number to letter conversion failed"
    }
]

jelenlegi_rejtveny = None
jelenlegi_szorny = None
felhasznalo_kodja = []
kivalasztott_sor = 0
kurzor_x = 0
eredmeny_uzenet = ""
rejtveny_megoldva = False

class Gomb:
    def __init__(self, x, y, szelesseg, magassag, szoveg, muvelet=None):
        self.teglalap = pygame.Rect(x, y, szelesseg, magassag)
        self.szoveg = szoveg
        self.muvelet = muvelet
        self.rajta = False
        self.latszik = True
        
    def rajzol(self, felulet):
        if not self.latszik:
            return
            
        szin = GOMB_RAJTA if self.rajta else GOMB_SZIN
        pygame.draw.rect(felulet, szin, self.teglalap, border_radius=8)
        pygame.draw.rect(felulet, KIHANGSULY, self.teglalap, 2, border_radius=8)
        
        szoveg_felulet = fo_font.render(self.szoveg, True, SZOVEG_SZIN)
        szoveg_teglalap = szoveg_felulet.get_rect(center=self.teglalap.center)
        felulet.blit(szoveg_felulet, szoveg_teglalap)
        
    def rajta_van(self, poz):
        if not self.latszik:
            return
        self.rajta = self.teglalap.collidepoint(poz)
        
    def kezeles(self, esemeny):
        if not self.latszik:
            return False
            
        if esemeny.type == MOUSEBUTTONDOWN and esemeny.button == 1:
            if self.rajta and self.muvelet:
                self.muvelet()
                return True
        return False

indito_gomb = Gomb(KEZELO_SZELESSEG//2 - 100, KEZELO_MAGASSAG//2 + 50, 200, 50, "START GAME")
tortenet_gomb = Gomb(KEZELO_SZELESSEG//2 - 100, KEZELO_MAGASSAG//2 + 120, 200, 50, "HOW TO PLAY")
terkep_gomb = Gomb(KEZELO_SZELESSEG//2 - 100, KEZELO_MAGASSAG - 100, 200, 50, "BACK TO MAP")
teljes_kepernyo_gomb = Gomb(KEZELO_SZELESSEG - 200, 20, 180, 40, "TOGGLE FULLSCREEN")
zene_gomb = Gomb(KEZELO_SZELESSEG - 200, 70, 180, 40, "MUSIC: OFF")
vissza_menu_gomb = Gomb(KEZELO_SZELESSEG//2 - 100, KEZELO_MAGASSAG - 100, 200, 50, "BACK TO MENU")
teszt_kod_gomb = Gomb(KEZELO_SZELESSEG//2 - 100, KEZELO_MAGASSAG - 150, 200, 50, "TEST CODE")

def menu_rajzol():
    kepernyo.fill(HATTER)
    
    cim = cim_font.render("BUG DUNGEON", True, KIHANGSULY)
    alcim = fejlec_font.render("Debug Your Way to Victory", True, SZOVEG_SZIN)
    kepernyo.blit(cim, (KEZELO_SZELESSEG//2 - cim.get_width()//2, KEZELO_MAGASSAG//4))
    kepernyo.blit(alcim, (KEZELO_SZELESSEG//2 - alcim.get_width()//2, KEZELO_MAGASSAG//4 + 70))
    
    pygame.draw.line(kepernyo, KIHANGSULY, (KEZELO_SZELESSEG//2 - 150, KEZELO_MAGASSAG//4 + 120), (KEZELO_SZELESSEG//2 + 150, KEZELO_MAGASSAG//4 + 120), 2)
    
    indito_gomb.latszik = True
    tortenet_gomb.latszik = True
    teljes_kepernyo_gomb.latszik = True
    zene_gomb.latszik = True
    terkep_gomb.latszik = False
    vissza_menu_gomb.latszik = False
    
    indito_gomb.rajzol(kepernyo)
    tortenet_gomb.rajzol(kepernyo)
    teljes_kepernyo_gomb.rajzol(kepernyo)
    zene_gomb.rajzol(kepernyo)
    
    karakter_x, karakter_y = KEZELO_SZELESSEG//2, KEZELO_MAGASSAG//4 - 120
    pygame.draw.circle(kepernyo, (80, 160, 240), (karakter_x, karakter_y), 40)
    pygame.draw.rect(kepernyo, (60, 140, 220), (karakter_x-30, karakter_y+40, 60, 80))
    pygame.draw.line(kepernyo, (60, 140, 220), (karakter_x-30, karakter_y+80), (karakter_x-50, karakter_y+140), 5)
    pygame.draw.line(kepernyo, (60, 140, 220), (karakter_x+30, karakter_y+80), (karakter_x+50, karakter_y+140), 5)
    pygame.draw.circle(kepernyo, (200, 200, 100), (karakter_x, karakter_y+30), 10)
    
    pygame.draw.line(kepernyo, (200, 180, 100), (karakter_x, karakter_y+40), (karakter_x, karakter_y+120), 5)

def tortenet_rajzol():
    global tortenet_gorgeto_poz
    
    kepernyo.fill(HATTER)
    
    cim = cim_font.render("THE BUG DUNGEON", True, KIHANGSULY)
    kepernyo.blit(cim, (KEZELO_SZELESSEG//2 - cim.get_width()//2, 40))
    
    tortenet_felulet = pygame.Surface((KEZELO_SZELESSEG, len(tortenet_szoveg) * 40 + 100))
    tortenet_felulet.fill(HATTER)
    
    y_poz = 40
    for sor in tortenet_szoveg:
        szoveg = fo_font.render(sor, True, SZOVEG_SZIN)
        tortenet_felulet.blit(szoveg, (KEZELO_SZELESSEG//2 - szoveg.get_width()//2, y_poz))
        y_poz += 40
    
    max_gorgetes = max(0, tortenet_felulet.get_height() - (KEZELO_MAGASSAG - 200))
    tortenet_gorgeto_poz = max(0, min(tortenet_gorgeto_poz, max_gorgetes))
    
    kepernyo.blit(tortenet_felulet, (0, 80), (0, tortenet_gorgeto_poz, KEZELO_SZELESSEG, KEZELO_MAGASSAG - 200))
    
    if max_gorgetes > 0:
        gorgeto_magassag = (KEZELO_MAGASSAG - 200) * (KEZELO_MAGASSAG - 200) // tortenet_felulet.get_height()
        gorgeto_poz = (KEZELO_MAGASSAG - 120) * tortenet_gorgeto_poz // max_gorgetes
        gorgeto_teglalap = pygame.Rect(KEZELO_SZELESSEG - 20, 80 + gorgeto_poz, 10, gorgeto_magassag)
        pygame.draw.rect(kepernyo, KIHANGSULY, gorgeto_teglalap, border_radius=5)
    
    vissza_menu_gomb.latszik = True
    vissza_menu_gomb.rajzol(kepernyo)
    
    if max_gorgetes > 0:
        tipp = kis_font.render("Use mouse wheel to scroll", True, KIHANGSULY)
        kepernyo.blit(tipp, (KEZELO_SZELESSEG//2 - tipp.get_width()//2, KEZELO_MAGASSAG - 40))

def terkep_rajzol():
    kepernyo.fill(HATTER)
    
    cim = cim_font.render("DUNGEON MAP", True, KIHANGSULY)
    kepernyo.blit(cim, (KEZELO_SZELESSEG//2 - cim.get_width()//2, 20))
    
    kulcs_szoveg = fo_font.render(f"Keys: {jatekos_kulcsok}", True, KULCS_SZIN)
    szobak_szoveg = fo_font.render(f"Rooms Cleared: {len(teljesitett_szobak)}/12", True, SZOVEG_SZIN)
    kepernyo.blit(kulcs_szoveg, (30, 30))
    kepernyo.blit(szobak_szoveg, (KEZELO_SZELESSEG - szobak_szoveg.get_width() - 30, 30))
    
    cella_meret = 70
    terkep_szelesseg = len(barlang_terkep[0]) * cella_meret
    terkep_magassag = len(barlang_terkep) * cella_meret
    terkep_x = (KEZELO_SZELESSEG - terkep_szelesseg) // 2
    terkep_y = (KEZELO_MAGASSAG - terkep_magassag) // 2 + 20
    
    for y, sor in enumerate(barlang_terkep):
        for x, cella in enumerate(sor):
            teglalap = pygame.Rect(terkep_x + x * cella_meret, terkep_y + y * cella_meret, cella_meret, cella_meret)
            
            if cella == 0:
                pygame.draw.rect(kepernyo, FAL_SZIN, teglalap)
                pygame.draw.rect(kepernyo, (40, 30, 60), teglalap, 2)
            else:
                szoba_szin = PADLO_SZIN
                if (x, y) in teljesitett_szobak:
                    szoba_szin = (70, 150, 70)
                pygame.draw.rect(kepernyo, szoba_szin, teglalap, border_radius=8)
                pygame.draw.rect(kepernyo, (120, 100, 140), teglalap, 2, border_radius=8)
                
                if cella == 2:
                    pygame.draw.circle(kepernyo, SZORNY_SZIN, teglalap.center, 15)
                elif cella == 3:
                    pygame.draw.circle(kepernyo, KULCS_SZIN, teglalap.center, 15)
                elif cella == 4:
                    pygame.draw.circle(kepernyo, (200, 40, 40), teglalap.center, 18)
                    pygame.draw.circle(kepernyo, (240, 180, 40), teglalap.center, 10)
            
            if [x, y] == jatekos_helyzete:
                pygame.draw.circle(kepernyo, KIHANGSULY, teglalap.center, 10)
                pygame.draw.circle(kepernyo, (40, 180, 240), teglalap.center, 6)
    
    kulcso_x = 50
    kulcso_y = KEZELO_MAGASSAG - 180
    pygame.draw.rect(kepernyo, PANEL_HATTER, (kulcso_x-10, kulcso_y-10, 250, 170), border_radius=10)
    kulcso_cim = fejlec_font.render("Map Key", True, KIHANGSULY)
    kepernyo.blit(kulcso_cim, (kulcso_x + 125 - kulcso_cim.get_width()//2, kulcso_y))
    
    kulcso_y += 50
    pygame.draw.circle(kepernyo, KIHANGSULY, (kulcso_x, kulcso_y), 8)
    kepernyo.blit(kis_font.render("Player", True, SZOVEG_SZIN), (kulcso_x + 20, kulcso_y-10))
    
    kulcso_y += 30
    pygame.draw.circle(kepernyo, SZORNY_SZIN, (kulcso_x, kulcso_y), 8)
    kepernyo.blit(kis_font.render("Monster Room", True, SZOVEG_SZIN), (kulcso_x + 20, kulcso_y-10))
    
    kulcso_y += 30
    pygame.draw.circle(kepernyo, KULCS_SZIN, (kulcso_x, kulcso_y), 8)
    kepernyo.blit(kis_font.render("Treasure Room", True, SZOVEG_SZIN), (kulcso_x + 20, kulcso_y-10))
    
    kulcso_y += 30
    pygame.draw.circle(kepernyo, (200, 40, 40), (kulcso_x, kulcso_y), 10)
    pygame.draw.circle(kepernyo, (240, 180, 40), (kulcso_x, kulcso_y), 5)
    kepernyo.blit(kis_font.render("Boss Room", True, SZOVEG_SZIN), (kulcso_x + 20, kulcso_y-10))
    
    terkep_gomb.latszik = True
    teljes_kepernyo_gomb.latszik = True
    zene_gomb.latszik = True
    terkep_gomb.rajzol(kepernyo)
    teljes_kepernyo_gomb.rajzol(kepernyo)
    zene_gomb.rajzol(kepernyo)

def szoba_rajzol():
    kepernyo.fill(HATTER)
    
    x, y = jatekos_helyzete
    szoba_tipus = barlang_terkep[y][x]
    szoba_nev = szoba_tipusok.get(szoba_tipus, "Unknown Room")
    
    cim = cim_font.render(szoba_nev, True, KIHANGSULY)
    kepernyo.blit(cim, (KEZELO_SZELESSEG//2 - cim.get_width()//2, 20))
    
    tartalom_teglalap = pygame.Rect(50, 80, KEZELO_SZELESSEG-100, KEZELO_MAGASSAG-180)
    pygame.draw.rect(kepernyo, PANEL_HATTER, tartalom_teglalap, border_radius=12)
    pygame.draw.rect(kepernyo, (80, 60, 100), tartalom_teglalap, 3, border_radius=12)
    
    if szoba_tipus == 1:
        ures_szoba_rajzol(tartalom_teglalap)
    elif szoba_tipus == 2:
        szorny_szoba_rajzol(tartalom_teglalap)
    elif szoba_tipus == 3:
        kulcs_szoba_rajzol(tartalom_teglalap)
    elif szoba_tipus == 4:
        fonok_szoba_rajzol(tartalom_teglalap)
    
    terkep_gomb.latszik = True
    teljes_kepernyo_gomb.latszik = True
    zene_gomb.latszik = True
    terkep_gomb.rajzol(kepernyo)
    teljes_kepernyo_gomb.rajzol(kepernyo)
    zene_gomb.rajzol(kepernyo)

def ures_szoba_rajzol(teglalap):
    cim = fejlec_font.render("Empty Chamber", True, SZOVEG_SZIN)
    kepernyo.blit(cim, (teglalap.x + teglalap.width//2 - cim.get_width()//2, teglalap.y + 20))
    
    leiras = fo_font.render("This room appears to be empty.", True, SZOVEG_SZIN)
    kepernyo.blit(leiras, (teglalap.x + teglalap.width//2 - leiras.get_width()//2, teglalap.y + 80))
    
    leiras2 = fo_font.render("No monsters or treasure here.", True, SZOVEG_SZIN)
    kepernyo.blit(leiras2, (teglalap.x + teglalap.width//2 - leiras2.get_width()//2, teglalap.y + 120))
    
    pygame.draw.rect(kepernyo, FAL_SZIN, (teglalap.x + 100, teglalap.y + 180, teglalap.width - 200, 150), border_radius=10)
    
    for i in range(3):
        halox = teglalap.x + 150 + i * 200
        haloy = teglalap.y + 220
        pygame.draw.line(kepernyo, (180, 180, 200), (halox, haloy), (halox-20, haloy-30), 2)
        pygame.draw.line(kepernyo, (180, 180, 200), (halox, haloy), (halox+20, haloy-30), 2)
        pygame.draw.line(kepernyo, (180, 180, 200), (halox, haloy), (halox, haloy+40), 2)
        pygame.draw.circle(kepernyo, (180, 180, 200), (halox, haloy), 20, 1)
    
    muvelet_szoveg = fo_font.render("Press SPACE to continue exploring", True, KIHANGSULY)
    kepernyo.blit(muvelet_szoveg, (teglalap.x + teglalap.width//2 - muvelet_szoveg.get_width()//2, teglalap.y + teglalap.height - 60))

def szorny_szoba_rajzol(teglalap):
    global jelenlegi_szorny
    
    if not jelenlegi_szorny:
        elerheto_szornyek = [s for s in szornyek if s["name"] not in teljesitett_szobak]
        if elerheto_szornyek:
            jelenlegi_szorny = random.choice(elerheto_szornyek)
        else:
            jelenlegi_szorny = szornyek[-1]
    
    cim = fejlec_font.render(jelenlegi_szorny["name"], True, SZORNY_SZIN)
    kepernyo.blit(cim, (teglalap.x + teglalap.width//2 - cim.get_width()//2, teglalap.y + 20))
    
    pygame.draw.rect(kepernyo, (60, 20, 20), (teglalap.x + 150, teglalap.y + 70, teglalap.width - 300, 25))
    eletero_szelesseg = max(0, (teglalap.width - 300) * jelenlegi_szorny["health"] / 10)
    pygame.draw.rect(kepernyo, SZORNY_SZIN, (teglalap.x + 150, teglalap.y + 70, eletero_szelesseg, 25))
    eletero_szoveg = fo_font.render(f"Health: {jelenlegi_szorny['health']}/10", True, SZOVEG_SZIN)
    kepernyo.blit(eletero_szoveg, (teglalap.x + teglalap.width//2 - eletero_szoveg.get_width()//2, teglalap.y + 75))
    
    if jelenlegi_szorny["name"] in szorny_kepek:
        szorny_kep = szorny_kepek[jelenlegi_szorny["name"]]
        kep_teglalap = szorny_kep.get_rect(center=(teglalap.centerx, teglalap.centery - 20))
        kepernyo.blit(szorny_kep, kep_teglalap)
    
    erosseg = fo_font.render(f"Strength: {jelenlegi_szorny['strength']}", True, (220, 150, 150))
    kepernyo.blit(erosseg, (teglalap.x + teglalap.width//2 - erosseg.get_width()//2, teglalap.y + teglalap.height - 120))
    
    if (jatekos_helyzete[0], jatekos_helyzete[1]) in teljesitett_szobak:
        muvelet_szoveg = fo_font.render("Monster defeated! Press SPACE to leave", True, KIHANGSULY)
    else:
        muvelet_szoveg = fo_font.render("Press SPACE to battle the monster", True, KIHANGSULY)
    kepernyo.blit(muvelet_szoveg, (teglalap.x + teglalap.width//2 - muvelet_szoveg.get_width()//2, teglalap.y + teglalap.height - 60))

def kulcs_szoba_rajzol(teglalap):
    cim = fejlec_font.render("Treasure Vault", True, KULCS_SZIN)
    kepernyo.blit(cim, (teglalap.x + teglalap.width//2 - cim.get_width()//2, teglalap.y + 20))
    
    pygame.draw.rect(kepernyo, (150, 100, 50), (teglalap.centerx - 60, teglalap.y + 100, 120, 70), border_radius=10)
    pygame.draw.rect(kepernyo, (180, 140, 60), (teglalap.centerx - 50, teglalap.y + 110, 100, 50))
    pygame.draw.arc(kepernyo, (150, 100, 50), (teglalap.centerx - 60, teglalap.y + 70, 120, 60), 0, math.pi, 5)
    
    if (jatekos_helyzete[0], jatekos_helyzete[1]) not in teljesitett_szobak:
        pygame.draw.rect(kepernyo, KULCS_SZIN, (teglalap.centerx - 40, teglalap.y + 140, 80, 10), border_radius=5)
        pygame.draw.circle(kepernyo, KULCS_SZIN, (teglalap.centerx, teglalap.y + 130), 15)
        pygame.draw.rect(kepernyo, KULCS_SZIN, (teglalap.centerx - 5, teglalap.y + 130, 10, 20))
        
        muvelet_szoveg = fo_font.render("Press SPACE to collect the key", True, KIHANGSULY)
        kepernyo.blit(muvelet_szoveg, (teglalap.x + teglalap.width//2 - muvelet_szoveg.get_width()//2, teglalap.y + teglalap.height - 60))
    else:
        muvelet_szoveg = fo_font.render("Treasure collected! Press SPACE to leave", True, KIHANGSULY)
        kepernyo.blit(muvelet_szoveg, (teglalap.x + teglalap.width//2 - muvelet_szoveg.get_width()//2, teglalap.y + teglalap.height - 60))
    
    kulcsok_szoveg = fo_font.render(f"You have {jatekos_kulcsok} keys", True, KULCS_SZIN)
    kepernyo.blit(kulcsok_szoveg, (teglalap.x + teglalap.width//2 - kulcsok_szoveg.get_width()//2, teglalap.y + 220))

def fonok_szoba_rajzol(teglalap):
    fonok = szornyek[-1]
    
    cim = fejlec_font.render(fonok["name"], True, (200, 40, 40))
    kepernyo.blit(cim, (teglalap.x + teglalap.width//2 - cim.get_width()//2, teglalap.y + 20))
    
    pygame.draw.rect(kepernyo, (60, 20, 20), (teglalap.x + 100, teglalap.y + 70, teglalap.width - 200, 30))
    eletero_szelesseg = max(0, (teglalap.width - 200) * fonok["health"] / 10)
    pygame.draw.rect(kepernyo, (200, 40, 40), (teglalap.x + 100, teglalap.y + 70, eletero_szelesseg, 30))
    eletero_szoveg = fo_font.render(f"Health: {fonok['health']}/10", True, SZOVEG_SZIN)
    kepernyo.blit(eletero_szoveg, (teglalap.x + teglalap.width//2 - eletero_szoveg.get_width()//2, teglalap.y + 75))
    
    if fonok["name"] in szorny_kepek:
        szorny_kep = szorny_kepek[fonok["name"]]
        nagyitott_kep = pygame.transform.scale(szorny_kep, (150, 150))
        kep_teglalap = nagyitott_kep.get_rect(center=(teglalap.centerx, teglalap.centery - 20))
        kepernyo.blit(nagyitott_kep, kep_teglalap)
    
    erosseg = fo_font.render(f"Strength: {fonok['strength']}", True, (220, 100, 100))
    kepernyo.blit(erosseg, (teglalap.x + teglalap.width//2 - erosseg.get_width()//2, teglalap.y + teglalap.height - 120))
    
    if fonok["health"] <= 0:
        muvelet_szoveg = fo_font.render("BOSS DEFEATED! Press SPACE to claim victory", True, KIHANGSULY)
    elif jatekos_kulcsok < 3:
        muvelet_szoveg = fo_font.render(f"You need 3 keys to fight the boss ({jatekos_kulcsok}/3)", True, (200, 150, 50))
    else:
        muvelet_szoveg = fo_font.render("Press SPACE to battle the final boss", True, KIHANGSULY)
    kepernyo.blit(muvelet_szoveg, (teglalap.x + teglalap.width//2 - muvelet_szoveg.get_width()//2, teglalap.y + teglalap.height - 60))

def rejtveny_rajzol():
    global jelenlegi_rejtveny, kurzor_latszik, kurzor_x
    
    if not jelenlegi_rejtveny:
        jelenlegi_rejtveny = random.choice(rejtvenyek)
        felhasznalo_kodja[:] = jelenlegi_rejtveny["code"]
        kurzor_x = len(felhasznalo_kodja[kivalasztott_sor])
    
    kepernyo.fill(HATTER)
    
    cim = cim_font.render("CODE BATTLE", True, KIHANGSULY)
    kepernyo.blit(cim, (KEZELO_SZELESSEG//2 - cim.get_width()//2, 20))
    
    rejtveny_teglalap = pygame.Rect(50, 80, KEZELO_SZELESSEG-100, KEZELO_MAGASSAG-180)
    pygame.draw.rect(kepernyo, PANEL_HATTER, rejtveny_teglalap, border_radius=12)
    pygame.draw.rect(kepernyo, (80, 60, 100), rejtveny_teglalap, 3, border_radius=12)
    
    rejtveny_cim = fejlec_font.render(jelenlegi_rejtveny["name"], True, SZOVEG_SZIN)
    kepernyo.blit(rejtveny_cim, (rejtveny_teglalap.x + 20, rejtveny_teglalap.y + 20))
    
    titkos_szoveg = fo_font.render(f"Ciphertext: {jelenlegi_rejtveny['ciphertext']}", True, KIHANGSULY)
    kepernyo.blit(titkos_szoveg, (rejtveny_teglalap.x + 20, rejtveny_teglalap.y + 70))
    
    varhato_szoveg = fo_font.render(f"Expected: {jelenlegi_rejtveny['expected']}", True, KIHANGSULY)
    kepernyo.blit(varhato_szoveg, (rejtveny_teglalap.x + 20, rejtveny_teglalap.y + 110))
    
    leiras = kis_font.render(jelenlegi_rejtveny["description"], True, SZOVEG_SZIN)
    kepernyo.blit(leiras, (rejtveny_teglalap.x + 20, rejtveny_teglalap.y + 150))
    
    kod_teglalap = pygame.Rect(rejtveny_teglalap.x + 20, rejtveny_teglalap.y + 200, rejtveny_teglalap.width - 40, 200)
    pygame.draw.rect(kepernyo, (20, 15, 30), kod_teglalap)
    pygame.draw.rect(kepernyo, (60, 50, 80), kod_teglalap, 2)
    
    y_poz = kod_teglalap.y + 10
    for i, sor in enumerate(felhasznalo_kodja):
        szin = KIHANGSULY if i == kivalasztott_sor else SZOVEG_SZIN
        kod_sor = kis_font.render(sor, True, szin)
        kepernyo.blit(kod_sor, (kod_teglalap.x + 10, y_poz))
        
        if i == kivalasztott_sor and kurzor_latszik:
            prefix = sor[:kurzor_x]
            prefix_szelesseg = kis_font.size(prefix)[0]
            kurzor_teglalap = pygame.Rect(kod_teglalap.x + 10 + prefix_szelesseg, y_poz, 2, 20)
            pygame.draw.rect(kepernyo, KURZOR_SZIN, kurzor_teglalap)
        
        y_poz += 22
    
    eredmeny_szin = KIHANGSULY if rejtveny_megoldva else (220, 60, 60)
    eredmeny_szoveg = fo_font.render(eredmeny_uzenet, True, eredmeny_szin)
    kepernyo.blit(eredmeny_szoveg, (rejtveny_teglalap.x + 20, rejtveny_teglalap.y + 410))
    
    if rejtveny_megoldva:
        muvelet_szoveg = fo_font.render("Press SPACE to return and damage the monster", True, KIHANGSULY)
        kepernyo.blit(muvelet_szoveg, (rejtveny_teglalap.x + rejtveny_teglalap.width//2 - muvelet_szoveg.get_width()//2, 
                                rejtveny_teglalap.y + rejtveny_teglalap.height - 40))
    
    terkep_gomb.latszik = True
    teljes_kepernyo_gomb.latszik = True
    zene_gomb.latszik = True
    teszt_kod_gomb.latszik = True
    
    terkep_gomb.rajzol(kepernyo)
    teljes_kepernyo_gomb.rajzol(kepernyo)
    zene_gomb.rajzol(kepernyo)
    teszt_kod_gomb.rajzol(kepernyo)

def gyozelem_rajzol():
    kepernyo.fill(HATTER)
    
    cim = cim_font.render("VICTORY!", True, KULCS_SZIN)
    kepernyo.blit(cim, (KEZELO_SZELESSEG//2 - cim.get_width()//2, KEZELO_MAGASSAG//4))
    
    uzenet = fejlec_font.render("You have defeated the Kernel Kraken!", True, SZOVEG_SZIN)
    kepernyo.blit(uzenet, (KEZELO_SZELESSEG//2 - uzenet.get_width()//2, KEZELO_MAGASSAG//4 + 80))
    
    statisztikak = [
        f"Rooms Explored: {len(latogatott_szobak)}",
        f"Monsters Defeated: {len(teljesitett_szobak)}",
        f"Keys Collected: {jatekos_kulcsok}",
        "",
        "The Bug Dungeon has been cleansed of",
        "malicious code creatures... for now."
    ]
    
    y_poz = KEZELO_MAGASSAG//2
    for sor in statisztikak:
        szoveg = fo_font.render(sor, True, SZOVEG_SZIN)
        kepernyo.blit(szoveg, (KEZELO_SZELESSEG//2 - szoveg.get_width()//2, y_poz))
        y_poz += 50
    
    pygame.draw.rect(kepernyo, GOMB_SZIN, (KEZELO_SZELESSEG//2 - 100, KEZELO_MAGASSAG - 100, 200, 50), border_radius=8)
    ujra = fo_font.render("PLAY AGAIN", True, SZOVEG_SZIN)
    kepernyo.blit(ujra, (KEZELO_SZELESSEG//2 - ujra.get_width()//2, KEZELO_MAGASSAG - 85))

def kod_ertekeles():
    global eredmeny_uzenet, rejtveny_megoldva, jelenlegi_szorny
    
    try:
        if jelenlegi_rejtveny["name"] == "Rot13 Cipher":
            eredmeny_uzenet = "Decryption successful! KEY=GOBLIN"
            rejtveny_megoldva = True
        elif jelenlegi_rejtveny["name"] == "Reverse Cipher":
            eredmeny_uzenet = "Decryption successful! KEY=GOBLIN"
            rejtveny_megoldva = True
        elif jelenlegi_rejtveny["name"] == "Number Substitution":
            eredmeny_uzenet = "Decryption successful! KEY=GOBLIN"
            rejtveny_megoldva = True
        else:
            eredmeny_uzenet = "Decryption failed!"
            rejtveny_megoldva = False
        
        if rejtveny_megoldva and jelenlegi_szorny:
            jelenlegi_szorny["health"] -= 3
            if jelenlegi_szorny["health"] <= 0:
                teljesitett_szobak.add((jatekos_helyzete[0], jatekos_helyzete[1]))
    
    except Exception as e:
        eredmeny_uzenet = f"Error: {str(e)}"
        rejtveny_megoldva = False

def jatek_inditas():
    global jelenlegi_allapot, jatekos_helyzete, latogatott_szobak, teljesitett_szobak, jatekos_kulcsok
    jelenlegi_allapot = TERKEP
    jatekos_helyzete = [1, 1]
    latogatott_szobak = set()
    teljesitett_szobak = set()
    jatekos_kulcsok = 0
    latogatott_szobak.add((1, 1))
    
    for szorny in szornyek:
        if szorny["name"] == "The Kernel Kraken":
            szorny["health"] = 10
        else:
            szorny["health"] = random.randint(3, 6)

def tortenet_megjelenitese():
    global jelenlegi_allapot, tortenet_gorgeto_poz
    jelenlegi_allapot = TORTENET
    tortenet_gorgeto_poz = 0

def vissza_a_terkephez():
    global jelenlegi_allapot, jelenlegi_rejtveny, jelenlegi_szorny
    jelenlegi_allapot = TERKEP
    jelenlegi_rejtveny = None
    jelenlegi_szorny = None

def vissza_a_menube():
    global jelenlegi_allapot
    jelenlegi_allapot = MENU

def teljes_kepernyo_valt():
    global teljes_kepernyo, kepernyo
    teljes_kepernyo = not teljes_kepernyo
    if teljes_kepernyo:
        kepernyo = pygame.display.set_mode((KEZELO_SZELESSEG, KEZELO_MAGASSAG), pygame.FULLSCREEN)
        teljes_kepernyo_gomb.szoveg = "FULLSCREEN: ON"
    else:
        kepernyo = pygame.display.set_mode((KEZELO_SZELESSEG, KEZELO_MAGASSAG))
        teljes_kepernyo_gomb.szoveg = "FULLSCREEN: OFF"

def zene_valt():
    global zene_mehet, zene_gomb
    zene_mehet = not zene_mehet
    
    if zene_mehet:
        zene_gomb.szoveg = "MUSIC: ON"
        try:
            pygame.mixer.music.load("Broken PenWave.mp3")
            pygame.mixer.music.set_volume(0.5)
            pygame.mixer.music.play(-1)
        except:
            print("Could not load music file")
            zene_mehet = False
            zene_gomb.szoveg = "MUSIC: ERROR"
    else:
        zene_gomb.szoveg = "MUSIC: OFF"
        pygame.mixer.music.stop()

def szoba_muvelet_kezelese():
    global jelenlegi_allapot, jatekos_kulcsok, jelenlegi_szorny, rejtveny_megoldva, eredmeny_uzenet
    
    x, y = jatekos_helyzete
    szoba_tipus = barlang_terkep[y][x]
    
    if szoba_tipus == 1:
        latogatott_szobak.add((x, y))
        vissza_a_terkephez()
        
    elif szoba_tipus == 2:
        if (x, y) in teljesitett_szobak:
            vissza_a_terkephez()
        else:
            jelenlegi_allapot = REJTVENY
            rejtveny_megoldva = False
            eredmeny_uzenet = ""
            
    elif szoba_tipus == 3:
        if (x, y) not in teljesitett_szobak:
            jatekos_kulcsok += 1
            teljesitett_szobak.add((x, y))
        vissza_a_terkephez()
        
    elif szoba_tipus == 4:
        if szornyek[-1]["health"] <= 0:
            jelenlegi_allapot = GYOZELEM
        elif jatekos_kulcsok >= 3:
            jelenlegi_allapot = REJTVENY
            rejtveny_megoldva = False
            eredmeny_uzenet = ""
        else:
            vissza_a_terkephez()

def jatekos_mozgatasa(dx, dy):
    global jatekos_helyzete
    
    x, y = jatekos_helyzete
    uj_x, uj_y = x + dx, y + dy
    
    if 0 <= uj_x < len(barlang_terkep[0]) and 0 <= uj_y < len(barlang_terkep):
        if barlang_terkep[uj_y][uj_x] != 0:
            jatekos_helyzete = [uj_x, uj_y]
            latogatott_szobak.add((uj_x, uj_y))

def jatek_alaphelyzet():
    global jelenlegi_allapot, jatekos_helyzete, latogatott_szobak, teljesitett_szobak, jatekos_kulcsok
    global jelenlegi_szorny, jelenlegi_rejtveny, szorny_eletero, rejtveny_megoldva, eredmeny_uzenet, kurzor_x
    
    jelenlegi_allapot = MENU
    jatekos_helyzete = [1, 1]
    latogatott_szobak = set()
    teljesitett_szobak = set()
    jatekos_kulcsok = 0
    jelenlegi_szorny = None
    jelenlegi_rejtveny = None
    szorny_eletero = 0
    rejtveny_megoldva = False
    eredmeny_uzenet = ""
    kurzor_x = 0
    
    for szorny in szornyek:
        szorny["health"] = 10 if szorny["name"] == "The Kernel Kraken" else random.randint(3, 6)

jatek_alaphelyzet()
ora = pygame.time.Clock()

indito_gomb.muvelet = jatek_inditas
tortenet_gomb.muvelet = tortenet_megjelenitese
terkep_gomb.muvelet = vissza_a_terkephez
teljes_kepernyo_gomb.muvelet = teljes_kepernyo_valt
zene_gomb.muvelet = zene_valt
vissza_menu_gomb.muvelet = vissza_a_menube
teszt_kod_gomb.muvelet = kod_ertekeles

osszes_gomb = [indito_gomb, tortenet_gomb, terkep_gomb, teljes_kepernyo_gomb, 
               zene_gomb, vissza_menu_gomb, teszt_kod_gomb]

fut = True
while fut:
    eger_poz = pygame.mouse.get_pos()
    ido_kul = ora.tick(60)
    
    kurzor_idozito += ido_kul
    if kurzor_idozito >= 500:
        kurzor_latszik = not kurzor_latszik
        kurzor_idozito = 0
    
    for gomb in osszes_gomb:
        gomb.rajta_van(eger_poz)
    
    for esemeny in pygame.event.get():
        if esemeny.type == pygame.QUIT:
            fut = False
        
        if esemeny.type == MOUSEBUTTONDOWN and esemeny.button == 1:
            for gomb in osszes_gomb:
                if gomb.latszik and gomb.rajta:
                    if gomb == teszt_kod_gomb:
                        kod_ertekeles()
                    else:
                        gomb.muvelet()
                    break
            
            if jelenlegi_allapot == TORTENET:
                if esemeny.button == 4:
                    tortenet_gorgeto_poz = max(0, tortenet_gorgeto_poz - 30)
                elif esemeny.button == 5:
                    tortenet_gorgeto_poz += 30
        
        if esemeny.type == MOUSEWHEEL:
            if jelenlegi_allapot == TORTENET:
                tortenet_gorgeto_poz = max(0, tortenet_gorgeto_poz - esemeny.y * 30)
        
        if esemeny.type == KEYDOWN:
            if esemeny.key == K_F11:
                teljes_kepernyo_valt()
                
            if jelenlegi_allapot == MENU:
                if esemeny.key == K_RETURN:
                    jatek_inditas()
                
            elif jelenlegi_allapot == TORTENET:
                if esemeny.key:
                    jelenlegi_allapot = TERKEP
                
            elif jelenlegi_allapot == TERKEP:
                if esemeny.key == K_UP:
                    jatekos_mozgatasa(0, -1)
                elif esemeny.key == K_DOWN:
                    jatekos_mozgatasa(0, 1)
                elif esemeny.key == K_LEFT:
                    jatekos_mozgatasa(-1, 0)
                elif esemeny.key == K_RIGHT:
                    jatekos_mozgatasa(1, 0)
                elif esemeny.key == K_RETURN:
                    jelenlegi_allapot = SZOBA
                
            elif jelenlegi_allapot == SZOBA:
                if esemeny.key == K_SPACE:
                    szoba_muvelet_kezelese()
                
            elif jelenlegi_allapot == REJTVENY:
                if esemeny.key == K_UP:
                    if kivalasztott_sor > 0:
                        kivalasztott_sor -= 1
                        kurzor_x = min(kurzor_x, len(felhasznalo_kodja[kivalasztott_sor]))
                        kurzor_latszik = True
                        kurzor_idozito = 0
                elif esemeny.key == K_DOWN:
                    if kivalasztott_sor < len(felhasznalo_kodja) - 1:
                        kivalasztott_sor += 1
                        kurzor_x = min(kurzor_x, len(felhasznalo_kodja[kivalasztott_sor]))
                        kurzor_latszik = True
                        kurzor_idozito = 0
                elif esemeny.key == K_LEFT:
                    if kurzor_x > 0:
                        kurzor_x -= 1
                        kurzor_latszik = True
                        kurzor_idozito = 0
                elif esemeny.key == K_RIGHT:
                    if kurzor_x < len(felhasznalo_kodja[kivalasztott_sor]):
                        kurzor_x += 1
                        kurzor_latszik = True
                        kurzor_idozito = 0
                elif esemeny.key == K_RETURN:
                    # Create new line on Enter press
                    sor = felhasznalo_kodja[kivalasztott_sor]
                    elotte = sor[:kurzor_x]
                    utana = sor[kurzor_x:]
                    felhasznalo_kodja[kivalasztott_sor] = elotte
                    felhasznalo_kodja.insert(kivalasztott_sor + 1, utana)
                    kivalasztott_sor += 1
                    kurzor_x = 0
                    kurzor_latszik = True
                    kurzor_idozito = 0
                elif esemeny.key == K_SPACE and rejtveny_megoldva:
                    vissza_a_terkephez()
                elif esemeny.key == K_BACKSPACE:
                    if kurzor_x > 0:
                        sor = felhasznalo_kodja[kivalasztott_sor]
                        felhasznalo_kodja[kivalasztott_sor] = sor[:kurzor_x-1] + sor[kurzor_x:]
                        kurzor_x -= 1
                        kurzor_latszik = True
                        kurzor_idozito = 0
                    elif kurzor_x == 0 and kivalasztott_sor > 0:
                        kurzor_x = len(felhasznalo_kodja[kivalasztott_sor-1])
                        felhasznalo_kodja[kivalasztott_sor-1] += felhasznalo_kodja[kivalasztott_sor]
                        del felhasznalo_kodja[kivalasztott_sor]
                        kivalasztott_sor -= 1
                        kurzor_latszik = True
                        kurzor_idozito = 0
                elif esemeny.key == K_DELETE:
                    if kurzor_x < len(felhasznalo_kodja[kivalasztott_sor]):
                        sor = felhasznalo_kodja[kivalasztott_sor]
                        felhasznalo_kodja[kivalasztott_sor] = sor[:kurzor_x] + sor[kurzor_x+1:]
                        kurzor_latszik = True
                        kurzor_idozito = 0
                elif esemeny.key == K_HOME:
                    kurzor_x = 0
                    kurzor_latszik = True
                    kurzor_idozito = 0
                elif esemeny.key == K_END:
                    kurzor_x = len(felhasznalo_kodja[kivalasztott_sor])
                    kurzor_latszik = True
                    kurzor_idozito = 0
                elif esemeny.key == K_TAB:
                    sor = felhasznalo_kodja[kivalasztott_sor]
                    felhasznalo_kodja[kivalasztott_sor] = sor[:kurzor_x] + "    " + sor[kurzor_x:]
                    kurzor_x += 4
                    kurzor_latszik = True
                    kurzor_idozito = 0
                elif esemeny.unicode:
                    sor = felhasznalo_kodja[kivalasztott_sor]
                    felhasznalo_kodja[kivalasztott_sor] = sor[:kurzor_x] + esemeny.unicode + sor[kurzor_x:]
                    kurzor_x += len(esemeny.unicode)
                    kurzor_latszik = True
                    kurzor_idozito = 0
                
            elif jelenlegi_allapot == GYOZELEM:
                if esemeny.key == K_RETURN:
                    jatek_alaphelyzet()
    
    if jelenlegi_allapot == MENU:
        menu_rajzol()
    elif jelenlegi_allapot == TORTENET:
        tortenet_rajzol()
    elif jelenlegi_allapot == TERKEP:
        terkep_rajzol()
    elif jelenlegi_allapot == SZOBA:
        szoba_rajzol()
    elif jelenlegi_allapot == REJTVENY:
        rejtveny_rajzol()
    elif jelenlegi_allapot == GYOZELEM:
        gyozelem_rajzol()
    
    pygame.display.flip()

pygame.quit()
sys.exit()

