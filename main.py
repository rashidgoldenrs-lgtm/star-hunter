
import pygame
import random
import math

pygame.init()

# إعداد الشاشة
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
W, H = screen.get_size()
pygame.display.set_caption("STAR HUNTER")
clock = pygame.time.Clock()

# الألوان
BLACK = (5, 5, 20)
WHITE = (245, 250, 255)
CYAN = (0, 230, 255)
BLUE = (35, 100, 255)
PURPLE = (170, 50, 255)
GOLD = (255, 210, 40)
RED = (255, 55, 90)
GREEN = (50, 255, 150)

font = pygame.font.Font(None, max(24, H // 25))
small_font = pygame.font.Font(None, max(18, H // 36))
big_font = pygame.font.Font(None, max(42, H // 11))

# خلفية النجوم
stars = [
    [random.randrange(W), random.randrange(H),
     random.choice([1, 2, 3])]
    for _ in range(100)
]

# حالات اللعبة
MENU = "menu"
PLAYING = "playing"
GAMEOVER = "gameover"
state = MENU

score = 0
lives = 3
stage = 1
kills = 0

player_x = W / 2
player_y = H * 0.78
player_speed = W * 0.65

bullets = []
enemies = []
enemy_bullets = []
particles = []
gold_stars = []

boss = None
boss_bullets = []

left_pressed = False
right_pressed = False
fire_pressed = False

enemy_timer = 0
star_timer = 0
fire_timer = 0
boss_message_timer = 0

# أحجام عناصر الواجهة
btn_w = W * 0.22
btn_h = H * 0.075

left_btn = pygame.Rect(
    int(W * 0.05), int(H * 0.86),
    int(btn_w), int(btn_h)
)
right_btn = pygame.Rect(
    int(W * 0.29), int(H * 0.86),
    int(btn_w), int(btn_h)
)
fire_btn = pygame.Rect(
    int(W * 0.70), int(H * 0.84),
    int(W * 0.25), int(H * 0.10)
)

start_btn = pygame.Rect(
    int(W * 0.28), int(H * 0.55),
    int(W * 0.44), int(H * 0.09)
)
again_btn = pygame.Rect(
    int(W * 0.25), int(H * 0.57),
    int(W * 0.50), int(H * 0.08)
)
home_btn = pygame.Rect(
    int(W * 0.25), int(H * 0.69),
    int(W * 0.50), int(H * 0.08)
)


def draw_text(text, fnt, color, x, y, center=True):
    image = fnt.render(str(text), True, color)
    rect = image.get_rect()
    if center:
        rect.center = (int(x), int(y))
    else:
        rect.topleft = (int(x), int(y))
    screen.blit(image, rect)


def draw_button(rect, text, color):
    pygame.draw.rect(screen, color, rect, border_radius=15)
    pygame.draw.rect(
        screen, WHITE, rect, width=2, border_radius=15
    )
    draw_text(
        text, font, WHITE,
        rect.centerx, rect.centery
    )


def draw_ship(x, y, scale=1, color=CYAN):
    x, y = int(x), int(y)
    points = [
        (x, y - 28 * scale),
        (x - 22 * scale, y + 22 * scale),
        (x, y + 12 * scale),
        (x + 22 * scale, y + 22 * scale)
    ]
    pygame.draw.polygon(screen, color, points)
    pygame.draw.polygon(screen, WHITE, points, 2)

    pygame.draw.polygon(screen, PURPLE, [
        (x - 12 * scale, y + 14 * scale),
        (x - 22 * scale, y + 26 * scale),
        (x - 4 * scale, y + 20 * scale)
    ])
    pygame.draw.polygon(screen, PURPLE, [
        (x + 12 * scale, y + 14 * scale),
        (x + 22 * scale, y + 26 * scale),
        (x + 4 * scale, y + 20 * scale)
    ])


def explosion(x, y, color=GOLD):
    for _ in range(18):
        angle = random.random() * math.pi * 2
        speed = random.uniform(70, 260)
        particles.append([
            x, y,
            math.cos(angle) * speed,
            math.sin(angle) * speed,
            random.uniform(0.25, 0.65),
            color
        ])


def reset_game():
    global score, lives, stage, kills
    global player_x, player_y
    global bullets, enemies, enemy_bullets
    global particles, gold_stars, boss, boss_bullets
    global enemy_timer, star_timer, fire_timer
    global boss_message_timer, state
    global left_pressed, right_pressed, fire_pressed

    score = 0
    lives = 3
    stage = 1
    kills = 0

    player_x = W / 2
    player_y = H * 0.78

    bullets = []
    enemies = []
    enemy_bullets = []
    particles = []
    gold_stars = []
    boss = None
    boss_bullets = []

    enemy_timer = 0
    star_timer = 0
    fire_timer = 0
    boss_message_timer = 0

    left_pressed = False
    right_pressed = False
    fire_pressed = False

    state = PLAYING


def spawn_enemy():
    enemies.append({
        "x": random.randint(35, W - 35),
        "y": -35,
        "speed": random.uniform(H * 0.17, H * 0.27)
                 + stage * 5,
        "hp": 1 if stage < 3 else 2,
        "shoot": random.uniform(1.0, 2.5),
        "size": random.randint(17, 23)
    })


def spawn_boss():
    global boss, boss_message_timer
    boss = {
        "x": W / 2,
        "y": H * 0.18,
        "direction": 1,
        "hp": 20 + stage * 8,
        "max_hp": 20 + stage * 8,
        "shoot": 1.0
    }
    boss_message_timer = 2.5


def draw_enemy(enemy):
    x, y = int(enemy["x"]), int(enemy["y"])
    s = enemy["size"]

    points = [
        (x - s, y - s // 2),
        (x - s // 2, y - s),
        (x + s // 2, y - s),
        (x + s, y - s // 2),
        (x + s // 2, y + s),
        (x - s // 2, y + s)
    ]
    pygame.draw.polygon(screen, RED, points)
    pygame.draw.polygon(screen, WHITE, points, 2)
    pygame.draw.circle(screen, GOLD, (x, y), 4)


def draw_boss():
    if boss is None:
        return

    x, y = int(boss["x"]), int(boss["y"])
    points = [
        (x - 65, y - 18),
        (x - 42, y - 40),
        (x + 42, y - 40),
        (x + 65, y - 18),
        (x + 45, y + 27),
        (x, y + 40),
        (x - 45, y + 27)
    ]

    pygame.draw.polygon(screen, PURPLE, points)
    pygame.draw.polygon(screen, CYAN, points, 3)
    pygame.draw.circle(screen, RED, (x, y), 12)

    bar_w = W * 0.58
    bar_h = 12
    bar_x = (W - bar_w) / 2
    bar_y = H * 0.075

    pygame.draw.rect(
        screen, (70, 30, 50),
        (bar_x, bar_y, bar_w, bar_h),
        border_radius=5
    )

    ratio = max(0, boss["hp"] / boss["max_hp"])
    pygame.draw.rect(
        screen, RED,
        (bar_x, bar_y, bar_w * ratio, bar_h),
        border_radius=5
    )

    draw_text(
        "BOSS", small_font, RED,
        W / 2, bar_y - 13
    )


def update_background(dt):
    screen.fill(BLACK)

    for star in stars:
        star[1] += star[2] * H * 0.12 * dt
        if star[1] > H:
            star[0] = random.randrange(W)
            star[1] = 0

        brightness = min(255, 100 + star[2] * 45)
        pygame.draw.circle(
            screen,
            (brightness // 2, brightness // 2, brightness),
            (int(star[0]), int(star[1])),
            star[2]
        )


def update_particles(dt):
    for p in particles[:]:
        p[0] += p[2] * dt
        p[1] += p[3] * dt
        p[4] -= dt

        if p[4] <= 0:
            particles.remove(p)
            continue

        radius = max(1, int(p[4] * 10))
        pygame.draw.circle(
            screen, p[5],
            (int(p[0]), int(p[1])),
            radius
        )


def draw_game_ui():
    draw_text(
        "SCORE: " + str(score),
        font, GOLD, 15, 15, False
    )
    draw_text(
        "LIVES: " + str(lives),
        font, RED, 15, 48, False
    )
    draw_text(
        "STAGE: " + str(stage),
        font, CYAN, W - 15, 15, False
    )

    draw_button(left_btn, "<", BLUE)
    draw_button(right_btn, ">", BLUE)
    draw_button(fire_btn, "FIRE!", RED)


def hit_player():
    global lives, state

    lives -= 1
    explosion(player_x, player_y, RED)

    if lives <= 0:
        state = GAMEOVER


def handle_touch(pos, pressed):
    global left_pressed, right_pressed, fire_pressed
    global state

    if state == PLAYING:
        if pressed:
            left_pressed = left_btn.collidepoint(pos)
            right_pressed = right_btn.collidepoint(pos)
            fire_pressed = fire_btn.collidepoint(pos)
        else:
            left_pressed = False
            right_pressed = False
            fire_pressed = False

    elif pressed and state == MENU:
        if start_btn.collidepoint(pos):
            reset_game()

    elif pressed and state == GAMEOVER:
        if again_btn.collidepoint(pos):
            reset_game()
        elif home_btn.collidepoint(pos):
            state = MENU


running = True

while running:
    dt = min(clock.tick(60) / 1000, 0.04)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

            if event.key == pygame.K_LEFT:
                left_pressed = True
            if event.key == pygame.K_RIGHT:
                right_pressed = True
            if event.key == pygame.K_SPACE:
                fire_pressed = True

        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                left_pressed = False
            if event.key == pygame.K_RIGHT:
                right_pressed = False
            if event.key == pygame.K_SPACE:
                fire_pressed = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            handle_touch(event.pos, True)

        elif event.type == pygame.MOUSEBUTTONUP:
            handle_touch(event.pos, False)

        elif event.type == pygame.FINGERDOWN:
            handle_touch(
                (int(event.x * W), int(event.y * H)), True
            )

        elif event.type == pygame.FINGERUP:
            handle_touch(
                (int(event.x * W), int(event.y * H)), False
            )

    update_background(dt)

    if state == MENU:
        draw_text(
            "STAR HUNTER", big_font, CYAN,
            W / 2, H * 0.28
        )
        draw_text(
            "SPACE BATTLE", font, PURPLE,
            W / 2, H * 0.39
        )
        draw_ship(W / 2, H * 0.46, 1.4)
        draw_button(start_btn, "START GAME", BLUE)
        draw_text(
            "BY RASHID AL-QATRANI",
            small_font, WHITE, W / 2, H * 0.78
        )

    elif state == PLAYING:
        # حركة سفينة اللاعب
        if left_pressed:
            player_x -= player_speed * dt
        if right_pressed:
            player_x += player_speed * dt

        player_x = max(28, min(W - 28, player_x))

        # إطلاق الليزر
        fire_timer -= dt
        if fire_pressed and fire_timer <= 0:
            bullets.append([player_x, player_y - 25])
            fire_timer = 0.22

        for bullet in bullets[:]:
            bullet[1] -= H * 0.85 * dt
            pygame.draw.rect(
                screen, CYAN,
                (int(bullet[0] - 3), int(bullet[1]), 6, 20),
                border_radius=3
            )
            if bullet[1] < 0:
                bullets.remove(bullet)

        # ظهور النجوم الذهبية
        star_timer += dt
        if star_timer > 2.5:
            star_timer = 0
            gold_stars.append([
                random.randint(20, W - 20), -15
            ])

        for star in gold_stars[:]:
            star[1] += H * 0.18 * dt
            pygame.draw.circle(
                screen, GOLD,
                (int(star[0]), int(star[1])), 9
            )
            pygame.draw.circle(
                screen, WHITE,
                (int(star[0]), int(star[1])), 4
            )

            if math.hypot(
                star[0] - player_x,
                star[1] - player_y
            ) < 30:
                score += 10
                gold_stars.remove(star)
            elif star[1] > H:
                gold_stars.remove(star)

        # ظهور الأعداء
        enemy_timer += dt
        if boss is None and enemy_timer > max(0.45, 1.35 - stage * 0.08):
            enemy_timer = 0
            spawn_enemy()

        # حركة الأعداء وإطلاقهم
        for enemy in enemies[:]:
            enemy["y"] += enemy["speed"] * dt
            enemy["shoot"] -= dt

            if enemy["shoot"] <= 0:
                enemy_bullets.append([
                    enemy["x"], enemy["y"] + 12
                ])
                enemy["shoot"] = random.uniform(1.4, 2.8)

            draw_enemy(enemy)

            if math.hypot(
                enemy["x"] - player_x,
                enemy["y"] - player_y
            ) < 32:
                enemies.remove(enemy)
                hit_player()
                continue

            if enemy["y"] > H + 40:
                enemies.remove(enemy)
                continue

            # اصطدام الليزر بالعدو
            for bullet in bullets[:]:
                if math.hypot(
                    enemy["x"] - bullet[0],
                    enemy["y"] - bullet[1]
                ) < enemy["size"] + 8:
                    if bullet in bullets:
                        bullets.remove(bullet)

                    enemy["hp"] -= 1
                    explosion(bullet[0], bullet[1], CYAN)

                    if enemy["hp"] <= 0:
                        explosion(
                            enemy["x"], enemy["y"], RED
                        )
                        enemies.remove(enemy)
                        score += 20
                        kills += 1
                    break

        # قذائف الأعداء
        for shot in enemy_bullets[:]:
            shot[1] += H * 0.30 * dt

            pygame.draw.circle(
                screen, RED,
                (int(shot[0]), int(shot[1])), 7
            )

            if math.hypot(
                shot[0] - player_x,
                shot[1] - player_y
            ) < 25:
                enemy_bullets.remove(shot)
                hit_player()
                continue

            if shot[1] > H:
                enemy_bullets.remove(shot)

        # ظهور الزعيم بعد القضاء على 12 عدواً
        if kills >= 12 and boss is None:
            spawn_boss()
            kills = 0

        # قتال الزعيم
        if boss is not None:
            boss["x"] += boss["direction"] * W * 0.22 * dt

            if boss["x"] > W - 75:
                boss["direction"] = -1
            elif boss["x"] < 75:
                boss["direction"] = 1

            boss["shoot"] -= dt

            if boss["shoot"] <= 0:
                boss_bullets.append([boss["x"], boss["y"] + 25])
                boss_bullets.append([
                    boss["x"] - 35, boss["y"] + 20
                ])
                boss_bullets.append([
                    boss["x"] + 35, boss["y"] + 20
                ])
                boss["shoot"] = max(0.45, 1.1 - stage * 0.05)

            draw_boss()

            for bullet in bullets[:]:
                if math.hypot(
                    bullet[0] - boss["x"],
                    bullet[1] - boss["y"]
                ) < 62:
                    bullets.remove(bullet)
                    boss["hp"] -= 1
                    explosion(
                        bullet[0], bullet[1], PURPLE
                    )

                    if boss["hp"] <= 0:
                        explosion(
                            boss["x"], boss["y"], GOLD
                        )
                        boss = None
                        stage += 1
                        score += 200
                        boss_message_timer = 2.0
                        boss_bullets.clear()
                    break

            if boss is not None:
                for shot in boss_bullets[:]:
                    shot[1] += H * 0.32 * dt
                    pygame.draw.circle(
                        screen, PURPLE,
                        (int(shot[0]), int(shot[1])), 9
                    )

                    if math.hypot(
                        shot[0] - player_x,
                        shot[1] - player_y
                    ) < 27:
                        boss_bullets.remove(shot)
                        hit_player()
                    elif shot[1] > H:
                        boss_bullets.remove(shot)

        if boss_message_timer > 0:
            boss_message_timer -= dt
            if boss is not None:
                draw_text(
                    "WARNING: BOSS APPROACHING!",
                    font, RED, W / 2, H * 0.30
                )
            else:
                draw_text(
                    "STAGE CLEARED!",
                    big_font, GREEN, W / 2, H * 0.30
                )

        draw_ship(player_x, player_y, 1.0)
        update_particles(dt)
        draw_game_ui()

    elif state == GAMEOVER:
        draw_text(
            "GAME OVER", big_font, RED,
            W / 2, H * 0.28
        )
        draw_text(
            "FINAL SCORE: " + str(score),
            font, GOLD, W / 2, H * 0.40
        )
        draw_button(again_btn, "PLAY AGAIN", BLUE)
        draw_button(home_btn, "MAIN MENU", PURPLE)
        draw_text(
            "BY RASHID AL-QATRANI",
            small_font, WHITE, W / 2, H * 0.84
        )

    pygame.display.flip()

pygame.quit()
