from sudoku_gui import *
from sudoku_alg import valid, solve, find_empty, generate_board

screen = pygame.display.set_mode((540*2 + 30, 590))
screen.fill((255, 255, 255))
pygame.display.set_caption("Sudoku")
icon = pygame.image.load("icon.png")
pygame.display.set_icon(icon)

game = GameBoard(screen)
board = generate_board()
game.boards_init(board)
game.draw_entirety()

game.my_board.tiles[0][0].set_border_selected()
game.draw_entirety()
