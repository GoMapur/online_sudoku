import sys
from time import sleep, localtime
import math
from pygase import GameState, Backend
from sudoku_alg import generate_board
from copy import deepcopy

### SETUP ###
board_p1 = generate_board()
board_p2 = deepcopy(board_p1)

# Initialize the game state.
initial_game_state = GameState(
    players={},  # dict with `player_id: player_dict` entries
    board_p1 = {"board": board_p1,
        "placed_values": [[0 for i in range(9)] for j in range(9)],
        "correct": [[True if  for i in range(9)] for j in range(9)], 
        "current_selection": None,
        "last_selection": None,
        "last_selection_color": None},
    board_p2 = {},
    time_elapsed = 0
)

# Define the game loop iteration function.
def time_step(game_state, dt):
    # Before a player joins, updating the game state is unnecessary.
    if len(players) < 2:
        return {}
    if

# Create the backend.
backend = Backend(initial_game_state, time_step)

# "MOVE" event handler
def on_move(player_id, new_position, **kwargs):
    return {"players": {player_id: {"position": new_position}}}

# "JOIN" event handler
def on_join(player_name, game_state, client_address, **kwargs):
    if len(game_state.players) == 2:
        backend.server.dispatch_event("JOIN_FAILED", target_client=client_address)

    print(f"{player_name} joined.")
    player_id = len(game_state.players)
    # Notify client that the player successfully joined the game.
    backend.server.dispatch_event("PLAYER_CREATED", player_id, target_client=client_address)
    return {
        # Add a new entry to the players dict
        "players": {player_id: {"name": player_name, "client_address": client_address, }},
        # If this is the first player to join, make it the chaser.
        "chaser_id": player_id if game_state.chaser_id is None else game_state.chaser_id,
    }


# Register handlers
backend.game_state_machine.register_event_handler("JOIN", on_join)
backend.game_state_machine.register_event_handler("MOVE", on_move)

### MAIN PROCESS ###

if __name__ == "__main__":
    backend.run(hostname="localhost", port=8080)
