# Name: Snake
# Author: G.G.Otto
# Date: 5/10/21
# Version: 2.2

import pygame, random, math
from pygame.locals import *
import gamesetup as gs
from os.path import isfile

class Snake:
    '''represents the snake'''

    def __init__(self, game, pos):
        '''Snake(Game, (x,y)) -> Snake
        constructs the snake at starting pos'''
        # game sizes
        self.block = game.get_block_size()
        self.grid = game.get_grid_size()
        
        # load all images
        self.heads = {}
        self.ends = {}
        for i in range(0, 360, 90):
            self.heads[i] = gs.remove_bg(f"head{i}.png")
            self.ends[i] = gs.remove_bg(f"head{i}_end.png")
        self.tail = gs.remove_bg("tail.png")

        self.canUseEvents = False
        self.snakeHead = 90
        self.pos = pos
        self.game = game
        self.stopped = False
        self.keys = {K_RIGHT: 0, K_UP: 90, K_LEFT: 180, K_DOWN: 270}
        self.tails = [pos for i in range(3)]
        self.turns = []

    def is_dead(self):
        '''Snake.is_dead() -> bool
        returns if the snake is dead'''
        return self.stopped

    def get_pos(self):
        '''Snake.get_pos() -> (x,y)
        returns the position of the snake'''
        return self.pos

    def get_tail(self):
        '''Snake.get_tail() -> list
        returns the tail of the snake'''
        return self.tails

    def add_length(self):
        '''Snake.add_length() -> None
        adds a new length to the snake'''
        self.tails.append(self.tails[-1])

    def forward(self):
        '''Snake.forward() -> None
        moves the snake forward'''
        if self.stopped: return
        if self.snakeHead == 90:
            pos = self.pos[0], self.pos[1] - self.block
        elif self.snakeHead == 180:
            pos = self.pos[0] - self.block, self.pos[1]
        elif self.snakeHead == 270:
            pos = self.pos[0], self.pos[1] + self.block
        else:
            pos = self.pos[0] + self.block, self.pos[1]
        self.canUseEvents = True

        # check if wrong
        if pos in self.tails or (pos[0] < 0 or pos[1] < 0 or pos[0] > self.grid[0]*self.block or
            pos[1] > self.grid[1]*self.block):
            self.heads = self.ends
            self.stopped = True
            return
        
        self.pos = pos
        last = self.tails[0]
        for i in range(1, len(self.tails)):
            current = self.tails[i]
            self.tails[i] = last
            last = current
        self.tails[0] = pos

    def event(self, event):
        '''Snake.event(event) -> None
        deals with a keypress'''
        if not self.canUseEvents or self.stopped: return
        if event.key in self.keys:
            self.turns.append(self.keys[event.key])

    def update(self):
        '''Snake.update() -> None
        updates the snake and tail'''
        # turn snake
        for turn in self.turns[:]:
            if (turn + 180) % 360 != self.snakeHead and turn != self.snakeHead:
                self.snakeHead = turn
                self.turns.remove(turn)
                break
            self.turns.remove(turn)
            
        self.forward()
        for tail in self.tails:
            self.game.blit(self.tail, tail, True, True)
        self.game.blit(self.heads[self.snakeHead], self.pos, True, True)

class Game(gs.Game):
    '''represents the game'''

    def __init__(self):
        '''Game() -> Game
        constructs the game'''
        gs.Game.__init__(self)

        # set up display
        pygame.display.set_caption("Snake")
        self.display = pygame.display.set_mode((650, 650))
        pygame.display.set_icon(gs.remove_bg("head90.png"))
        self.screen = gs.Camera(self.display.get_size())

        # colors and attributes
        self.OUT = 0, 0, 0
        self.IN = 57, 217, 105
        self.LINE = 28, 147, 62
        self.factor = 1
        self.gridSize = (19,19)
        self.blockSize = 30
        self.border = int(self.blockSize/2)
        self.score = 0
        self.high = self.get_high()
        self.scoreFont = pygame.font.SysFont("Arial", 30, True)
        self.stopped = True
        self.startFont = pygame.font.SysFont("Arial", 100, True)
        self.startClock = gs.Clock(3)
        self.startClock.start()

        # game objects
        pos = (self.gridSize[0]/2)*self.blockSize, (self.gridSize[1]/2)*self.blockSize
        self.snake = Snake(self, pos)
        self.screen.center_at(pos)
        self.apple = gs.remove_bg("apple.png")
        self.move_apple()
        
    def get_grid_size(self):
        '''Game.get_grid_size() -> tuple
        returns the grid size of the game'''
        return self.gridSize

    def get_block_size(self):
        '''Game.get_block_size() -> None
        returns the block size'''
        return self.blockSize

    def get_border(self):
        '''Game.get_border() -> int
        returns the width of the border'''
        return self.width

    def shadow_text(self, text, pos, color, font):
        '''Game.shadow_text(str, (x,y), Color, SysFont) -> None
        adds shadow text to the screen'''
        text = font.render(text, True, color)
        self.blit(gs.set_alpha(text, 100), (pos[0]+1, pos[1]+2), True, True, self.display)
        self.blit(text, pos, True, True, self.display)

    def move_apple(self):
        '''Game.move_apple() -> None
        moves the apple to a different place'''
        self.applePos = random.randrange(self.border, (self.gridSize[0])*self.blockSize,
            self.blockSize), random.randrange(self.border, (self.gridSize[1])*self.blockSize, self.blockSize)
        while self.applePos in self.snake.get_tail():
             self.applePos = random.randrange(self.border, (self.gridSize[0])*self.blockSize,
                self.blockSize), random.randrange(self.border, (self.gridSize[1])*self.blockSize, self.blockSize)

    def event(self, event):
        '''Game.event(event) -> None
        deals with an event'''
        if event.type == KEYDOWN:
            self.snake.event(event)
            if event.key == K_SPACE and self.stopped and self.startClock.get_time() == 4:
                self.__init__()

    def update(self):
        '''Game.update() -> None
        updates the game'''
        # start timer
        if self.startClock.get_time() < 3:
            self.display.fill("black")
            self.shadow_text(str(3 - int(self.startClock.get_time())), (325, 325), "white", self.startFont)
            pygame.display.update()
        elif self.startClock.get_time() == 3:
            self.stopped = False
            self.startClock.set_time(4)
            
        if self.stopped: return
        self.screen.fill(self.LINE)

        # update grid
        self.screen.rect(self.IN, (0, 0, self.gridSize[0]*self.blockSize, self.gridSize[1]*self.blockSize))
        for i in range(self.gridSize[0]+1):
            self.screen.line(self.LINE, (i*self.blockSize, 0),
                (i*self.blockSize, self.gridSize[1]*self.blockSize), 1)
        for i in range(self.gridSize[1]+1):
            self.screen.line(self.LINE, (0, i*self.blockSize),
                (self.gridSize[0]*self.blockSize, i*self.blockSize), 1)

        self.snake.update()

        # update apple
        if self.snake.get_pos() == self.applePos:
            self.snake.add_length()
            self.score += 1
            self.applePos = None
            self.after(400, self.move_apple)
        if self.applePos != None: self.blit(self.apple, self.applePos, True, True)

        # add everything on display
        self.display.blit(self.screen, (0,0))
        pygame.draw.rect(self.display, self.LINE, (0,0,700,700), 20)
        self.shadow_text(str(self.score), (325, 20), "black", self.scoreFont)
        pygame.display.update()
        pygame.time.wait(140)

        if self.snake.is_dead(): self.end_game()

    def end_game(self):
        '''Game.end_game() -> None
        ends the game'''
        self.shadow_text(str("GAME OVER!"), (325, 325), "white", self.startFont)
        self.stopped = True

        # deal with high score
        if self.set_high(self.score): add = " (New!)"
        else: add = ""
        self.shadow_text("High: "+str(self.high)+add, (325, 627), "black", pygame.font.SysFont("Arial", 25, True))

        pygame.display.update()

    def get_high(self):
        '''Game.get_high() -> None
        returns the game's high score'''
        if not isfile("high.txt"):
            return 0

        file = open("high.txt")
        high = file.read()
        file.close()
        return int(high)

    def set_high(self, high):
        '''Game.set_high(int) -> None
        sets the game's high score'''
        if high > self.high:
            file = open("high.txt", "w")
            file.write(str(high))
            file.close()
            self.high = high
            return True
        return False

pygame.init()
Game().mainloop()
