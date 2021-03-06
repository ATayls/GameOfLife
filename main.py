import pygame
import numpy as np
import sys
from functools import reduce
from scipy.signal import convolve2d

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
        self.drawing = False
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
        """
        Calculate factors of integer n
        :param n: Integer
        :return:
        """
        return set(reduce(list.__add__,
                          ([i, n // i] for i in range(1, int(n ** 0.5) + 1) if n % i == 0)))

    def evolve(self,grid):
        """
        Evaluate grid following Conways GOL rules.
        Implemented using Scipy convolutions for speed efficiency
        :param grid: ndarray
        :return: ndarray
        """
        # create number of neighbours array 'neighbourhood'
        in_shp = np.shape(grid)
        kernal = np.array([
            [1, 1, 1],
            [1, 0, 1],
            [1, 1, 1],
        ])
        conv_grid = convolve2d(grid,kernal,boundary='fill',fillvalue=0)
        neighbourhood = conv_grid[1:in_shp[0]+1,1:in_shp[1]+1]

        # initialise empty grid
        new_state = np.zeros_like(grid)

        # If a cell is OFF and has exactly three neighbors that are ON, it turns ON.
        new_state[np.where((neighbourhood == 3) & (grid == 0))] = 1
        # If a cell is ON and has either two or three neighbors that are ON, it remains ON
        new_state[np.where((neighbourhood == 2) & (grid == 1))] = 1
        new_state[np.where((neighbourhood == 3) & (grid == 1))] = 1
        # If a cell is ON and has fewer than two neighbors that are ON, it turns OFF.
        new_state[np.where((neighbourhood < 2) & (grid == 1))] = 0
        # If a cell is ON and has more than three neighbors that are ON, it turns OFF.
        new_state[np.where((neighbourhood > 3) & (grid == 1))] = 0

        return new_state


    def calculate_x_y_blocks(self):
        """
        Calculate grid size in blocks closest to given number of elements
        :return:
        """
        # Desired number of elements
        elements = self.elements

        # Get factors of x and y window resolution
        factorsX = self.factors(self.xmax)
        factorsY = self.factors(self.ymax)

        # Find common factors
        C_factors = list(set(factorsX) & set(factorsY))

        #todo if no common factors
        if C_factors:

            # Create a dictionary of every possible number of elements that fits window size
            poss_elements = {}
            for i in C_factors:
                X_blocks = self.xmax / i
                Y_blocks = self.ymax / i
                element_n = X_blocks * Y_blocks
                if element_n not in poss_elements:
                    poss_elements[element_n] = []
                poss_elements[element_n].append([int(i), int(X_blocks), int(Y_blocks)])

            # find closest number of elements to input
            closest_el = min(poss_elements.keys(), key=lambda x:abs(x-elements))
            print('Number of elements set to ', closest_el)

            # set class attributes
            self.X_block_size = poss_elements[closest_el][0][0]
            self.Y_block_size = poss_elements[closest_el][0][0]
            self.X_blocks = poss_elements[closest_el][0][1]
            self.Y_blocks = poss_elements[closest_el][0][2]


    def handleInputEvents(self):
        """
        Pygame event handler
        :return:
        """
        for event in pygame.event.get():
            #QUIT
            if (event.type == pygame.QUIT):  # pygame issues a quit event, for e.g. by closing the window
                print("quitting")
                sys.exit(0)

            #drawing
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1: # left click
                    self.drawing = False
                elif event.button == 3: #right click:
                    self.erase = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.start = False
                if event.button == 1: # left click
                    self.drawing = True
                elif event.button == 3: #right click:
                    self.erase = True
            elif event.type == pygame.MOUSEMOTION:
                if self.drawing:
                    mouse_position = pygame.mouse.get_pos()
                    x, y = self.pixel2block(mouse_position[0],mouse_position[1])
                    self.world[x][y] = 1
                elif self.erase:
                    mouse_position = pygame.mouse.get_pos()
                    x, y = self.pixel2block(mouse_position[0],mouse_position[1])
                    self.world[x][y] = 0

            #Keyboard
            if (event.type == pygame.KEYDOWN):
                # New random world: key = N
                if event.key == pygame.K_n:
                    self.start = False
                    self.save = None
                    self.world = self.make_random_grid(self.X_blocks, self.Y_blocks)
                # Save world: key = S
                if event.key == pygame.K_s:
                    self.save = self.world
                # Reset to Saved world: key = R
                if event.key == pygame.K_r:
                    self.start = False
                    if not self.save is None:
                        self.world = self.save
                # Start / Pause game: key = Space
                if event.key == pygame.K_SPACE:
                    if self.start == False:
                        self.start = True
                    elif self.start == True:
                        self.start = False
                # Clear : key = C
                if event.key == pygame.K_c:
                    self.start = False
                    self.save = None
                    self.world = np.zeros_like(self.world)
                if event.key == pygame.K_ESCAPE:
                    sys.exit(0)  # quit on any key



    def createScreen(self):
        """
        Initialise pygame screen
        :return:
        """
        print('Available resolutions', pygame.display.list_modes(0))

        if not self.windowed:
            # the next two lines set up full screen options, to run in a window see below
            screen_width, screen_height = pygame.display.list_modes(0)[0]
            # we use the 1st resolution which is the largest, and ought to give us the full multi-monitor
            options = pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF
        else:
            screen_width, screen_height = (600,600)
            options = 0

        # create the screen with the options
        screen = pygame.display.set_mode((screen_width, screen_height), options)
        (self.xmax, self.ymax) = screen.get_size()
        print("screen created, size is:",self.xmax, self.ymax)

        return screen


    def draw_block(self,x,y,cell_color):
        """
        Draw a grid block in given colour to screen
        :param x: grid x pos
        :param y: grid y pos
        :param cell_color: rgb colour
        :return:
        """
        x *= self.X_block_size
        y *= self.Y_block_size
        pygame.draw.rect(screen, cell_color,
                         [x, y, self.X_block_size, self.Y_block_size])


    def pixel2block(self,x,y):
        """
        Convert a pixel x,y coord to containing block
        :param x:
        :param y:
        :return:
        """
        x_block = int((x+1)/self.X_block_size)
        y_block = int((y+1)/self.Y_block_size)
        return x_block, y_block


    def draw_grid(self):
        """
        Draw world grid to screen
        :return:
        """
        cell_number = 0
        for x in range(self.X_blocks):
            for y in range(self.Y_blocks):
                alive = self.world[x][y]
                cell_number += 1
                cell_color = self.alive_colour if alive else self.dead_colour
                self.draw_block(x, y, cell_color)


    def run_game(self):
        """
        Game loop
        :return:
        """
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
            clock.tick(60)
            if self.start:
                if self.save is None:
                    self.save = self.world
                self.world = self.evolve(self.world)
            self.draw_grid()
            pygame.display.flip()


if __name__ == '__main__':

    # New random world: key = N
    # Save world: key = S
    # Reset to Saved world: key = R
    # Start / Pause game: key = Space
    # Clear : key = C

    G = Game(20000, windowed=True)
    G.run_game()