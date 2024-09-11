import pygame
import sys
import random

pygame.init()

WIDTH, HEIGHT = 400, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Bird")

WHITE = (255, 255, 255)

clock = pygame.time.Clock()

# Load and scale images
bird_image = pygame.image.load('images/flappybird.png')
pipe_image = pygame.image.load('images/pipe2.png')
background_image = pygame.image.load('images/background.png')
coin_image = pygame.image.load('images/coin.png')

bird_image = pygame.transform.scale(bird_image, (34, 24))
pipe_image = pygame.transform.scale(pipe_image, (52, 200))
background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))
coin_image = pygame.transform.scale(coin_image, (30, 30))  # Adjust size as needed

# Flipped pipe image for the bottom pipe
pipe_image_flipped = pygame.transform.flip(pipe_image, False, True)

# Bird variables
bird_x, bird_y = 50, HEIGHT // 2
bird_y_velocity = 0
gravity = 0.5
flap_strength = -5

# Pipe variables
pipe_width = 52
pipe_height = 150
pipe_gap = 200
pipe_velocity = -5
pipe_frequency = 1500  # milliseconds
pipe_timer = pygame.USEREVENT
pygame.time.set_timer(pipe_timer, pipe_frequency)

pipes = []
coins = []

# Score and coin collected counter
score = 0
coins_collected = 0
total_coins_collected = 0
high_score = 0
font = pygame.font.Font(None, 36)

def load_high_score_and_total_coins():
    global high_score, total_coins_collected
    try:
        with open("highscore.txt", "r") as file:
            high_score = int(file.read())
    except FileNotFoundError:
        high_score = 0

    try:
        with open("total_coins.txt", "r") as file:
            total_coins_collected = int(file.read())
    except FileNotFoundError:
        total_coins_collected = 0

def save_high_score_and_total_coins():
    global high_score, total_coins_collected
    try:
        with open("highscore.txt", "w") as file:
            file.write(str(high_score))
    except Exception as e:
        print(f"Error saving high score: {e}")

    try:
        with open("total_coins.txt", "w") as file:
            file.write(str(total_coins_collected))
    except Exception as e:
        print(f"Error saving total coins: {e}")

def reset_high_score_and_total_coins():
    global high_score, total_coins_collected
    high_score = 0
    total_coins_collected = 0
    save_high_score_and_total_coins()

def draw_bird():
    screen.blit(bird_image, (bird_x, bird_y))

def draw_pipes():
    for pipe in pipes:
        screen.blit(pipe_image, (pipe[0], pipe[1]))
        screen.blit(pipe_image_flipped, (pipe[0], pipe[1] + pipe_height + pipe_gap))

def draw_coins():
    for coin in coins:
        screen.blit(coin_image, (coin[0], coin[1]))

def draw_score():
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))

def draw_high_score():
    high_score_text = font.render(f"High Score: {high_score}", True, WHITE)
    screen.blit(high_score_text, (WIDTH - high_score_text.get_width() - 10, 10))

def draw_coins_collected():
    coins_collected_text = font.render(f"Coins Collected this game: {coins_collected}", True, WHITE)
    screen.blit(coins_collected_text, (10, 50))

def draw_total_coins_collected():
    total_coins_text = font.render(f"Total Coins Collected: {total_coins_collected}", True, WHITE)
    screen.blit(total_coins_text, (10, 90))

def update_bird():
    global bird_y, bird_y_velocity
    bird_y_velocity += gravity
    bird_y += bird_y_velocity

def update_pipes_and_coins():
    global score
    min_distance = 200  # Minimum distance between consecutive pipes

    # Move pipes and coins to the left and remove off-screen objects
    for pipe in pipes:
        pipe[0] += pipe_velocity  # Move pipe to the left

        # Remove pipes that have gone off-screen
        if pipe[0] + pipe_width < 0:
            pipes.remove(pipe)
            score += 1

    for coin in coins:
        coin[0] += pipe_velocity  # Move coin to the left
        if coin[0] + coin_image.get_width() < 0:
            coins.remove(coin)

    # Add new pipes and coins if needed
    if len(pipes) == 0 or pipes[-1][0] < WIDTH - min_distance:
        top_pipe_height = random.randint(100, HEIGHT - 100 - pipe_gap)

        pipes.append([WIDTH, top_pipe_height])

        # Adjust coin placement to appear lower in the gap
        coin_x = WIDTH
        coin_y = random.randint(top_pipe_height + 30, top_pipe_height + pipe_gap - coin_image.get_height())
        
        # Ensure the coin_y does not exceed screen bounds
        coin_y = max(top_pipe_height + 30, min(coin_y, top_pipe_height + pipe_gap - coin_image.get_height()))

        # Ensure coin_x is horizontally within the gap
        coin_x_gap = random.randint(pipe_width, pipe_width + pipe_gap - coin_image.get_width())
        
        coins.append([coin_x + coin_x_gap, coin_y])

def check_collision():
    global bird_y
    bird_rect = pygame.Rect(bird_x, bird_y, bird_image.get_width(), bird_image.get_height())

    # Check if the bird hits the ground or ceiling
    if bird_y + bird_image.get_height() > HEIGHT or bird_y < 0:
        return True

    for pipe in pipes:
        # Create rectangles for the top and bottom pipes
        pipe_rect_top = pygame.Rect(pipe[0], pipe[1], pipe_width, pipe_height)
        pipe_rect_bottom = pygame.Rect(pipe[0], pipe[1] + pipe_height + pipe_gap, pipe_width, HEIGHT)

        # Check if the bird intersects with either part of the pipe
        if bird_rect.colliderect(pipe_rect_top) or bird_rect.colliderect(pipe_rect_bottom):
            return True

        # Check if the bird is above the top pipe
        if bird_y < pipe[1] and bird_x + bird_image.get_width() > pipe[0] and bird_x < pipe[0] + pipe_width:
            return True
    
    return False

def check_coin_collection():
    global score, coins_collected, total_coins_collected
    bird_rect = pygame.Rect(bird_x, bird_y, bird_image.get_width(), bird_image.get_height())

    for coin in coins:
        coin_rect = pygame.Rect(coin[0], coin[1], coin_image.get_width(), coin_image.get_height())
        if bird_rect.colliderect(coin_rect):
            coins.remove(coin)
            score += 5  # Increase score by 5 or any other value
            coins_collected += 1  # Increment the coin collected counter
            total_coins_collected += 1  # Increment the total coins collected counter
            break

def game_over_screen():
    global score, high_score, coins_collected, total_coins_collected
    if score > high_score:
        high_score = score
        save_high_score_and_total_coins()
    
    while True:
        screen.blit(background_image, (0, 0))
        game_over_text = font.render("Game Over!", True, WHITE)
        play_again_text = font.render("Press R to Restart or Q to Quit", True, WHITE)
        reset_high_score_text = font.render("Press H to Reset Highscore&Coins", True, WHITE)
        reset_coins_text = font.render("Press C to Reset Total Coins", True, WHITE)
        screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 100))
        screen.blit(play_again_text, (WIDTH // 2 - play_again_text.get_width() // 2, HEIGHT // 2 - 60))
        screen.blit(reset_high_score_text, (WIDTH // 2 - reset_high_score_text.get_width() // 2, HEIGHT // 2))
        screen.blit(reset_coins_text, (WIDTH // 2 - reset_coins_text.get_width() // 2, HEIGHT // 2 + 40))
        draw_high_score()
        draw_total_coins_collected()
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_r:
                    coins_collected = 0
                    return
                if event.key == pygame.K_h:
                    reset_high_score_and_total_coins()
                    coins_collected = 0
                    return
                if event.key == pygame.K_c:
                    total_coins_collected = 0
                    save_high_score_and_total_coins()
                    coins_collected = 0
                    return

def main_game_loop():
    global bird_x, bird_y, bird_y_velocity, score, coins, coins_collected, total_coins_collected

    while True:
        # Reset game state
        bird_x, bird_y = 50, HEIGHT // 2
        bird_y_velocity = 0
        score = 0
        coins = []
        coins_collected = 0 

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        bird_y_velocity = flap_strength
                    if event.key == pygame.K_r:
                        break
                if event.type == pipe_timer:
                    update_pipes_and_coins()
            
            update_bird()
            update_pipes_and_coins()
            check_coin_collection() 

            if check_collision():
                save_high_score_and_total_coins()
                game_over_screen() 
                break 

            screen.blit(background_image, (0, 0))
            draw_pipes()
            draw_coins()
            draw_bird()
            draw_score()
            draw_high_score()  
            draw_coins_collected() 
            draw_total_coins_collected() 
            
            pygame.display.flip()
            clock.tick(30)

load_high_score_and_total_coins()
main_game_loop()

