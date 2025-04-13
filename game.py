import random
import pygame
import pgzrun

WIDTH = 500
HEIGHT = 500
rocket = Actor("rocket", (WIDTH // 2, HEIGHT - 50))
rocket_speed = 5
rocket_timer = 0
rocket_moving = False
game_time = 0
game_over_time = 0
game_started = False  # New variable to track if the game has started
show_info = False

background = Actor("background", (WIDTH // 2, HEIGHT // 2))

aliens = []
for _ in range(5):
    enemy_type = random.choice(["ufo1", "alien1"])
    alien = Actor(enemy_type, (random.randint(50, WIDTH - 50), random.randint(-100, HEIGHT // 4)))
    alien.type = enemy_type
    aliens.append(alien)

lasers = []
score = 0
lives = 3
game_over = False

heart_powerup = None
heart_spawn_time = random.randint(5, 10)
heart_speed = 2

bullet_powerup = None
bullet_spawn_time = random.randint(10, 20)
bullet_speed = 2
laser_count = 1
bullet_active_time = 0

def draw():
    background.draw()

    if not game_started:
        # Draw the start screen with the "Start" button
        screen.draw.text("Rocket Game", center=(WIDTH // 2, HEIGHT // 3), fontsize=60, color="white")
        screen.draw.text("Press 'Start' to Begin", center=(WIDTH // 2, HEIGHT // 2), fontsize=40, color="yellow")
        screen.draw.filled_rect(Rect((WIDTH // 2 - 50, HEIGHT // 2 + 50), (100, 40)), "green")
        screen.draw.text("Start", center=(WIDTH // 2, HEIGHT // 2 + 70), fontsize=30, color="white")
         # Info Button
        screen.draw.filled_rect(Rect((WIDTH // 2 - 50, HEIGHT // 2 + 100), (100, 40)), "blue")
        screen.draw.text("Info", center=(WIDTH // 2, HEIGHT // 2 + 120), fontsize=30, color="white")

    elif show_info:
        # Bilgi ekranını göster
        screen.draw.text("Rocket Game Info", center=(WIDTH // 2, HEIGHT // 3), fontsize=50, color="white")
        screen.draw.text("Use arrow keys to move.", center=(WIDTH // 2, HEIGHT // 2), fontsize=30, color="white")
        screen.draw.text("Press 'M' to shoot lasers.", center=(WIDTH // 2, HEIGHT // 2 + 40), fontsize=30, color="white")
        screen.draw.text("Avoid aliens and collect power-ups.", center=(WIDTH // 2, HEIGHT // 2 + 80), fontsize=30, color="white")
        screen.draw.filled_rect(Rect((WIDTH // 2 - 50, HEIGHT - 70), (100, 40)), "red")
        screen.draw.text("Back", center=(WIDTH // 2, HEIGHT - 50), fontsize=30, color="white")


    elif game_over:
        screen.draw.text("Game Over", center=(WIDTH // 2, HEIGHT // 2), fontsize=60, color="red")
        screen.draw.text(f"Score: {score}", center=(WIDTH // 2, HEIGHT // 2 + 60), fontsize=40, color="white")
        screen.draw.text(f"Time Survived: {game_time:.2f} seconds", center=(WIDTH // 2, HEIGHT // 2 + 100), fontsize=40, color="white")
    else:
        rocket.draw()
        for alien in aliens:
            alien.draw()
        for laser in lasers:
            screen.draw.filled_rect(laser, "yellow")
        screen.draw.text(f"Score: {score}", topright=(WIDTH - 20, 10), fontsize=30, color="white")
        screen.draw.text(f"Time: {int(game_time // 60)}:{int(game_time % 60):02d}", topleft=(10, 10), fontsize=30, color="white")

        heart_x = WIDTH - 200
        heart_y = 20
        if lives == 3:
            heart_image = Actor("fullheart", (heart_x, heart_y))
        elif lives == 2:
            heart_image = Actor("halfheart", (heart_x, heart_y))
        elif lives == 1:
            heart_image = Actor("quarterheart", (heart_x, heart_y))
        else:
            heart_image = None
        if heart_image:
            heart_image.draw()

        if heart_powerup:
            heart_powerup.draw()
        if bullet_powerup:
            bullet_powerup.draw()

        if bullet_active_time > 0:
            screen.draw.text(f"Bullet Active: {int(bullet_active_time)}s", topleft=(10, 30), fontsize=30, color="white")

def update():
    global game_over, score, lives, rocket_timer, rocket_moving, game_time, game_over_time
    global heart_powerup, heart_spawn_time, bullet_powerup, bullet_spawn_time, laser_count, bullet_active_time

    if not game_started:
        return  # Skip update logic if the game hasn't started

    if not game_over:
        game_time += 1 / 60

        if game_time > heart_spawn_time and heart_powerup is None:
            heart_powerup = Actor("heart", (random.randint(50, WIDTH - 50), -20))
        if heart_powerup:
            heart_powerup.y += heart_speed
            if heart_powerup.top > HEIGHT:
                heart_powerup = None
                heart_spawn_time = game_time + random.randint(10, 20)

        if game_time > bullet_spawn_time and bullet_powerup is None and laser_count == 1:
            bullet_powerup = Actor("bullet", (random.randint(50, WIDTH - 50), -20))
        if bullet_powerup:
            bullet_powerup.y += bullet_speed
            if bullet_powerup.top > HEIGHT:
                bullet_powerup = None
                bullet_spawn_time = game_time + random.randint(10, 20)

        if bullet_active_time > 0:
            bullet_active_time -= 1 / 60
            if bullet_active_time <= 0:
                laser_count = 1

        if keyboard.left and rocket.left > 0:
            rocket.image = "rocket_moves_left"
            rocket.x -= rocket_speed
            rocket_moving = True
        elif keyboard.right and rocket.right < WIDTH:
            rocket.image = "rocket_moves_right"
            rocket.x += rocket_speed
            rocket_moving = True
        elif keyboard.up and rocket.top > 0:
            rocket.image = "rocket_moves"
            rocket.y -= rocket_speed
            rocket_moving = True
        elif keyboard.down and rocket.bottom < HEIGHT:
            rocket.image = "rocket"
            rocket.y += rocket_speed
            rocket_moving = True

        if not rocket_moving:
            rocket_timer += 1
            if rocket_timer > 60:
                rocket.image = "rocket"
                rocket_timer = 0
        else:
            rocket_timer = 0
            rocket_moving = False

        lasers_to_remove = []
        for laser in lasers:
            laser.y -= 10
            laser_collided = False
            for alien in aliens[:]:
                alien_rect = Rect(alien.x, alien.y, alien.width, alien.height)
                if laser.colliderect(alien_rect):
                    aliens.remove(alien)
                    lasers_to_remove.append(laser)
                    score += 2 if alien.type == "ufo1" else 1
                    spawn_alien()
                    laser_collided = True
                    break
            if laser.y < 0 and not laser_collided:
                lasers_to_remove.append(laser)

        for laser in lasers_to_remove:
            if laser in lasers:
                lasers.remove(laser)

        for alien in aliens:
            alien.y += 3 if alien.type == "ufo1" else 2
            if alien.top > HEIGHT:
                alien.y = random.randint(-100, -40)
                alien.x = random.randint(50, WIDTH - 50)
            if rocket.colliderect(alien):
                aliens.remove(alien)
                spawn_alien()
                lives -= 1
                if lives == 0:
                    game_over = True
                    game_over_time = game_time

        if heart_powerup and rocket.colliderect(heart_powerup):
            lives = min(lives + 1, 3)
            heart_powerup = None
            heart_spawn_time = game_time + random.randint(10, 20)

        if bullet_powerup and rocket.colliderect(bullet_powerup):
            laser_count = 2
            bullet_active_time = 5
            bullet_powerup = None
            bullet_spawn_time = game_time + random.randint(10, 20)

def spawn_alien():
    alien_type = random.choice(["ufo1", "alien1"])
    alien = Actor(alien_type, (random.randint(50, WIDTH - 50), random.randint(-100, HEIGHT // 4)))
    alien.type = alien_type
    aliens.append(alien)

def on_mouse_down(pos):
    global game_started
    if not game_started and Rect((WIDTH // 2 - 50, HEIGHT // 2 + 50), (100, 40)).collidepoint(pos):
        game_started = True

def on_key_down(key):
    if key == keys.M and game_started and not game_over:
        if laser_count == 1:
            laser = Rect((rocket.x + rocket.width // 2 - 2, rocket.y), (4, 10))
            lasers.append(laser)
        elif laser_count == 2:
            laser_left = Rect((rocket.x + rocket.width // 2 - 10, rocket.y), (4, 10))
            laser_right = Rect((rocket.x + rocket.width // 2 + 6, rocket.y), (4, 10))
            lasers.extend([laser_left, laser_right])

pgzrun.go()
