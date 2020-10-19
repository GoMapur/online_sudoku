import sys
from sys import stdin, exit
from sudoku_gui import *
from sudoku_alg import valid, solve, find_empty, generate_board
from copy import deepcopy
from sys import exit
import pygame
import time
import random
from pygase import Client

### SETUP ###

# Subclass pygase classes to scope event handlers and game-specific variables.
class SudokuClient(Client):
    def __init__(self):
        super().__init__()
        self.player_id = None
        self.match_id = None
        # The backend will send a "PLAYER_CREATED" event in response to a "JOIN" event.
        self.register_event_handler("PLAYER_CREATED", self.on_player_created)

    # "PLAYER_CREATED" event handler
    def on_player_created(self, player_id):
        # Remember the id the backend assigned the player.
        self.player_id = player_id

### MAIN PROCESS ###
if __name__ == "__main__":
    # Create a client.
    client = SudokuClient()
    # Connect the client, let the player input a name and join the server.
    client.connect_in_thread(hostname="localhost", port=8080)
    client.dispatch_event("JOIN")

    # Wait until "PLAYER_CREATED" has been handled.
    while client.player_id is None:
        pass

    # Initialize a pygame screen.
    pygame.init()
    screen = pygame.display.set_mode((540*2 + 30, 590))
    screen.fill((255, 255, 255))
    pygame.display.set_caption("Sudoku")
    icon = pygame.image.load("icon.png")
    pygame.display.set_icon(icon)
    screen = screen
    game_board = GameBoard(screen)



    # Start the actual main loop.
    while True:
        with client.access_game_state() as game_state:

        elapsed = time.time() - startTime
        passedTime = time.strftime("%H:%M:%S", time.gmtime(elapsed))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                connection.Send({"action": "OpponentLeft"})
                exit() #so that it doesnt go to the outer run loop

            elif event.type == pygame.MOUSEBUTTONUP: #allow clicks only while the board hasn't been solved
                mousePos = pygame.mouse.get_pos()
                for i in range(9):
                    for j in range (9):
                        if board.my_tiles[i][j].clicked(mousePos):
                            selected = i,j
                            board.deselect(board.my_tiles[i][j]) #deselects every tile except the one currently clicked
                            connection.Send({"action": "OpponentMove"})

            elif event.type == pygame.KEYDOWN:
                if board.board[selected[1]][selected[0]] == 0 and selected != (-1,-1):
                    if event.key == pygame.K_1:
                        keyDict[selected] = 1
                        connection.Send({"action": "OpponentMove"})

                    if event.key == pygame.K_2:
                        keyDict[selected] = 2
                        connection.Send({"action": "OpponentMove"})

                    if event.key == pygame.K_3:
                        keyDict[selected] = 3
                        connection.Send({"action": "OpponentMove"})

                    if event.key == pygame.K_4:
                        keyDict[selected] = 4
                        connection.Send({"action": "OpponentMove"})

                    if event.key == pygame.K_5:
                        keyDict[selected] = 5
                        connection.Send({"action": "OpponentMove"})

                    if event.key == pygame.K_6:
                        keyDict[selected] = 6
                        connection.Send({"action": "OpponentMove"})

                    if event.key == pygame.K_7:
                        keyDict[selected] = 7
                        connection.Send({"action": "OpponentMove"})

                    if event.key == pygame.K_8:
                        keyDict[selected] = 8
                        connection.Send({"action": "OpponentMove"})

                    if event.key == pygame.K_9:
                        keyDict[selected] = 9
                        connection.Send({"action": "OpponentMove"})

                    elif event.key == pygame.K_BACKSPACE or event.key == pygame.K_DELETE:  # clears tile out
                        if selected in keyDict:
                            board.my_tiles[selected[1]][selected[0]].value = 0
                            del keyDict[selected]
                            connection.Send({"action": "OpponentMove"})

                    elif event.key == pygame.K_RETURN:
                        if selected in keyDict:
                            if keyDict[selected] != board.solvedBoard[selected[1]][selected[0]]: #clear tile when incorrect value is inputted
                                wrong += 1
                                board.my_tiles[selected[1]][selected[0]].value = 0
                                del keyDict[selected]
                                connection.Send({"action": "OpponentMove"})
                                break
                            #valid and correct entry into cell
                            board.my_tiles[selected[1]][selected[0]].value = keyDict[selected] #assigns current grid value
                            board.board[selected[1]][selected[0]] = keyDict[selected] #assigns to actual board so that the correct value can't be modified
                            del keyDict[selected]
                            connection.Send({"action": "OpponentMove"})

        board.redraw(keyDict, wrong, passedTime)
        # Safely access the synchronized shared game state.
        with client.access_game_state() as game_state:
            # Notify server about player movement.
            old_position = game_state.players[client.player_id]["position"]
            client.dispatch_event(
                event_type="MOVE",
                player_id=client.player_id,
                new_position=((old_position[0] + dx) % screen_width, (old_position[1] + dy) % screen_height),
            )
            # Draw all players as little circles.
            for player_id, player in game_state.players.items():
                if player_id == client.player_id:
                    # Green: Yourself
                    color = (50, 255, 50)
                elif player_id == game_state.chaser_id:
                    # Red: The chaser
                    color = (255, 50, 50)
                else:
                    # Blue: Others
                    color = (50, 50, 255)
                x, y = [int(coordinate) for coordinate in player["position"]]
                pygame.draw.circle(screen, color, (x, y), 10)
        # Do the thing.
        pygame.display.flip()

    # Clean up.
    pygame.quit()

    # Disconnect afterwards and shut down the server if the client is the host.
    client.disconnect(shutdown_server=False)
