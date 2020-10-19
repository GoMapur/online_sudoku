from sudoku_alg import valid, solve, find_empty, generate_board
from copy import deepcopy
from sys import exit
import pygame
import time
import random

pygame.init()

class color:
    blue1 = (14,104,179)
    blue2 = (2,144,207)
    blue3 = (7,165,220)
    blue4 = (110,217,245)
    green = (11,168,105)
    black = (0, 0, 0)
    white = (224, 224, 224)
    red = (255, 0, 0)

class GameBoard:
    def __init__(self, window):
        self.window = window
        self.my_board = SudokuBoard(window, 0, True)
        self.opponent_board = SudokuBoard(window, 540 + 30, False)
        self.time = None

    def boards_init(self, board):
        self.my_board.board_init(board)
        self.opponent_board.board_init(board)
        self.my_board.game_ready = True
        self.opponent_board.game_ready = True
        self.time = time.time()

    def draw_entirety(self):
        self.window.fill(color.white)
        self.my_board.draw_board()
        self.opponent_board.draw_board()

        # elapsed = time.time() - self.time
        # passedTime = time.strftime("%H:%M:%S", time.gmtime(elapsed))
        # font = pygame.font.SysFont('Bahnschrift', 40) #Time Display
        # text = font.render(str(passedTime), True, color.black)
        # self.window.blit(text, (388, 542))

class SudokuBoard:
    '''A sudoku board made out of Tiles'''
    def __init__(self, window, shift_x, is_host):
        self.window = window
        self.shift_x = shift_x

        self.is_host = is_host

        self.game_ready = False
        self.opponent_ready = False
        self.tiles = [[Tile(window, i*60+shift_x, j*60, is_host) for j in range(9)] for i in range(9)]

        self.board = None
        self.solvedBoard = None
        self.board_state_original = None
        self.board_state_filled = None
        self.board_state_correct = None
        self.last_selection = None
        self.current_selection = None
        self.selection_color = None

        self.wrong = 0

    def board_init(self, board):
        self.board = deepcopy(board)
        self.solvedBoard = deepcopy(board)
        solve(self.solvedBoard)
        self.board_state_original = deepcopy(board)
        self.board_state_filled = [[0 for i in range(9)] for j in range(9)]
        self.board_state_correct = deepcopy(self.board_state_filled)
        for i in range(9):
            for j in range(9):
                self.tiles[i][j].solution_value = self.solvedBoard[i][j]
                if board[i][j] != 0:
                    self.tiles[i][j].placed_value = board[i][j]
                    self.tiles[i][j].show_wrong = False
                    self.tiles[i][j].selected = False
                    self.tiles[i][j].set_background_correct()
                    self.tiles[i][j].original_correct = True

    def draw_division_lines(self):
        if self.game_ready:
            shift_x = self.shift_x
            for i in range(10):
                for j in range(10):
                    if j%3 == 0: #vertical lines
                        pygame.draw.line(self.window, (0, 0, 0), ((j//3)*180+shift_x, 0), ((j//3)*180+shift_x, 540), 4)

                    if i%3 == 0: #horizontal lines
                        pygame.draw.line(self.window, (0, 0, 0), (0+shift_x, (i//3)*180), (540+shift_x, (i//3)*180), 4)

                    #bottom-most line
                    pygame.draw.line(self.window, (0, 0, 0), (0+shift_x, ((i+1) // 3) * 180), (540+shift_x, ((i+1) // 3) * 180), 4)

    def draw_board(self):
        '''Fills the board with Tiles and renders their values'''
        if self.game_ready:
            shift_x = self.shift_x
            for i in range(9):
                for j in range(9):
                    self.tiles[i][j].display_entirety()
            self.draw_division_lines()
            if self.wrong > 0:
                font = pygame.font.SysFont('Bauhaus 93', 30) #Red X
                text = font.render('X', True, color.red)
                self.window.blit(text, (10 + self.shift_x, 554))
                font = pygame.font.SysFont('Bahnschrift', 40) #Number of Incorrect Inputs
                text = font.render(str(self.wrong), True, color.black)
                self.window.blit(text, (32, 542))
            pygame.display.flip()
        elif self.opponent_ready:
            font = pygame.font.SysFont('Bahnschrift', 40)
            text = font.render("Waiting server to generate board", True, color.black)
            screen.blit(text, (175 + self.shift_x, 245))
        elif self.opponent_ready:
            font = pygame.font.SysFont('Bahnschrift', 40)
            text = font.render("Waiting opponent to connect", True, color.black)
            screen.blit(text, (175 + self.shift_x, 245))

    def deselect(self):
        '''Deselects every tile except the one currently clicked'''
        if self.game_ready:
            self.last_selection.set_border_unselected()

class Tile:
    '''Represents each white tile/box on the grid'''
    def __init__(self, window, x1, y1, is_host):
        self.window = window
        self.x1 = x1
        self.y1 = y1
        self.rect = pygame.Rect(x1, y1, 60, 60) #dimensions for the rectangle

        self.solution_value = 0
        self.placed_value = 0
        self.correct = False
        self.show_wrong = False
        self.selected = False

        self.border_color = color.black
        self.fill_color = color.white
        self.font_color = color.black
        self.font_bold = False
        self.border_width = 1

        self.font_shift_x = 21
        self.font_shift_y = 6

        self.is_host_tile = is_host
        self.original_correct = False

    def set_border_selected(self):
        self.selected = True
        self.border_width = 8
        self.border_color = color.green

    def set_border_unselected(self):
        self.selected = False
        self.border_width = 1
        self.border_color = color.black

    def set_background_correct(self):
        self.fill_color = color.blue1
        self.font_bold = True
        self.correct = True

    def set_background_wrong(self):
        self.fill_color = color.red
        self.font_bold = False
        self.correct = False

    def set_background_normal(self):
        self.fill_color = color.white
        self.font_bold = False
        self.correct = False

    def check_set_background(self):
        if self.is_correct():
            self.set_background_correct()
        elif self.show_wrong:
            self.set_background_wrong()
        else:
            self.set_background_normal()

    def is_correct(self):
        '''When a tile is correct, it cannot be changed anymore.'''
        return self.correct and self.solution_value == self.placed_value

    def try_enter(self):
        if self.solution_value == self.placed_value:
            self.correct = True
            return True
        else:
            self.placed_value = 0
            self.show_wrong = True
            self.set_background_wrong()
            return False

    def fill_rect(self):
        '''Draws a tile on the board'''
        pygame.draw.rect(self.window, self.fill_color, self.rect)

    def display_font(self):
        '''Displays a number on that tile'''
        if self.placed_value != 0:
            if self.is_host or (not self.is_host and self.original_correct):
                font = pygame.font.SysFont('lato', 45, bold = self.font_bold)
                text = font.render(str(self.placed_value), True, self.font_color)
                self.window.blit(text, (self.x1 + self.font_shift_x, self.y1 + self.font_shift_y))

    def draw_border(self):
        color = self.border_color
        width = self.border_width

        top_left = (self.x1, self.y1)
        top_right = (self.x1 + 60, self.y1)
        bottom_left = (self.x1, self.y1 + 60)
        bottom_right = (self.x1 + 60, self.y1 + 60)

        pygame.draw.line(self.window, color, top_left, top_right, width)
        pygame.draw.line(self.window, color, top_right, bottom_right, width)
        pygame.draw.line(self.window, color, bottom_right, bottom_left, width)
        pygame.draw.line(self.window, color, bottom_left, top_left, width)

    def display_entirety(self):
        self.fill_rect()
        self.draw_border()
        self.display_font()

    def clicked(self, mousePos):
        '''Checks if a tile has been clicked'''
        if self.rect.collidepoint(mousePos): #checks if a point is inside a rect
            self.set_border_selected()
        return self.selected
