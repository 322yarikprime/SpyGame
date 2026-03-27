import pygame
import sys
import random
import os
import traceback
import math
import time
from PIL import Image, ImageSequence

pygame.init()

# Полноэкранный режим
info = pygame.display.Info()
WIDTH = info.current_w
HEIGHT = info.current_h
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("ШПИОН")

# Базовый размер
BASE_W, BASE_H = 1024, 768
scale_x = WIDTH / BASE_W
scale_y = HEIGHT / BASE_H
scale = min(scale_x, scale_y)

def s(value):
    return int(value * scale)

# Путь к файлам
base_path = "C:/SpyGame/"

# Проверка файлов
print("\n=== ПРОВЕРКА ФАЙЛОВ ===")
files_to_check = [
    "images/menufon.png",
    "images/fonybora.jpg",
    "images/dota.png",
    "images/my.jpg",
    "images/clash.png",
    "images/brawl.png",
    "music/background_music.mp3",
    "music/fonmysik2.mp3",
    "music/legenda.mp3",
    "music/WIN.mp3",
    "music/Porazenie.mp3",
    "images/START.gif",
    "images/zagruzka.png",
    "images/zagruzka.jpg",
    "music/brawlsong.mp3",
    "images/jojo.png",
    "images/OIOI.gif",
]
for f in files_to_check:
    if os.path.exists(base_path + f):
        print(f"✓ {f}")
    else:
        print(f"✗ {f} (НЕ НАЙДЕН)")
print("======================\n")

def safe_load_image(filename, size=None):
    full_path = base_path + "images/" + filename
    try:
        img = pygame.image.load(full_path)
        if filename.lower().endswith('.png'):
            img = img.convert_alpha()
        else:
            img = img.convert()
        if size:
            img = pygame.transform.scale(img, (s(size[0]), s(size[1])))
        return img
    except Exception as e:
        print(f"✗ Ошибка {filename}: {e}")
        surf = pygame.Surface((s(size[0]) if size else s(200), s(size[1]) if size else s(200)), pygame.SRCALPHA)
        surf.fill((200, 100, 100, 200))
        return surf

def safe_load_bg(filename):
    full_path = base_path + "images/" + filename
    try:
        img = pygame.image.load(full_path)
        return pygame.transform.scale(img, (WIDTH, HEIGHT))
    except:
        surf = pygame.Surface((WIDTH, HEIGHT))
        surf.fill((30, 30, 50))
        return surf

# ====================== ЗАГРУЗКА АНИМИРОВАННОГО GIF С УДАЛЕНИЕМ ЗЕЛЁНОГО ФОНА ======================
def load_animated_gif(filename, size=None, chroma_key=(0,255,0), tolerance=60):
    full_path = base_path + "images/" + filename
    try:
        pil_img = Image.open(full_path)
        frames = []
        durations = []
        for frame in ImageSequence.Iterator(pil_img):
            frame_rgba = frame.convert("RGBA")
            if chroma_key:
                data = frame_rgba.getdata()
                new_data = []
                for pixel in data:
                    r, g, b, a = pixel
                    # Удаляем пиксели, близкие к chroma_key
                    if abs(r - chroma_key[0]) <= tolerance and abs(g - chroma_key[1]) <= tolerance and abs(b - chroma_key[2]) <= tolerance:
                        new_data.append((r, g, b, 0))
                    else:
                        new_data.append((r, g, b, a))
                frame_rgba.putdata(new_data)
            mode = frame_rgba.mode
            size_frame = frame_rgba.size
            data = frame_rgba.tobytes()
            pygame_surf = pygame.image.frombuffer(data, size_frame, mode).convert_alpha()
            if size:
                pygame_surf = pygame.transform.scale(pygame_surf, (s(size[0]), s(size[1])))
            frames.append(pygame_surf)
            dur = frame.info.get('duration', 100)
            durations.append(dur)
        if not durations:
            durations = [100] * len(frames)
        avg_delay = sum(durations) / len(durations) / 1000.0
        return frames, avg_delay
    except Exception as e:
        print(f"✗ Ошибка загрузки GIF {filename}: {e}")
        dummy = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        dummy.fill((0,0,0,128))
        return [dummy], 0.1

# Загружаем START.gif для экрана загрузки (без хромакея)
gif_frames, gif_frame_delay = load_animated_gif("START.gif", size=(WIDTH, HEIGHT))
gif_frame_index = 0
gif_last_update = time.time()

# Загружаем OIOI.gif для главного меню (фон, удаляем зелёный, растягиваем на весь экран)
oioi_frames, oioi_delay = load_animated_gif("OIOI.gif", size=(WIDTH, HEIGHT), chroma_key=(0,255,0), tolerance=60)
oioi_frame_index = 0
oioi_last_update = time.time()

# Загружаем menufon.png и растягиваем на весь экран (будет плавно покачиваться)
menufon_original = safe_load_image("menufon.png", None)
menufon_full = pygame.transform.scale(menufon_original, (WIDTH, HEIGHT))
menufon_x = 0
menufon_y = 0
menufon_phase = 0
menufon_speed = 0.02   # скорость покачивания
menufon_amp = 15       # амплитуда покачивания (в пикселях)

# Загружаем jojo.png (будет телепортироваться и трястись)
jojo_img = safe_load_image("jojo.png", (200,200))

# Загружаем вращающуюся картинку для экрана загрузки
if os.path.exists(base_path + "images/zagruzka.png"):
    rotate_img = safe_load_image("zagruzka.png", (300,300))
    print("✓ Используется zagruzka.png с прозрачностью")
else:
    rotate_img = safe_load_image("zagruzka.jpg", (300,300))
    print("⚠ Используется zagruzka.jpg без прозрачности – возможен чёрный фон вокруг вращающейся картинки.")

if rotate_img is None:
    rotate_img = pygame.Surface((s(300), s(300)), pygame.SRCALPHA)
    rotate_img.fill((100,100,100,128))

# Загружаем фоны для других экранов
choice_bg = safe_load_bg("fonybora.jpg")
dota_img = safe_load_image("dota.png", (360,360))
nas_img = safe_load_image("my.jpg", (360,360))
clash_img = safe_load_image("clash.png", (360,360))
brawl_img = safe_load_image("brawl.png", (360,360))

def get_font(size):
    return pygame.font.SysFont("Arial", s(size), bold=True)

font_title = get_font(72)
font_big = get_font(68)
font_med = get_font(55)
font_button = get_font(48)
font_next = get_font(24)
font_vote = get_font(80)
font_role_btn = get_font(33)
font_confirm = get_font(28)
font_back   = get_font(28)
font_small = get_font(25)
font_loading = get_font(40)

# ====================== ПОЛНЫЕ СПИСКИ ======================
dota_characters = ["Abaddon", "Alchemist", "Ancient Apparition", "Anti-Mage", "Arc Warden", "Axe", "Bane", "Batrider", "Beastmaster", "Bloodseeker", "Bounty Hunter", "Brewmaster", "Bristleback", "Broodmother", "Centaur Warrunner", "Chaos Knight", "Chen", "Clinkz", "Clockwerk", "Crystal Maiden", "Dark Seer", "Dark Willow", "Dawnbreaker", "Dazzle", "Death Prophet", "Disruptor", "Doom", "Dragon Knight", "Drow Ranger", "Earth Spirit", "Earthshaker", "Elder Titan", "Ember Spirit", "Enchantress", "Enigma", "Faceless Void", "Grimstroke", "Gyrocopter", "Hoodwink", "Huskar", "Invoker", "Io", "Jakiro", "Juggernaut", "Keeper of the Light", "Kunkka", "Legion Commander", "Leshrac", "Lich", "Lifestealer", "Lina", "Lion", "Lone Druid", "Luna", "Lycan", "Magnus", "Marci", "Mars", "Medusa", "Meepo", "Mirana", "Monkey King", "Morphling", "Naga Siren", "Nature’s Prophet", "Necrophos", "Night Stalker", "Nyx Assassin", "Ogre Magi", "Omniknight", "Oracle", "Outworld Destroyer", "Pangolier", "Phantom Assassin", "Phantom Lancer", "Phoenix", "Primal Beast", "Puck", "Pudge", "Pugna", "Queen of Pain", "Razor", "Riki", "Rubick", "Sand King", "Shadow Demon", "Shadow Fiend", "Shadow Shaman", "Silencer", "Skywrath Mage", "Slardar", "Slark", "Snapfire", "Sniper", "Spectre", "Spirit Breaker", "Storm Spirit", "Sven", "Techies", "Templar Assassin", "Terrorblade", "Tidehunter", "Timbersaw", "Tinker", "Tiny", "Treant Protector", "Troll Warlord", "Tusk", "Underlord", "Undying", "Ursa", "Vengeful Spirit", "Venomancer", "Viper", "Visage", "Void Spirit", "Warlock", "Weaver", "Windranger", "Winter Wyvern", "Witch Doctor", "Zeus", "Ringmaster", "Мать Габена"]

nas_names = ["настя", "ярик", "даня", "саша", "давид", "фунтик", "химичка", "никита", "ксюша", "мася", "кузя", "защита украины", "песя", "настя (ярика)", "алина (настена)", "алина (данена)", "ульяна (ярика)", "географ"]

clash_royale_cards = ["Knight", "Archers", "Goblins", "Giant", "P.E.K.K.A", "Minions", "Balloon", "Witch", "Barbarians", "Golem", "Skeletons", "Valkyrie", "Skeleton Army", "Bomber", "Musketeer", "Baby Dragon", "Prince", "Wizard", "Mini P.E.K.K.A", "Spear Goblins", "Giant Skeleton", "Hog Rider", "Minion Horde", "Ice Wizard", "Royal Giant", "Guards", "Princess", "Dark Prince", "Three Musketeers", "Lava Hound", "Fire Spirits", "Miner", "Sparky", "Bowler", "Lumberjack", "Battle Ram", "Inferno Dragon", "Ice Spirit", "Dart Goblin", "Goblin Gang", "Electro Wizard", "Elite Barbarians", "Hunter", "Executioner", "Bandit", "Royal Recruits", "Night Witch", "Bats", "Royal Ghost", "Ram Rider", "Zappies", "Rascals", "Cannon Cart", "Mega Knight", "Skeleton Barrel", "Flying Machine", "Wall Breakers", "Royal Hogs", "Goblin Giant", "Fisherman", "Magic Archer", "Electro Dragon", "Firecracker", "Mighty Miner", "Elixir Golem", "Battle Healer", "Skeleton Dragons", "Electro Spirit", "Mother Witch", "Electro Giant", "Goblin Drill", "Skeleton King", "Golden Knight", "Archer Queen", "Monk", "Phoenix", "Little Prince"]

brawl_stars_fighters = ["Shelly", "Nita", "Colt", "Bull", "Brock", "El Primo", "Barley", "Poco", "Rosa", "Jessie", "Dynamike", "Tick", "8-Bit", "Rico", "Darryl", "Penny", "Carl", "Jacky", "Gus", "Bo", "Emz", "Stu", "Piper", "Pam", "Frank", "Bibi", "Bea", "Nani", "Edgar", "Griff", "Grom", "Bonnie", "Gale", "Colette", "Belle", "Ash", "Lola", "Sam", "Mandy", "Maisie", "Hank", "Pearl", "Larry & Lawrie", "Angelo", "Berry", "Shade", "Meeple", "Trunk", "Mortis", "Tara", "Gene", "Max", "Mr. P", "Sprout", "Byron", "Squeak", "Lou", "Ruffs", "Buzz", "Fang", "Eve", "Janet", "Otis", "Buster", "Gray", "R-T", "Willow", "Doug", "Chuck", "Charlie", "Mico", "Melodie", "Lily", "Clancy", "Moe", "Juju", "Ollie", "Finx", "Lumi", "Jae-Yong", "Alli", "Ziggy", "Mina", "Gigi", "Glowy", "Najia", "Spike", "Crow", "Leon", "Sandy", "Amber", "Meg", "Chester", "Kit", "Surge", "Cordelius", "Draco", "Kenji", "Pierce", "Kaze", "Sirius"]

# ====================== ПЕРЕМЕННЫЕ ======================
current_screen = "loading"
loading_start_time = 0
loading_angle = 0
loading_display_percent = 0
loading_real_percent = 0
selected_mode = None
num_players = 5
players_roles = []
spy_index = -1
current_player = 0
role_shown = False
voting_for = None
game_result = None
common_character = ""

clock = pygame.time.Clock()
running = True
pygame.mixer.init()

def play_music(filename, loop=-1, volume=0.7):
    try:
        pygame.mixer.music.stop()
        pygame.mixer.music.unload()
        full_path = base_path + "music/" + filename
        pygame.mixer.music.load(full_path)
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.play(loop)
        print(f"✓ Музыка: {filename}")
    except Exception as e:
        print(f"✗ Ошибка музыки {filename}: {e}")

def stop_music():
    pygame.mixer.music.stop()
    pygame.mixer.music.unload()

play_music("brawlsong.mp3", loop=-1, volume=0.7)

# ====================== АНИМАЦИИ ДЛЯ МЕНЮ ======================
# Для jojo (телепортация + тряска)
jojo_x = WIDTH // 2
jojo_y = HEIGHT // 2
jojo_shake_offset = (0, 0)
jojo_last_teleport = time.time()
jojo_last_shake = time.time()
jojo_shake_strength = 5

def update_jojo():
    global jojo_x, jojo_y, jojo_shake_offset, jojo_last_teleport, jojo_last_shake
    now = time.time()
    if now - jojo_last_teleport > random.uniform(0.3, 0.7):
        jojo_last_teleport = now
        jojo_x = random.randint(0, WIDTH - s(200))
        jojo_y = random.randint(0, HEIGHT - s(200))
    if now - jojo_last_shake > 0.05:
        jojo_last_shake = now
        jojo_shake_offset = (random.randint(-jojo_shake_strength, jojo_shake_strength),
                             random.randint(-jojo_shake_strength, jojo_shake_strength))

# Для menufon.png (плавное покачивание на весь экран)
def update_menufon():
    global menufon_x, menufon_y, menufon_phase
    menufon_phase += menufon_speed
    # Смещаем фон по синусоиде
    menufon_x = menufon_amp * math.sin(menufon_phase)
    menufon_y = menufon_amp * 0.5 * math.sin(menufon_phase * 1.3)

# ====================== ОТРИСОВКА ГЛАВНОГО МЕНЮ ======================
def draw_menu():
    global oioi_frame_index, oioi_last_update, oioi_delay

    # 1. Рисуем анимированный фон OIOI.gif (на весь экран, с удалённым зелёным)
    if oioi_frames:
        now = time.time()
        if now - oioi_last_update >= oioi_delay:
            oioi_frame_index = (oioi_frame_index + 1) % len(oioi_frames)
            oioi_last_update = now
        current_frame = oioi_frames[oioi_frame_index]
        if current_frame.get_size() != (WIDTH, HEIGHT):
            current_frame = pygame.transform.scale(current_frame, (WIDTH, HEIGHT))
        screen.blit(current_frame, (0, 0))
    else:
        screen.fill((0,0,0))

    # 2. Рисуем поверх menufon.png (растянут на весь экран, плавно покачивается)
    update_menufon()
    screen.blit(menufon_full, (menufon_x, menufon_y))

    # 3. Рисуем текст и кнопку
    draw_text_centered(screen, "ПРИВЕТСТВУЕМ ВАС В ИГРЕ", font_big, (255,215,0), s(768//2 - 120))
    draw_text_centered(screen, "ШПИОН", font_big, (255,50,50), s(768//2 - 40))
    play_rect_base = pygame.Rect(1024//2 - 180 + 175, 768//2 + 80, 360, 85)
    draw_button(screen, "ИГРАТЬ", play_rect_base, (180,0,0), (200,40,40), font_button)

    # 4. Рисуем jojo (телепортируется и трясётся)
    if jojo_img:
        update_jojo()
        img_rect = jojo_img.get_rect(center=(jojo_x + jojo_shake_offset[0], jojo_y + jojo_shake_offset[1]))
        screen.blit(jojo_img, img_rect)

# ====================== ТЕКСТ С ОБВОДКОЙ ======================
def draw_text_outlined(surf, text, font, color, x, y, outline_color=(0,0,0), outline_width=2):
    text_surf = font.render(text, True, color)
    outline_surf = font.render(text, True, outline_color)
    for dx in range(-outline_width, outline_width+1):
        for dy in range(-outline_width, outline_width+1):
            if dx == 0 and dy == 0:
                continue
            surf.blit(outline_surf, (x + dx, y + dy))
    surf.blit(text_surf, (x, y))

def draw_text_centered(surf, text, font, color, y):
    text_surf = font.render(text, True, color)
    x = (WIDTH - text_surf.get_width()) // 2
    draw_text_outlined(surf, text, font, color, x, y, (0,0,0), 2)

# ====================== КНОПКИ ======================
def draw_button(surf, text, rect_base, base_color, hover_color, font):
    rect = pygame.Rect(s(rect_base.x), s(rect_base.y), s(rect_base.width), s(rect_base.height))
    mouse = pygame.mouse.get_pos()
    color = hover_color if rect.collidepoint(mouse) else base_color
    pygame.draw.rect(surf, color, rect, border_radius=s(15))
    pygame.draw.rect(surf, (255,255,255), rect, width=s(4), border_radius=s(15))
    lines = text.split('\n')
    line_height = font.get_height()
    total_height = len(lines) * line_height
    start_y = rect.centery - total_height // 2
    for i, line in enumerate(lines):
        line_surf = font.render(line, True, (255,255,255))
        line_x = rect.centerx - line_surf.get_width() // 2
        draw_text_outlined(surf, line, font, (255,255,255), line_x, start_y + i * line_height, (0,0,0), 2)

# ====================== ЭФФЕКТ ПЕРЕХОДА ======================
transition_effect = 0
transition_target = None

def start_transition(next_screen):
    global transition_effect, transition_target
    transition_effect = 5
    transition_target = next_screen

# ====================== ЭКРАН ЗАГРУЗКИ ======================
def draw_loading():
    global loading_angle, gif_frame_index, gif_last_update, gif_frames, gif_frame_delay

    if gif_frames:
        now = time.time()
        if now - gif_last_update >= gif_frame_delay:
            gif_frame_index = (gif_frame_index + 1) % len(gif_frames)
            gif_last_update = now
        current_frame = gif_frames[gif_frame_index]
        if current_frame.get_size() != (WIDTH, HEIGHT):
            current_frame = pygame.transform.scale(current_frame, (WIDTH, HEIGHT))
        screen.blit(current_frame, (0, 0))
    else:
        screen.fill((0,0,0))

    if rotate_img:
        rotated = pygame.transform.rotate(rotate_img, loading_angle)
        rect = rotated.get_rect(center=(WIDTH//2, HEIGHT//2))
        screen.blit(rotated, rect)
        loading_angle += 5
        if loading_angle >= 360:
            loading_angle = 0

    bar_width = int(WIDTH * 0.6)
    bar_height = s(30)
    bar_x = (WIDTH - bar_width) // 2
    bar_y = HEIGHT - s(150)

    pygame.draw.rect(screen, (40,40,40), (bar_x, bar_y, bar_width, bar_height), border_radius=s(8))

    fill_width = int(bar_width * loading_real_percent / 100)
    if fill_width > 0:
        stripe_height = bar_height // 4
        for i in range(4):
            y_offset = bar_y + i * stripe_height
            stripe_rect = pygame.Rect(bar_x, y_offset, fill_width, stripe_height)
            brightness = 150 + i * 25
            color = (brightness, brightness // 2, 0)
            pygame.draw.rect(screen, color, stripe_rect)

    percent_text = f"{int(loading_display_percent)}%"
    text_surf = font_loading.render(percent_text, True, (255,255,255))
    text_x = (WIDTH - text_surf.get_width()) // 2
    text_y = bar_y - s(50)
    draw_text_outlined(screen, percent_text, font_loading, (255,255,255), text_x, text_y, (0,0,0), 2)

# ====================== ОСТАЛЬНЫЕ ЭКРАНЫ (БЕЗ ИЗМЕНЕНИЙ) ======================
def draw_choice():
    screen.blit(choice_bg, (0, 0))
    draw_text_centered(screen, "ВЫБОР ИГРЫ", font_title, (255,215,0), s(30))

    max_card_width = WIDTH * 0.35
    max_card_height = HEIGHT * 0.45
    card_height = min(max_card_height, HEIGHT * 0.4)
    card_width = card_height / 1.3
    if card_width > max_card_width:
        card_width = max_card_width
        card_height = card_width * 1.3
    card_w = int(card_width)
    card_h = int(card_height)

    spacing_x = int(WIDTH * 0.05)
    spacing_y = int(HEIGHT * 0.05)

    total_width = card_w * 2 + spacing_x
    start_x = (WIDTH - total_width) // 2

    y_row1 = s(100)
    y_row2 = y_row1 + card_h + spacing_y - s(50)

    modes = [
        ("ДОТА", dota_img, (0,0,0)),
        ("НАС", nas_img, (80,160,255)),
        ("КЛЕШ РОЯЛЬ", clash_img, (255,200,0)),
        ("БРАВЛ СТАРС", brawl_img, (0,200,100))
    ]
    mouse = pygame.mouse.get_pos()
    for i, (name, img, color) in enumerate(modes):
        row = i // 2
        col = i % 2
        y = y_row1 if row == 0 else y_row2
        x = start_x + col * (card_w + spacing_x)
        rect = pygame.Rect(x, y, card_w, card_h)

        hover = rect.collidepoint(mouse)
        scale = 1.08 if hover else 1.0
        scaled_w = int(card_w * scale)
        scaled_h = int(card_h * scale)
        scaled_x = x + (card_w - scaled_w) // 2
        scaled_y = y + (card_h - scaled_h) // 2

        for j, (_, _, _) in enumerate(modes):
            if j != i and hover:
                mask = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
                mask.fill((0,0,0,128))
                screen.blit(mask, (x, y))

        if hover:
            draw_rect = pygame.Rect(scaled_x, scaled_y, scaled_w, scaled_h)
        else:
            draw_rect = rect

        pygame.draw.rect(screen, color, draw_rect, border_radius=s(20))
        pygame.draw.rect(screen, (255,255,255), draw_rect, width=s(8), border_radius=s(20))
        img_scaled = pygame.transform.scale(img, (draw_rect.width - s(40), draw_rect.height - s(100)))
        screen.blit(img_scaled, (draw_rect.x + s(20), draw_rect.y + s(30)))

        if row == 0:
            if name == "ДОТА":
                text_y = draw_rect.y + draw_rect.height - s(60) - s(32)
            elif name == "НАС":
                text_y = draw_rect.y + draw_rect.height - s(60) - s(10)
            else:
                text_y = draw_rect.y + draw_rect.height - s(60)
            draw_text_outlined(screen, name, font_med, (255,255,255),
                               draw_rect.x + draw_rect.width//2 - font_med.size(name)[0]//2,
                               text_y, (0,0,0), 2)
        else:
            draw_text_outlined(screen, name, font_small, (255,255,255),
                               draw_rect.x + draw_rect.width//2 - font_small.size(name)[0]//2,
                               draw_rect.y + draw_rect.height - s(60), (0,0,0), 2)

def draw_player_count():
    global start_rect_global
    screen.blit(choice_bg, (0, 0))
    draw_text_centered(screen, "КОЛИЧЕСТВО ИГРОКОВ", font_title, (255,215,0), s(150))

    num_text = font_title.render(str(num_players), True, (255,255,255))
    num_x = (WIDTH - num_text.get_width()) // 2
    num_y = s(768//2 - 30)
    draw_text_outlined(screen, str(num_players), font_title, (255,255,255), num_x, num_y, (0,0,0), 2)

    arrow_size = s(80)
    arrow_offset = s(120)
    center_x = WIDTH // 2
    center_y = num_y + num_text.get_height() // 2

    plus_rect = pygame.Rect(center_x + arrow_offset - arrow_size//2, center_y - arrow_size//2, arrow_size, arrow_size)
    minus_rect = pygame.Rect(center_x - arrow_offset - arrow_size//2, center_y - arrow_size//2, arrow_size, arrow_size)

    pygame.draw.rect(screen, (0,180,0), plus_rect, border_radius=s(15))
    pygame.draw.rect(screen, (180,0,0), minus_rect, border_radius=s(15))
    plus_surf = font_big.render("+", True, (255,255,255))
    minus_surf = font_big.render("-", True, (255,255,255))
    screen.blit(plus_surf, plus_surf.get_rect(center=plus_rect.center))
    screen.blit(minus_surf, minus_surf.get_rect(center=minus_rect.center))

    btn_width = s(360)
    btn_height = s(90)
    btn_x = (WIDTH - btn_width) // 2
    btn_y = s(768//2 + 120)
    start_rect_global = pygame.Rect(btn_x, btn_y, btn_width, btn_height)
    mouse = pygame.mouse.get_pos()
    color = (0,180,0) if start_rect_global.collidepoint(mouse) else (0,140,0)
    pygame.draw.rect(screen, color, start_rect_global, border_radius=s(15))
    pygame.draw.rect(screen, (255,255,255), start_rect_global, width=s(4), border_radius=s(15))
    draw_text_outlined(screen, "НАЧАТЬ ИГРУ", font_button, (255,255,255),
                       btn_x + btn_width//2 - font_button.size("НАЧАТЬ ИГРУ")[0]//2,
                       btn_y + btn_height//2 - font_button.size("НАЧАТЬ ИГРУ")[1]//2,
                       (0,0,0), 2)

def draw_game():
    screen.blit(choice_bg, (0, 0))
    draw_text_centered(screen, f"ИГРОК {current_player + 1} ИЗ {num_players}", font_title, (255,215,0), s(100))
    if not role_shown:
        show_role_base = pygame.Rect(1024//2 - 220 + 155, 768//2 + 40, 440, 110)
        draw_button(screen, "ПОКАЗАТЬ МОЮ РОЛЬ", show_role_base, (80,80,255), (100,100,255), font_role_btn)
    else:
        role = players_roles[current_player]
        if role == "ШПИОН":
            draw_text_centered(screen, "ТЫ — ШПИОН!", font_big, (255,50,50), s(768//2 - 90))
            draw_text_centered(screen, "Никому не говори!", font_med, (255,180,180), s(768//2 + 20))
        else:
            draw_text_centered(screen, "ТЫ — НПС", font_big, (0,255,100), s(768//2 - 130))
            draw_text_centered(screen, str(common_character).upper(), font_med, (255,255,120), s(768//2 - 30))
        btn_text = "ПЕРЕДАТЬ ТЕЛЕФОН\nДАЛЬШЕ" if current_player < num_players - 1 else "НАЧАТЬ ГОЛОСОВАНИЕ"
        base_color = (0,200,0) if current_player < num_players - 1 else (255,140,0)
        hover_color = (min(255, base_color[0]+20), min(255, base_color[1]+20), min(255, base_color[2]+20))
        next_btn_base = pygame.Rect(1024//2 - 220 + 175, 768 - 380 + 100, 440, 140)
        draw_button(screen, btn_text, next_btn_base, base_color, hover_color, font_next)

def draw_voting():
    screen.blit(choice_bg, (0, 0))
    draw_text_centered(screen, "КТО ШПИОН?", font_title, (255,215,0), s(120))

    instr_bg = pygame.Rect(s(1024//2 - 320 + 170), s(190), s(640), s(70))
    pygame.draw.rect(screen, (255,255,255), instr_bg, border_radius=s(15))
    instr_text = font_med.render("Нажми на номер игрока", True, (0,0,0))
    screen.blit(instr_text, instr_text.get_rect(center=instr_bg.center))

    cols = 3 if num_players <= 6 else 4
    btn_size = s(140)
    spacing = s(30)
    total_width = cols * btn_size + (cols-1) * spacing
    start_x = (WIDTH - total_width) // 2
    start_y = s(320)
    for i in range(num_players):
        row = i // cols
        col = i % cols
        x = start_x + col * (btn_size + spacing)
        y = start_y + row * (btn_size + spacing)
        rect = pygame.Rect(x, y, btn_size, btn_size)
        color = (255,80,80) if voting_for == i else (60,60,180)
        pygame.draw.rect(screen, color, rect, border_radius=s(20))
        pygame.draw.rect(screen, (255,255,255), rect, width=s(6), border_radius=s(20))
        num_text = font_vote.render(str(i+1), True, (255,255,255))
        num_rect = num_text.get_rect(center=rect.center)
        draw_text_outlined(screen, str(i+1), font_vote, (255,255,255), num_rect.x, num_rect.y, (0,0,0), 2)

    if voting_for is not None:
        confirm_rect_base = pygame.Rect(1024//2 - 200 + 150, 768 - 320 + 40, 400, 100)
        draw_button(screen, "ПРОГОЛОСОВАТЬ", confirm_rect_base, (0,140,0), (0,180,0), font_confirm)

def draw_result():
    screen.blit(choice_bg, (0, 0))
    if game_result == "win_nps":
        result_text = "ПОБЕДА НПС!"
        color = (50,255,50)
    else:
        result_text = "ПОБЕДА ШПИОНА!"
        color = (255,50,50)
    draw_text_centered(screen, result_text, font_big, color, s(768//2 - 140))
    back_rect_base = pygame.Rect(1024//2 - 300 + 145, 768//2 + 80, 600, 160)
    draw_button(screen, "ВЕРНУТЬСЯ В ВЫБОР ТЕМ", back_rect_base, (180,0,0), (220,20,60), font_back)

# ====================== ГЛАВНЫЙ ЦИКЛ ======================
try:
    loading_start_time = time.time()
    loading_real_percent = 0.0
    loading_display_percent = 0.0
    last_update_time = time.time()
    target_display = 0.0

    while running:
        pos = None
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_F11:
                    pygame.display.toggle_fullscreen()
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()

        # ЭКРАН ЗАГРУЗКИ
        if current_screen == "loading":
            elapsed = time.time() - loading_start_time
            loading_real_percent = min(100.0, (elapsed / 15.0) * 100.0)

            if elapsed < 15:
                if time.time() - last_update_time > random.uniform(0.15, 0.35):
                    if loading_display_percent < loading_real_percent:
                        target_display = min(loading_real_percent, loading_display_percent + random.uniform(3, 12))
                        target_display = min(100, target_display)
                        last_update_time = time.time()
                if loading_display_percent < target_display:
                    step = (time.time() - last_update_time) * 50
                    loading_display_percent = min(target_display, loading_display_percent + step)
                elif loading_display_percent > loading_real_percent + 2:
                    loading_display_percent = max(loading_display_percent - 1, loading_real_percent)
                loading_display_percent = max(0, min(100, loading_display_percent))
            else:
                loading_real_percent = 100
                loading_display_percent = 100

            draw_loading()
            pygame.display.flip()
            clock.tick(60)

            if elapsed >= 15:
                stop_music()
                play_music("background_music.mp3", loop=-1, volume=0.65)
                current_screen = "menu"
                loading_real_percent = 0
                loading_display_percent = 0
                continue

        # Эффект перехода
        if transition_effect > 0:
            transition_effect -= 1
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.fill((255,255,255))
            overlay.set_alpha(150 - transition_effect * 30)
            screen.blit(overlay, (0,0))
            if transition_effect == 0 and transition_target:
                current_screen = transition_target
                transition_target = None

        # Обработка кликов для остальных экранов
        if pos and current_screen != "loading":
            if current_screen == "menu":
                play_rect_base = pygame.Rect(1024//2 - 180 + 175, 768//2 + 80, 360, 85)
                play_rect = pygame.Rect(s(play_rect_base.x), s(play_rect_base.y), s(play_rect_base.width), s(play_rect_base.height))
                if play_rect.collidepoint(pos):
                    stop_music()
                    play_music("fonmysik2.mp3", loop=-1, volume=0.7)
                    start_transition("choice")

            elif current_screen == "choice":
                max_card_width = WIDTH * 0.35
                max_card_height = HEIGHT * 0.45
                card_height = min(max_card_height, HEIGHT * 0.4)
                card_width = card_height / 1.3
                if card_width > max_card_width:
                    card_width = max_card_width
                    card_height = card_width * 1.3
                card_w = int(card_width)
                card_h = int(card_height)
                spacing_x = int(WIDTH * 0.05)
                spacing_y = int(HEIGHT * 0.05)
                total_width = card_w * 2 + spacing_x
                start_x = (WIDTH - total_width) // 2
                y_row1 = s(100)
                y_row2 = y_row1 + card_h + spacing_y - s(50)

                modes = ["dota", "nas", "clash", "brawl"]
                for i, mode_key in enumerate(modes):
                    row = i // 2
                    col = i % 2
                    y = y_row1 if row == 0 else y_row2
                    x = start_x + col * (card_w + spacing_x)
                    rect = pygame.Rect(x, y, card_w, card_h)
                    if rect.collidepoint(pos):
                        selected_mode = mode_key
                        start_transition("player_count")
                        break

            elif current_screen == "player_count":
                arrow_size = s(80)
                arrow_offset = s(120)
                center_x = WIDTH // 2
                num_y = s(768//2 - 30)
                num_text = font_title.render(str(num_players), True, (255,255,255))
                center_y = num_y + num_text.get_height() // 2

                plus_rect = pygame.Rect(center_x + arrow_offset - arrow_size//2, center_y - arrow_size//2, arrow_size, arrow_size)
                minus_rect = pygame.Rect(center_x - arrow_offset - arrow_size//2, center_y - arrow_size//2, arrow_size, arrow_size)

                btn_width = s(360)
                btn_height = s(90)
                btn_x = (WIDTH - btn_width) // 2
                btn_y = s(768//2 + 120)
                start_rect_global = pygame.Rect(btn_x, btn_y, btn_width, btn_height)

                if plus_rect.collidepoint(pos) and num_players < 12:
                    num_players += 1
                elif minus_rect.collidepoint(pos) and num_players > 3:
                    num_players -= 1
                elif start_rect_global and start_rect_global.collidepoint(pos):
                    if selected_mode == "dota":
                        char_list = dota_characters[:]
                    elif selected_mode == "nas":
                        char_list = nas_names[:]
                    elif selected_mode == "clash":
                        char_list = clash_royale_cards[:]
                    else:
                        char_list = brawl_stars_fighters[:]
                    spy_index = random.randint(0, num_players - 1)
                    common_character = random.choice(char_list)
                    players_roles = [common_character] * num_players
                    players_roles[spy_index] = "ШПИОН"
                    stop_music()
                    play_music("legenda.mp3", loop=-1, volume=0.65)
                    current_player = 0
                    role_shown = False
                    voting_for = None
                    game_result = None
                    start_transition("game")

            elif current_screen == "game":
                if not role_shown:
                    show_role_base = pygame.Rect(1024//2 - 220 + 155, 768//2 + 40, 440, 110)
                    show_rect = pygame.Rect(s(show_role_base.x), s(show_role_base.y), s(show_role_base.width), s(show_role_base.height))
                    if show_rect.collidepoint(pos):
                        role_shown = True
                else:
                    next_btn_base = pygame.Rect(1024//2 - 220 + 175, 768 - 380 + 100, 440, 140)
                    next_rect = pygame.Rect(s(next_btn_base.x), s(next_btn_base.y), s(next_btn_base.width), s(next_btn_base.height))
                    if next_rect.collidepoint(pos):
                        if current_player < num_players - 1:
                            current_player += 1
                            role_shown = False
                        else:
                            start_transition("voting")
                            voting_for = None

            elif current_screen == "voting":
                cols = 3 if num_players <= 6 else 4
                btn_size = s(140)
                spacing = s(30)
                total_width = cols * btn_size + (cols-1) * spacing
                start_x = (WIDTH - total_width) // 2
                start_y = s(320)
                for i in range(num_players):
                    row = i // cols
                    col = i % cols
                    x = start_x + col * (btn_size + spacing)
                    y = start_y + row * (btn_size + spacing)
                    rect = pygame.Rect(x, y, btn_size, btn_size)
                    if rect.collidepoint(pos):
                        voting_for = i
                        break
                if voting_for is not None:
                    confirm_rect_base = pygame.Rect(1024//2 - 200 + 150, 768 - 320 + 40, 400, 100)
                    confirm_rect = pygame.Rect(s(confirm_rect_base.x), s(confirm_rect_base.y), s(confirm_rect_base.width), s(confirm_rect_base.height))
                    if confirm_rect.collidepoint(pos):
                        if voting_for == spy_index:
                            game_result = "win_nps"
                            stop_music()
                            play_music("WIN.mp3", loop=0, volume=0.8)
                        else:
                            game_result = "win_spy"
                            stop_music()
                            play_music("Porazenie.mp3", loop=0, volume=0.8)
                        start_transition("result")

            elif current_screen == "result":
                back_rect_base = pygame.Rect(1024//2 - 300 + 145, 768//2 + 80, 600, 160)
                back_rect = pygame.Rect(s(back_rect_base.x), s(back_rect_base.y), s(back_rect_base.width), s(back_rect_base.height))
                if back_rect.collidepoint(pos):
                    stop_music()
                    play_music("fonmysik2.mp3", loop=-1, volume=0.7)
                    start_transition("choice")
                    selected_mode = None
                    num_players = 5
                    players_roles = []
                    spy_index = -1
                    current_player = 0
                    role_shown = False
                    voting_for = None
                    game_result = None

        # Отрисовка основных экранов
        if current_screen != "loading":
            if current_screen == "menu":
                draw_menu()
            elif current_screen == "choice":
                draw_choice()
            elif current_screen == "player_count":
                draw_player_count()
            elif current_screen == "game":
                draw_game()
            elif current_screen == "voting":
                draw_voting()
            elif current_screen == "result":
                draw_result()

            pygame.display.flip()

        clock.tick(60)

except Exception as e:
    print("=" * 50)
    print("ПРОИЗОШЛА ОШИБКА:")
    traceback.print_exc()
    print("=" * 50)
    input("Нажми Enter для выхода...")

finally:
    stop_music()
    pygame.quit()
    sys.exit()