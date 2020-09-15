# importing all modules
import pygame as pg
import neat
from random import randint, choice, random

# initialising pygame
pg.init()
pg.font.init()

# some constants and the screen
screen_width, screen_height = 1100, 400
screen = pg.display.set_mode((screen_width, screen_height))

# colors
WHITE = 255, 255, 255
BLACK = 0, 0, 0

# font
font = pg.font.Font('freesansbold.ttf', 32)

# fps variables
fps = 20
fps_clock = pg.time.Clock()

# current speed of the game and the maximum speed reached
speed = 15
high_speed = 0

class Background:
    # cloud class for the clouds (of course!)
    class Cloud:
        def __init__(self):
            # random position and speed
            self.x = randint(0, screen_width)
            self.y = randint(0, screen_height - 200)
            self.speed = randint(1, speed // 3)

            # main image of the clod resized
            self.image = pg.transform.scale(pg.image.load("images\\cloud.png"), (60, 30))

        def move(self):
            # drawing the cloud
            screen.blit(self.image, (self.x, self.y))

            # moving x position
            self.x -= self.speed

            # if right side of cloud exits the screen, then restart it
            if self.x <= -100:
                self.x = screen_width
                self.y = randint(0, screen_height - 200)
                self.speed = randint(3, speed // 3)
                

    def __init__(self):
        # main background

        # 5 clouds
        self.clouds = [self.Cloud() for _ in range(5)]

        # 2 floors for moving effect
        self.floor1 = pg.transform.scale(pg.image.load("images/floor.png"), (screen_width, screen_height // 40))
        self.floor2 = pg.transform.scale(pg.image.load("images/floor.png"), (screen_width, screen_height // 40))
        self.floor_y = screen_height - 100

        # x position of both floors
        self.floor1_x = 0
        self.floor2_x = screen_width

    def display(self):
        # drawing the floors
        screen.blit(self.floor1, (self.floor1_x, self.floor_y))
        screen.blit(self.floor2, (self.floor2_x, self.floor_y))

        # moving the floors
        self.floor1_x -= speed
        self.floor2_x -= speed

        # redrawing the floors
        if self.floor1_x <= -screen_width:
            self.floor1_x = screen_width
        elif self.floor2_x <= -screen_width:
            self.floor2_x = screen_width

        # moving all cluds in the scene
        for cloud in self.clouds:
            cloud.move()

class Dino:
    def __init__(self, genome, config):
        self.div_counter = 13  # just a counter to scale the images

        self.images = [
            pg.transform.scale(pg.image.load("images\\dino1.png"), (screen_width // self.div_counter, screen_width // self.div_counter)),
            pg.transform.scale(pg.image.load("images\\dino2.png"), (screen_width // self.div_counter, screen_width // self.div_counter))
        ]

        self.image = self.images[0]
        self.time_stamp = 0

        self.rect = None

        # position variables
        self.ground_level = screen_height - 150
        self.x = 150
        self.y = self.ground_level

        # motion variables
        self.vel = 65
        self.grav = 13
        self.jumping = False

        # neat-python variables
        self.genome = genome
        self.genome.fitness = 0
        self.net = neat.nn.FeedForwardNetwork.create(self.genome, config)

    def increase_fitness_by(self, num):
        # increasing the fitness of the dino
        self.genome.fitness += num

    def think(self, *args):
        # generating output for input
        output = self.net.activate(*args)[0]

        if output > 0.5:
            self.jump()

    def iterate_image(self):
        # give the dino a running effect
        if self.time_stamp % 2 == 0:
                self.image = self.images[1]
        else:
            self.image = self.images[0]

    def display(self):
        # displaying the dinosaur and checking for jumps
        self.check_jump_dino()

        if self.on_ground():
            self.iterate_image()
            self.reset_movement()

        self.rect = screen.blit(self.image, (self.x, self.y))
        self.time_stamp += 1

    # jumping functions
    def jump(self):
        self.jumping = True
        self.image = pg.transform.scale(pg.image.load("images\\dinoj.png"), (screen_width // self.div_counter, screen_width // self.div_counter))

    def check_jump_dino(self):
        if self.jumping:
            self.y -= self.vel
            self.vel -= self.grav

    def reset_movement(self):
        # reset the motion variables
        self.vel = 65
        self.grav = 13
        self.jumping = False

    def on_ground(self):
        # checking if the dinosaur is on ground
        return self.y >= self.ground_level

class Cactus:
    def __init__(self, x=screen_width):
        # generating random image for cactus
        image_index = randint(1, 3) 
        self.img = pg.image.load(f"images\\cactus{image_index}.png")

        # position variables
        self.x = x
        self.y = screen_height - 80 - self.img.get_height()

        # rect variable for collision detection
        self.rect = None

    def move(self):
        # moving the cactus
        self.x -= speed

    def display(self):
        # displaying the cactus
        self.rect = screen.blit(self.img, (self.x, self.y))

    def off_screen(self):
        # checking if the cactus has passes the screen
        return self.x <= 0

    def collide_dino(self, dino_rect):
        # checking if dino collides with cactus
        return self.rect.colliderect(dino_rect)

class GameEnv:
    def __init__(self):
        # setting the background and dinos
        self.bg = Background()
        self.cacti = [Cactus(), Cactus(screen_width * 1.5)]
        self.dinos = []

        # the stats
        self.score = 0
        self.generation = 0

    def add_dino(self, genome, config):
        # add a dino according to genome and config
        self.dinos.append(Dino(genome, config))

    def display_all(self):
        # display the background and dinos
        self.bg.display()

        for dino in self.dinos:
            dino.display()

    def manage_cactus(self):
        to_remove = []

        for cactus in self.cacti:
            # moving and displaying the cactus
            cactus.move()
            cactus.display()

            # if a cactus exits the screen, increase the score, add a cactus and remove the exited cactus
            if cactus.off_screen():
                self.score += 1
                self.cacti.append(Cactus())
                to_remove.append(cactus)

        for remove in to_remove:
            self.cacti.remove(remove)

    def check_removal(self):
        to_remove = []

        for cactus in self.cacti:

            cactus.display()

            for dino in self.dinos:

                if cactus.collide_dino(dino.rect):
                    # dino collides with cactus remove it
                    to_remove.append(dino)
                else:
                    # increase dino fitness by one
                    dino.increase_fitness_by(1 / len(self.cacti))


        for remove in to_remove:
            try:
                remove.genome.fitness -= 5
                self.dinos.remove(remove)
            except:
                pass

    def get_active_cactus(self):
        # give the cactus infront of the dino
        for cactus in self.cacti:
            if cactus.x > 150:
                return cactus
        return Cactus()

    def get_info(self, dino):
        active_cactus = self.get_active_cactus()

        return (
            dino.x,
            dino.y,
            active_cactus.x,
            active_cactus.y,
            speed
        )

    def think_all(self):
        # telling all dinos to think and jump if neccessary
        for dino in self.dinos:
            dino.think(self.get_info(dino))

    def all_dead(self):
        # checking if all dinos are dead
        return len(self.dinos) == 0

    def reset(self):
        # reset the environment
        self.cacti = [Cactus(), Cactus(screen_width * 1.5)]
        self.dinos = []

        self.score = 0
        self.generation += 1

        global speed
        speed = 15

env = GameEnv()

def eval_genomes(genomes, config):
    global speed
    global fps
    global high_speed

    # adding the dinos to the environment
    for genome_id, genome in genomes:
        env.add_dino(genome, config)

    while True:
        screen.fill(WHITE)

        # increase the speed
        if speed < 30:
            speed += 0.03

        # env functions
        env.display_all()
        env.manage_cactus()
        env.check_removal()
        env.think_all()

        # check the generation loop
        if env.all_dead():
            env.reset()
            break

        # manage the high speed
        if speed > high_speed:
            high_speed = speed

        # show the stats
        screen.blit(font.render(f"Generation: {env.generation}", True, BLACK), (10, screen_height - 100))
        screen.blit(font.render(f"Speed: {int(speed)}", True, BLACK), (10, screen_height - 130))
        screen.blit(font.render(f"Highest Speed: {int(high_speed)}", True, BLACK), (10, screen_height - 160))
        screen.blit(font.render(f"Score: {env.score}", True, BLACK), (10, screen_height - 70))
        screen.blit(font.render(f"Dinos Alive: {len(env.dinos)}", True, BLACK), (10, screen_height - 40))
        
        # managing events
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                quit()

            if event.type == pg.KEYDOWN:
                if event.key == pg.K_UP:
                    fps += 5
                elif event.key == pg.K_DOWN:
                    fps -= 5

                if event.key == pg.K_w:
                    speed += 1

        # managing fps
        pg.display.update()
        fps_clock.tick(fps)

# main function for neat
def main():
    config_file = "config.txt"

    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_file)

    p = neat.Population(config)

    p.add_reporter(neat.StdOutReporter(True))
    p.add_reporter(neat.StatisticsReporter())

    winner = p.run(eval_genomes, 5000)
    print(f"Best genome:\n {winner}")

if __name__ == "__main__":
    main()
