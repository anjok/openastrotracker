import pygame
import random
import time

# This aimple script allows to test guiding during the day:
# - in a dark room, run the script on a computer about 5-7m away from the OAT
# - lift up the back of your OAT so the guider is slightly (1-2cm) above the RA ring when pointed to the computer
# - Use a second computer to run phd2 and kstars
# - connect, sync to about 65 degrees in DEC
# - point the OAT at the left side of the screen, so some stars are visible. Stars should move to the left in the guider
# - Enable tracking (Meade Command `:MT1#`) 
# - adjust the stars_speed so the stars are stationary (quit, change and run this script again)
# - calibrate, then guide
# - after about 8-12m you need to move to the left side again, as your stars have moved out of the screen. Then guide again for another 4 mins

# Configurable Parameters
num_stars = 500        # Number of stars to display
star_size = 1          # Size of the stars
stars_speed = 1.6        # Speed of stars moving in pixels per second
screen_resolution = (2048, 1280)  # Screen resolution of the MacBook
random_seed = 42       # Seed for reproducibility

# Initialize pygame
pygame.init()

# Create the screen in full-screen mode
screen = pygame.display.set_mode(screen_resolution, pygame.FULLSCREEN)
pygame.display.set_caption("Guiding Simulation")

# Set the background color (black)
background_color = (0, 0, 0)

# Set up the clock to control the frame rate
clock = pygame.time.Clock()

# Generate stars
random.seed(random_seed)  # Ensure repeatability
stars = []
for _ in range(num_stars):
    x = random.randint(0, screen_resolution[0])
    y = random.randint(0, screen_resolution[1])
    stars.append([x, y])

# Function to update star positions based on speed
def update_stars(stars, speed, delta_time):
    for star in stars:
        star[0] += speed * delta_time  # Move horizontally
        # Wrap around the screen horizontally
        if star[0] > screen_resolution[0]:
            star[0] = 0

# Main loop
running = True
start_time = time.time()

while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Calculate time difference
    delta_time = time.time() - start_time
    start_time = time.time()

    # Update star positions
    update_stars(stars, stars_speed, delta_time)

    # Fill the screen with the background color
    screen.fill(background_color)

    # Draw the stars
    for star in stars:
        pygame.draw.circle(screen, (255, 255, 255), (star[0], star[1]), star_size)

    # Update the display
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(30)

# Quit pygame
pygame.quit()
