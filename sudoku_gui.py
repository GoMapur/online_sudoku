from sudoku_alg import valid, solve, find_empty, generate_board
from copy import deepcopy
from sys import exit
import pygame
import time
import random

pygame.init()

class Board:
    '''A sudoku board made out of Tiles'''
    def __init__(self, window):
        self.board = generate_board()

        self.my_board_state_filled = None
        self.opponent_board_state_filled = None

        self.solvedBoard = deepcopy(self.board)

        self.my_tiles = [[Tile(self.board[i][j], window, i*60, j*60) for j in range(9)] for i in range(9)]
        self.opponent_tiles = [[Tile(self.board[i][j], window, i*60+540+30, j*60) for j in range(9)] for i in range(9)]

        self.window = window

        self.my_selection = None
        self.oppnent_selection = None


    def draw_board(self):
        '''Fills the board with Tiles and renders their values'''
        for shift_x in [0, 540+30]:
            for i in range(9):
                for j in range(9):
                    if j%3 == 0 and j != 0: #vertical lines
                        pygame.draw.line(self.window, (0, 0, 0), ((j//3)*180+shift_x, 0), ((j//3)*180+shift_x, 540), 4)

                    if i%3 == 0 and i != 0: #horizontal lines
                        pygame.draw.line(self.window, (0, 0, 0), (0+shift_x, (i//3)*180), (540+shift_x, (i//3)*180), 4)

                    self.my_tiles[i][j].draw((0,0,0), 1)
                    self.opponent_tiles[i][j].draw((0,0,0), 1)

                    if self.my_tiles[i][j].value != 0: #don't draw 0s on the grid
                        self.my_tiles[i][j].display(self.my_tiles[i][j].value, (21+(j*60), (16+(i*60))), (0, 0, 0))  #20,5 are the coordinates of the first tile
                    if self.opponent_tiles[i][j].value != 0: #don't draw 0s on the grid
                        self.opponent_tiles[i][j].display(self.opponent_tiles[i][j].value, (21+(j*60)+540+30, (16+(i*60))), (0, 0, 0))
        #bottom-most line
        pygame.draw.line(self.window, (0, 0, 0), (0, ((i+1) // 3) * 180), (540, ((i+1) // 3) * 180), 4)

    def deselect(self, tile):
        '''Deselects every tile except the one currently clicked'''
        for i in range(9):
            for j in range(9):
                if self.my_tiles[i][j] != tile:
                    self.my_tiles[i][j].selected = False

    def redraw(self, keys, wrong, time):
        '''redraws board with highlighted tiles'''
        self.window.fill((255,255,255))
        self.draw_board()
        for i in range(9):
            for j in range(9):
                if self.my_tiles[j][i].selected:  #draws the border on selected tiles
                    self.my_tiles[j][i].draw((50, 205, 50), 4)

                elif self.my_tiles[i][j].correct:
                    self.my_tiles[j][i].draw((34, 139, 34), 4)

                elif self.my_tiles[i][j].incorrect:
                    self.my_tiles[j][i].draw((255, 0, 0), 4)

        if len(keys) != 0: #draws inputs that the user places on board but not their final value on that tile
            for value in keys:
                self.my_tiles[value[0]][value[1]].display(keys[value], (21+(value[0]*60), (16+(value[1]*60))), (128, 128, 128))

        if wrong > 0:
            font = pygame.font.SysFont('Bauhaus 93', 30) #Red X
            text = font.render('X', True, (255, 0, 0))
            self.window.blit(text, (10, 554))

            font = pygame.font.SysFont('Bahnschrift', 40) #Number of Incorrect Inputs
            text = font.render(str(wrong), True, (0, 0, 0))
            self.window.blit(text, (32, 542))

        font = pygame.font.SysFont('Bahnschrift', 40) #Time Display
        text = font.render(str(time), True, (0, 0, 0))
        self.window.blit(text, (388, 542))
        pygame.display.flip()

class Tile:
    '''Represents each white tile/box on the grid'''
    def __init__(self, value, window, x1, y1):
        self.value = value
        self.window = window
        self.rect = pygame.Rect(x1, y1, 60, 60) #dimensions for the rectangle
        self.selected = False
        self.correct = False
        self.incorrect = False

    def draw(self, color, thickness):
        '''Draws a tile on the board'''
        pygame.draw.rect(self.window, color, self.rect, thickness)

    def display(self, value, position, color):
        '''Displays a number on that tile'''
        font = pygame.font.SysFont('lato', 45)
        text = font.render(str(value), True, color)
        self.window.blit(text, position)

    def clicked(self, mousePos):
        '''Checks if a tile has been clicked'''
        if self.rect.collidepoint(mousePos): #checks if a point is inside a rect
            self.selected = True
        return self.selected
