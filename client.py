from __future__ import print_function

import sys
from time import sleep
from sys import stdin, exit

from PodSixNet.Connection import connection, ConnectionListener

# This example uses Python threads to manage async input from sys.stdin.
# This is so that I can receive input from the console whilst running the server.
# Don't ever do this - it's slow and ugly. (I'm doing it for simplicity's sake)
from _thread import *
from sudoku_gui import *
from sudoku_alg import valid, solve, find_empty, generate_board
from copy import deepcopy
from sys import exit
import pygame
import time
import random

pygame.init()

class Client(ConnectionListener):
    def __init__(self, host, port):
        self.Connect((host, port))
        print("Chat client started")
        print("Ctrl-C to exit")
        # get a nickname from the user before starting
        print("Enter your nickname: ")
        connection.Send({"action": "Nickname", "nickname": stdin.readline().rstrip("\n")})

        screen = pygame.display.set_mode((540*2 + 30, 590))
        screen.fill((255, 255, 255))
        pygame.display.set_caption("Sudoku")
        icon = pygame.image.load("icon.png")
        pygame.display.set_icon(icon)
        self.screen = screen

        font = pygame.font.SysFont('Bahnschrift', 40)
        text = font.render("Waiting opponent to connect", True, (0, 0, 0))
        screen.blit(text, (175, 245))

        self.board = Board(screen)
        self.

    def Loop(self):
        connection.Pump()
        self.Pump()

    def InputLoop(self):
        # connection.Send({"action": "move", "board_state": stdin.readline().rstrip("\n")})

        #initiliaze values and variables
        wrong = 0
        selected = -1,-1 #NoneType error when selected = None, easier to just format as a tuple whose value will never be used
        keyDict = {}
        running = True
        startTime = time.time()
        while running:
            elapsed = time.time() - startTime
            passedTime = time.strftime("%H:%M:%S", time.gmtime(elapsed))

            if board.board == board.solvedBoard: #user has solved the board
                for i in range(9):
                    for j in range(9):
                        board.my_tiles[i][j].selected = False
                running = False
                connection.Send({"action": "OpponentWin"})

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
        while True: #another running loop so that the program ONLY closes when user closes program
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
        pygame.quit()

    #######################################
    ### Network event/message callbacks ###
    #######################################

    def Network_InformPlayerPresence(self, data):
        print("*** Opponent joined the game: " + data["opponent"])
        #loading screen when generating grid
        font = pygame.font.SysFont('Bahnschrift', 40)
        text = font.render("Opponent Joined:", True, (0, 0, 0))
        screen.blit(text, (175, 245))

        font = pygame.font.SysFont('Bahnschrift', 40)
        text = font.render(data["opponent"], True, (0, 0, 0))
        screen.blit(text, (230, 290))
        pygame.display.flip()

    def Network_InformPlayerLeft(self, data):
        print("*** Opponent left the game: " + data["opponent"])
        # What to do?

    def Network_CompetitionInit(self, data):
        print("Initial board received from server:\n" + data["initial_board_state"])
        self.board.board = data["initial_board_state"]
        # launch our threaded input loop
        t = start_new_thread(self.InputLoop, ())

    def Network_OpponentMove(self, data):
        board_state_correct = data["board_state_correct"]
        board_state_filled = data["board_state_filled"]
        board_state_original = data["board_state_original"]
        current_selection = data["current_selection"]
        selection_color = data["selection_color"]
        self.board.opponent_board_state_correct = board_state_correct
        self.board.opponent_board_state_filled = board_state_filled
        self.board.opponent_board_state_original = board_state_original
        self.board.opponent_current_selection = current_selection
        self.board.opponent_selection_color = selection_color

    def Network_OpponentWin(self, data):
        print("opponent won")


    # built in stuff
    def Network_connected(self, data):
        print("You are now connected to the server")

    def Network_error(self, data):
        print('error:', data['error'][1])
        connection.Close()

    def Network_disconnected(self, data):
        print('Server disconnected')
        exit()




import pygame
import pygame.locals
from pygase import Client
### SETUP ###

# Subclass pygase classes to scope event handlers and game-specific variables.
class SudokuClient(Client):
    def __init__(self):
        super().__init__()
        self.player_id = None
        # The backend will send a "PLAYER_CREATED" event in response to a "JOIN" event.
        self.register_event_handler("PLAYER_CREATED", self.on_player_created)

    # "PLAYER_CREATED" event handler
    def on_player_created(self, player_id):
        # Remember the id the backend assigned the player.
        self.player_id = player_id


# Create a client.
client = ChaseClient()

### MAIN PROCESS ###

if __name__ == "__main__":
    # Connect the client, let the player input a name and join the server.
    client.connect_in_thread(hostname="localhost", port=8080)
    client.dispatch_event("JOIN", input("Player name: "))
    # Wait until "PLAYER_CREATED" has been handled.
    while client.player_id is None:
        pass
    # Set up pygame.
    keys_pressed = set()  # all keys that are currently pressed down
    clock = pygame.time.Clock()
    # Initialize a pygame screen.
    pygame.init()
    screen_width = 640
    screen_height = 420
    screen = pygame.display.set_mode((screen_width, screen_height))
    # Start the actual main loop.
    game_loop_is_running = True
    while game_loop_is_running:
        # Run at 50 FPS
        dt = clock.tick(50)
        # Clear the screen.
        screen.fill((0, 0, 0))
        # Handle pygame input events.
        for event in pygame.event.get():
            if event.type == pygame.locals.QUIT:
                game_loop_is_running = False
            if event.type == pygame.locals.KEYDOWN:
                keys_pressed.add(event.key)
            if event.type == pygame.locals.KEYUP:
                keys_pressed.remove(event.key)
        # Handle player movement.
        dx, dy = 0, 0
        if pygame.locals.K_DOWN in keys_pressed:
            dy += 0.5 * dt
        elif pygame.locals.K_UP in keys_pressed:
            dy -= 0.5 * dt
        elif pygame.locals.K_RIGHT in keys_pressed:
            dx += 0.5 * dt
        elif pygame.locals.K_LEFT in keys_pressed:
            dx -= 0.5 * dt
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
    client.disconnect(shutdown_server=True)
