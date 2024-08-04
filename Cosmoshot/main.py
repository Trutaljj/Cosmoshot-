import pygame
import random
import math

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Cosmoshot")

# Load and scale sprites
background = pygame.image.load("bg.png")
background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))

playerufo = pygame.image.load("playerufo.png").convert_alpha()
playerufo = pygame.transform.scale(playerufo, (20, 20))
playerufo_rect = playerufo.get_rect()
playerufo_mask = pygame.mask.from_surface(playerufo)

playerbullet = pygame.image.load("playerbullet.png").convert_alpha()
playerbullet = pygame.transform.scale(playerbullet, (5, 5))
playerbullet_mask = pygame.mask.from_surface(playerbullet)

enemyufo = pygame.image.load("enemyufo.png").convert_alpha()
enemyufo = pygame.transform.scale(enemyufo, (20, 20))
enemyufo_mask = pygame.mask.from_surface(enemyufo)

# Define colors
BG = (50, 50, 50)
WHITE = (255, 255, 255)
RED = (255, 0, 0)

clock = pygame.time.Clock()

player = pygame.Rect((200, 250, 20, 20))  # Initial player position

# Sound effects
hit = pygame.mixer.Sound('hit.mp3')
bullet = pygame.mixer.Sound('bullet.mp3')
goal = pygame.mixer.Sound('goal.wav')
fail = pygame.mixer.Sound('fail.wav')
damage = pygame.mixer.Sound('damage.wav')
tik = pygame.mixer.Sound('tik.wav')
go = pygame.mixer.Sound('go.wav')
pygame.mixer.music.load('bgm.wav')
pygame.mixer.music.play(-1)

# Define movement types
MOVE_TOWARDS_PLAYER = 0
MOVE_LEFT_RIGHT = 1

# Initialize green squares with different movement types
def create_random_square():
    x = random.randint(SCREEN_WIDTH - 200, SCREEN_WIDTH - 35)
    y = random.randint(0, SCREEN_HEIGHT - 35)
    move_type = random.choice([MOVE_TOWARDS_PLAYER, MOVE_LEFT_RIGHT, MOVE_LEFT_RIGHT])
    return {'rect': pygame.Rect(x, y, 20, 20), 'move_type': move_type, 'direction': random.choice([1, -1])}

def create_random_squarespawn():
    x = random.randint(0, 0)
    y = random.randint(0, SCREEN_HEIGHT)
    move_type = random.choice([MOVE_TOWARDS_PLAYER, MOVE_LEFT_RIGHT, MOVE_LEFT_RIGHT])
    return {'rect': pygame.Rect(x, y, 20, 20), 'move_type': move_type, 'direction': random.choice([1, -1])}

num_squares = random.randint(50, 75)
squares = [create_random_square() for _ in range(num_squares)]

shots = []

text_font = pygame.font.SysFont("Helvetica", 30)

def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

def reflect_vector(dir_vec, normal):
    dot_product = dir_vec[0] * normal[0] + dir_vec[1] * normal[1]
    return (dir_vec[0] - 2 * dot_product * normal[0], dir_vec[1] - 2 * dot_product * normal[1])

# Countdown setup
countdown_time = 5000  # 5 seconds in milliseconds
countdown_start = pygame.time.get_ticks()
countdown_finished = False

# LIMIT timer setup
limit_time = 60000  # 60 seconds in milliseconds
limit_start = None  # To be set when countdown finishes
limit_finished = False

# Initialize collision counter and max hits (lives)
collision_count = 0
max_hits = 5

# Initialize shot-green square collision counter
shot_square_collision_count = 0
target_collisions_required = 100

# Spawning setup
spawn_interval = 90
last_spawn_time = pygame.time.get_ticks()

run = True
while run:
    screen.fill(BG)
    screen.blit(background, (0,0))
    
    # Draw player
    playerufo_rect.topleft = (player.x, player.y)
    screen.blit(playerufo, playerufo_rect)

    clock.tick(60)
    current_time = pygame.time.get_ticks()
    elapsed_time = current_time - countdown_start

    if elapsed_time >= countdown_time:
        countdown_finished = True
        elapsed_time = countdown_time  # Cap the elapsed time to countdown_time for display purposes
        
        if limit_start is None:
            limit_start = current_time  # Start the LIMIT timer when countdown finishes
        
        if not limit_finished:
            limit_elapsed_time = current_time - limit_start
            if limit_elapsed_time >= limit_time:
                limit_finished = True
                limit_elapsed_time = limit_time  # Cap the elapsed time to limit_time for display purposes
    else:
        limit_start = None

    # Draw countdown timer
    if not countdown_finished:
        remaining_time = max(countdown_time - elapsed_time, 0) / 1000
        draw_text(f"Countdown: {remaining_time:.1f}", text_font, WHITE, 10, 10)
        draw_text("USE WASD AND MOUSE | SHOOT TARGETS", text_font, WHITE, 80, 150)
        draw_text("TARGETS SPAWN ON THE LEFT", text_font, WHITE, 80, 100)
        draw_text("SHOOT 100 TARGETS", text_font, WHITE, 80, 200)
    else:
        draw_text("", text_font, (0, 0, 0), 220, 150)
        
        # Draw LIMIT timer
        if not limit_finished:
            limit_remaining_time = max(limit_time - (current_time - limit_start), 0) / 1000
            draw_text(f"TIME: {limit_remaining_time:.1f}", text_font, WHITE, 10, 200)
        else:
            draw_text("TIME: 0.0", text_font, WHITE, 10, 200)

    # Update collision with player and green squares
    for square_data in squares[:]:
        square = square_data['rect']
        if playerufo_rect.colliderect(square):
            damage.set_volume(1.2)
            damage.play()
            collision_count += 1
            playercol = WHITE
            squares.remove(square_data)
            break
    else:
        playercol = RED

    # Check for loss condition
    if collision_count >= max_hits:
        fail.set_volume(5)
        fail.play()
        draw_text("You Lost", text_font, WHITE, SCREEN_WIDTH // 2 - 70, SCREEN_HEIGHT // 2 - 15)
        pygame.display.update()
        pygame.time.wait(3000)  # Display the message for 3 seconds
        run = False  # End the game loop

    # Draw and update squares
    for square_data in squares:
        square = square_data['rect']
        move_type = square_data['move_type']
        direction = square_data['direction']
        if countdown_finished:
            if move_type == MOVE_TOWARDS_PLAYER:
                dx = player.centerx - square.centerx
                dy = player.centery - square.centery
                mag = math.sqrt(dx**2 + dy**2)
                if mag != 0:
                    dx, dy = dx / mag, dy / mag
                    square.x += dx * 2
                    square.y += dy * 2

            elif move_type == MOVE_LEFT_RIGHT:
                square.x += direction * 2
                if square.left < 0 or square.right > SCREEN_WIDTH:
                    square_data['direction'] *= -1

        screen.blit(enemyufo, square)

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        elif countdown_finished:
            if event.type == pygame.MOUSEBUTTONDOWN:
                bullet.set_volume(1.2)
                bullet.play()
                mouse_pos = event.pos
                dir_vec = (mouse_pos[0] - player.centerx, mouse_pos[1] - player.centery)
                mag = (dir_vec[0]**2 + dir_vec[1]**2)**0.5
                dir_vec = (dir_vec[0]/mag, dir_vec[1]/mag)
                shot = pygame.Rect(player.centerx, player.centery, 5, 5)
                screen.blit(playerbullet, shot)
                shots.append((shot, dir_vec, pygame.time.get_ticks()))  # Store creation time

    # Check if it's time to spawn a new square
    if countdown_finished and current_time - last_spawn_time >= spawn_interval:
        last_spawn_time = current_time
        squares.append(create_random_squarespawn())

    # Remove old shots
    shots = [(shot, dir_vec, creation_time) for (shot, dir_vec, creation_time) in shots if current_time - creation_time < 15000]

    # Update shot positions and handle reflections
    for i in range(len(shots) - 1, -1, -1):
        shot, dir_vec, creation_time = shots[i]
        
        # Move shot
        shot.x += dir_vec[0] * 5
        shot.y += dir_vec[1] * 5

        # Handle boundary collisions
        if shot.left < 0:
            dir_vec = reflect_vector(dir_vec, (1, 0))
        elif shot.right > SCREEN_WIDTH:
            dir_vec = reflect_vector(dir_vec, (-1, 0))
        if shot.top < 0:
            dir_vec = reflect_vector(dir_vec, (0, 1))
        elif shot.bottom > SCREEN_HEIGHT:
            dir_vec = reflect_vector(dir_vec, (0, -1))

        # Update the shot's direction and store the new state
        shots[i] = (shot, dir_vec, creation_time)

        # Draw the shot
        screen.blit(playerbullet, shot)

        # Check for collision with squares
        for square_data in squares[:]:
            square = square_data['rect']
            if shot.colliderect(square):
                hit.set_volume(0.7)
                hit.play()
                squares.remove(square_data)
                shots.pop(i)
                shot_square_collision_count += 1
                break
        else:
            # Check for collision with the player if no square collision
            if pygame.time.get_ticks() - creation_time >= 300:
                if playerufo_rect.colliderect(shot):
                    damage.set_volume(0.7)
                    damage.play()
                    playercol = WHITE
                    collision_count += 1
                    shots.pop(i)  # Remove the shot if it hits the player

    # Player movement
    key = pygame.key.get_pressed()
    dx, dy = 0, 0

    if key[pygame.K_a] and key[pygame.K_w]:
        dx, dy = -5, -5
    elif key[pygame.K_a] and key[pygame.K_s]:
        dx, dy = -5, 5
    elif key[pygame.K_d] and key[pygame.K_w]:
        dx, dy = 5, -5
    elif key[pygame.K_d] and key[pygame.K_s]:
        dx, dy = 5, 5
    else:
        if key[pygame.K_a]:
            dx = -5
        elif key[pygame.K_d]:
            dx = 5
        elif key[pygame.K_w]:
            dy = -5
        elif key[pygame.K_s]:
            dy = 5

    if countdown_finished:
        player.move_ip(dx, dy)
        player.x = max(0, min(player.x + dx, SCREEN_WIDTH - player.width))
        player.y = max(0, min(player.y + dy, SCREEN_HEIGHT - player.height))

    # Draw the remaining hits
    remaining_hits = max_hits - collision_count
    draw_text(f"HP: {remaining_hits}", text_font, WHITE, 10, 50)
    draw_text(f"TARGETS: {shot_square_collision_count}", text_font, WHITE, 10, 500)

    # Check for victory condition
    if shot_square_collision_count >= target_collisions_required:
        goal.set_volume(5)
        goal.play()
        draw_text("You Won!", text_font, WHITE, SCREEN_WIDTH // 2 - 70, SCREEN_HEIGHT // 2 - 15)
        pygame.display.update()
        pygame.time.wait(3000)  # Display the message for 3 seconds
        run = False  # End the game loop

    pygame.display.update()

pygame.quit()