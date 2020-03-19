import pygame
import numpy as np
import sys
from functools import reduce


class Game:
    def __init__(self, elements, windowed=False):
        """
        Initialise Game
        :param elements: Desired Number of Grid cells in GOL
        :param windowed: Run Game in window
        """
        self.windowed = windowed
        self.elements = elements

        self.start = False
        self.erase = False
        self.save = None

        self.alive_colour = (255, 255, 255)
        self.dead_colour = (0, 0, 0)

    @staticmethod
    def make_random_grid(x, y):
        """
        Create ndarray to represent game world
        :param x: number of rows
        :param y: number of cols
        :return:
        """
        grid = np.random.randint(2, size=(int(x), int(y)))
        return grid

    @staticmethod
    def factors(n):
        return set(reduce(list.__add__,
                          ([i, n // i] for i in range(1, int(n ** 0.5) + 1) if n % i == 0)))

    @staticmethod
    def get_num_neighbours(grid, row, col):
        num_neighbours = 0
        grid_shp = np.shape(grid)
        for i in range(-1, 2):
            for j in range(-1, 2):
                n_row = row + i
                n_col = col + j

                if (i == 0) and (j == 0):
                    continue
                elif (n_row < 0) or (n_row >= grid_shp[0]):
                    N_val = 0
                elif (n_col < 0) or (n_col >= grid_shp[1]):
                    N_val = 0
                else:
                    N_val = grid[n_row][n_col]

                num_neighbours += N_val

        return num_neighbours

    def evolve(self, grid):
        #todo implement faster method
        cell_number = 0
        new_state = np.zeros_like(grid)
        for row in range(self.X_blocks):
            for col in range(self.Y_blocks):
                NN = self.get_num_neighbours(grid, row, col)

                alive = grid[row][col]

                # If a cell is OFF and has exactly three neighbors that are ON, it turns ON.
                if not alive and NN == 3:
                    new_state[row][col] = 1
                # If a cell is ON and has either two or three neighbors that are ON, it remains ON
                if alive and (NN == 3 or NN == 2):
                    new_state[row][col] = 1
                # If a cell is ON and has fewer than two neighbors that are ON, it turns OFF.
                if alive and NN < 2:
                    new_state[row][col] = 0
                # If a cell is ON and has more than three neighbors that are ON, it turns OFF.
                if alive and NN > 3:
                    new_state[row][col] = 0

                cell_number += 1

        return new_state


    def calculate_x_y_blocks(self):
        elements = self.elements
        factorsX = self.factors(self.xmax)
        factorsY = self.factors(self.ymax)

        C_factors = list(set(factorsX) & set(factorsY))
        if C_factors:
            poss_elements = {}
            for i in C_factors:
                X_blocks = self.xmax / i
                Y_blocks = self.ymax / i
                element_n = X_blocks * Y_blocks
                if element_n not in poss_elements:
                    poss_elements[element_n] = []
                poss_elements[element_n].append([int(i), int(X_blocks), int(Y_blocks)])

            closest_el = min(poss_elements.keys(), key=lambda x:abs(x-elements))
            print('Number of elements set to ', closest_el)

            self.X_block_size = poss_elements[closest_el][0][0]
            self.Y_block_size = poss_elements[closest_el][0][0]
            self.X_blocks = poss_elements[closest_el][0][1]
            self.Y_blocks = poss_elements[closest_el][0][2]


    def handleInputEvents(self):
        for event in pygame.event.get():
            #QUIT
            if (event.type == pygame.QUIT):  # pygame issues a quit event, for e.g. by closing the window
                print("quitting")
                sys.exit(0)

            #Keyboard
            if (event.type == pygame.KEYDOWN):
                if event.key == pygame.K_n:
                    self.start = False
                    self.save = None
                    self.world = self.make_random_grid(self.X_blocks, self.Y_blocks)
                if event.key == pygame.K_s:
                    self.save = self.world
                if event.key == pygame.K_r:
                    self.start = False
                    if not self.save is None:
                        self.world = self.save
                if event.key == pygame.K_SPACE:
                    if self.start == False:
                        self.start = True
                    elif self.start == True:
                        self.start = False
                if event.key == pygame.K_b:
                    self.start = False
                    self.save = None
                    self.world = np.zeros_like(self.world)
                if event.key == pygame.K_ESCAPE:
                    sys.exit(0)  # quit on any key



    def createScreen(self):
        print('available resolutions', pygame.display.list_modes(0))

        if not self.windowed:
            # the next two lines set up full screen options, to run in a window see below
            screen_width, screen_height = pygame.display.list_modes(0)[0]
            # we use the 1st resolution which is the largest, and ought to give us the full multi-monitor
            options = pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF
        else:
            screen_width, screen_height = (600,600)
            options=0

        # create the screen with the options
        screen = pygame.display.set_mode((screen_width, screen_height), options)
        (self.xmax, self.ymax) = screen.get_size()
        print("screen created, size is:",self.xmax, self.ymax)

        return screen


    def draw_block(self,x,y,cell_color):
        x *= self.X_block_size
        y *= self.Y_block_size
        pygame.draw.rect(screen, cell_color,
                         [x, y, self.X_block_size, self.Y_block_size])


    def pixel2block(self,x,y):
        x_block = int((x+1)/self.X_block_size)
        y_block = int((y+1)/self.Y_block_size)
        return x_block, y_block


    def draw_grid(self):
        cell_number = 0
        for x in range(self.X_blocks):
            for y in range(self.Y_blocks):
                alive = self.world[x][y]
                cell_number += 1
                cell_color = self.alive_colour if alive else self.dead_colour
                self.draw_block(x, y, cell_color)


    def run_game(self):
        pygame.init()
        clock = pygame.time.Clock()

        global screen
        screen = self.createScreen()
        screen.fill((255, 255, 255))

        self.calculate_x_y_blocks()

        self.world = self.make_random_grid(self.X_blocks, self.Y_blocks)

        while True:
            self.handleInputEvents()
            pygame.display.update()
            clock.tick(10)
            if self.start:
                if self.save is None:
                    self.save = self.world
                self.world = self.evolve(self.world)
            self.draw_grid()
            pygame.display.flip()


if __name__ == '__main__':

    G = Game(20000, windowed=True)
    G.run_game()