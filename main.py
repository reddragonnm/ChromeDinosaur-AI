import pygame as pg
import neat
from random import randint, choice, random
from collections import deque

pg.init()
pg.font.init()

screen_width, screen_height = 1100, 400
screen = pg.display.set_mode((screen_width, screen_height))

WHITE = 255, 255, 255

fps = 20
fps_clock = pg.time.Clock()

speed = 15

class Background:
    def __init__(self):
        self.floor = pg.transform.scale(pg.image.load("images/floor.png"), (screen_width, screen_height // 40))
        self.floor_y = screen_height - 100

    def display(self):
        screen.blit(self.floor, (0, self.floor_y))

class Dino:
    def __init__(self, genome, config):
        div_counter = 13

        self.images = [
            pg.transform.scale(pg.image.load("images\\d1.png"), (screen_width // div_counter, screen_width // div_counter)),
            pg.transform.scale(pg.image.load("images\\d2.png"), (screen_width // div_counter, screen_width // div_counter))
        ]

        self.image = self.images[0]
        self.time_stamp = 0

        self.rect = None

        self.ground_level = screen_height - 150
        self.x = 150
        self.y = self.ground_level

        self.vel = 50
        self.grav = 8

        self.jumping = False

        self.genome = genome
        self.genome.fitness = 0
        self.net = neat.nn.FeedForwardNetwork.create(self.genome, config)

    def increase_fitness_by(self, num):
        self.genome.fitness += 1

    def think(self, *args):
        output = self.net.activate(*args)[0]

        if output > 0.5:
            self.jump()

    def iterate_image(self):
        if self.time_stamp % 2 == 0:
                self.image = self.images[1]
        else:
            self.image = self.images[0]

    def display(self):
        self.check_jump_dino()

        if self.on_ground():
            self.iterate_image()
            self.reset_movement()

        self.rect = screen.blit(self.image, (self.x, self.y))
        self.time_stamp += 1

    def jump(self):
        self.jumping = True

    def check_jump_dino(self):
        if self.jumping:
            self.y -= self.vel
            self.vel -= self.grav

    def reset_movement(self):
        self.vel = 50
        self.grav = 8
        self.jumping = False

    def on_ground(self):
        return self.y >= self.ground_level

class Cactus:
    def __init__(self):
        self.x = screen_width
        self.y = screen_height - 150

        image_index = randint(1, 5)
        self.img = pg.image.load(f"images\\c{image_index}.png")

        self.rect = None

    def move(self):
        self.x -= speed

    def display(self):
        self.move()
        self.rect = screen.blit(self.img, (self.x, self.y))

    def off_screen(self):
        return self.x <= 0

    def collide_dino(self, dino_rect):
        return self.rect.colliderect(dino_rect)

class GameEnv:
    def __init__(self):
        self.bg = Background()
        self.cacti = [Cactus()]
        self.dinos = []

        self.score = 0
        self.generation = 0

    def add_dino(self, genome, config):
        self.dinos.append(Dino(genome, config))

    def display_all(self):
        self.bg.display()

        for dino in self.dinos:
            dino.display()

    def manage_cactus(self):
        to_remove = []

        for cactus in self.cacti:
            cactus.display()
            if cactus.off_screen():
                self.cacti.append(Cactus())
                to_remove.append(cactus)

        for remove in to_remove:
            self.cacti.remove(remove)

        # if random() > 0.99:
        #     self.cacti.append(Cactus())

    def check_removal(self):
        to_remove = []

        for cactus in self.cacti:
            cactus.display()
            for dino in self.dinos:
                if cactus.collide_dino(dino.rect):
                    to_remove.append(dino)

        for remove in to_remove:
            try:
                remove.genome.fitness -= 5
                self.dinos.remove(remove)
            except:
                pass

    def get_active_cactus(self):
        for cactus in self.cacti:
            if cactus.x > 150:
                return cactus
        return Cactus()

    def get_info(self, dino, active_cactus):
        return (
            dino.x,
            dino.y,
            active_cactus.x,
            active_cactus.y,
            speed
        )

    def think_all(self):
        active_cactus = self.get_active_cactus()

        for dino in self.dinos:
            dino.think(self.get_info(dino, active_cactus))

    def all_dead(self):
        return len(self.dinos) == 0

    def reset(self):
        self.bg = Background()
        self.cacti = [Cactus()]
        self.dinos = []

        self.score = 0
        self.generation += 1

        global speed
        speed = 15

env = GameEnv()

def eval_genomes(genomes, config):
    global speed

    for genome_id, genome in genomes:
        env.add_dino(genome, config)

    while True:
        screen.fill(WHITE)

        if speed < 30:
            speed += 0.03

        env.display_all()
        env.manage_cactus()
        env.check_removal()
        env.think_all()

        if env.all_dead():
            env.reset()
            break
        
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                quit()

        pg.display.update()
        fps_clock.tick(fps)

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
