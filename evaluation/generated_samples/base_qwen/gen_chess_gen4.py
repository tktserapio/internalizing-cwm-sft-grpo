import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

import copy

# Type definitions
Action = str
State = dict[str, Any]
PlayerObservation = dict[str, Any]

# Helper function to convert algebraic notation to coordinates
def algebraic_to_coordinates(algebraic_notation):
    file = algebraic_notation[0]
    rank = 6 - int(algebraic_notation[1])  # Inverting ranks for easier calculation
    return file, rank

# Function to convert coordinates to algebraic notation
def coordinates_to_algebraic(file, rank):
    return f"{chr(97 + file)}{6 - rank}"

# Function to get the initial state of the game
def get_initial_state() -> State:
    # Initial board setup
    initial_board = {
        "a1": "R", "b1": "N", "c1": "B", "d1": "Q", "e1": "K",
        "a2": "P", "b2": "P", "c2": "P", "d2": "P", "e2": "P",
        "a3": ".", "b3": ".", "c3": ".", "d3": ".", "e3": ".",
        "a4": ".", "b4": ".", "c4": ".", "d4": ".", "e4": ".",
        "a5": "r", "b5": "n", "c5": "b", "d5": "q", "e5": "k"
    }
    return {"board": initial_board}

# Function to apply an action to the state
def apply_action(state: State, action: Action) -> State:
    # Convert action to pieces and coordinates
    piece, from_square, to_square = action.split("_")
    from_file, from_rank = algebraic_to_coordinates(from_square)
    to_file, to_rank = algebraic_to_coordinates(to_square)
    
    # Create a deep copy of the state to avoid mutating the original state
    new_state = copy.deepcopy(state)
    
    # Update the board
    new_state["board"][coordinates_to_algebraic(to_file, to_rank)] = new_state["board"].pop(coordinates_to_algebraic(from_file, from_rank))
    
    # Handle special cases like pawn promotion
    if piece == "P":
        if to_rank == 1 or to_rank == 5:
            new_state["board"][coordinates_to_algebraic(to_file, to_rank)] += "Q"
    
    # Handle castling
    # Castling is not implemented in this 5x5 variant
    
    return new_state

# Function to get the current player
def get_current_player(state: State) -> int:
    # White starts first
    return 0 if state["board"]["e1"] == "R" else 1

# Function to get the name of the player
def get_player_name(player_id: int) -> str:
    return "Player 0" if player_id == 0 else "Player 1"

# Function to get the rewards per player
def get_rewards(state: State) -> list[float]:
    # Check for checkmate/stalemate/draw conditions
    # For simplicity, assume the game ends immediately upon checkmate
    white_king_position = next((file, rank) for file, rank in state["board"].items() if state["board"][file + str(rank)] == "K")
    black_king_position = next((file, rank) for file, rank in state["board"].items() if state["board"][file + str(rank)] == "k")
    
    if state["board"][white_king_position[0] + str(6 - white_king_position[1])] == "K":
        return [-1.0, 1.0]
    elif state["board"][black_king_position[0] + str(6 - black_king_position[1])] == "k":
        return [1.0, -1.0]
    
    return [0.0, 0.0]

# Function to get the legal actions for the current state
def get_legal_actions(state: State) -> list[Action]:
    legal_actions = []
    for file, rank in state["board"].items():
        if rank in ["R", "N", "B", "Q", "K"]:
            # Generate possible moves for each piece
            if rank in ["R", "N", "B", "Q"]:
                generate_moves(file, rank, state["board"])
            if rank == "K":
                generate_castle_moves(file, state["board"])
        elif rank == "P":
            generate_pawn_moves(file, rank, state["board"])
    
    return legal_actions

# Helper function to generate moves for each piece
def generate_moves(file, rank, board):
    moves = []
    if rank == "R":
        moves.extend(generate_horizontal_vertical_moves(file, rank, board))
    elif rank == "N":
        moves.extend(generate_l_shape_moves(file, board))
    elif rank == "B":
        moves.extend(generate_diagonal_moves(file, board))
    elif rank == "Q":
        moves.extend(generate_horizontal_vertical_moves(file, rank, board))
        moves.extend(generate_diagonal_moves(file, board))
    elif rank == "K":
        moves.extend(generate_castle_moves(file, board))
    return moves

# Helper function to generate horizontal-vertical moves
def generate_horizontal_vertical_moves(file, rank, board):
    moves = []
    for i in range(1, 5):
        new_file = file
        new_rank = rank
        if rank == "P":
            new_rank = 6 - int(rank)
        if new_file - i >= 0 and board.get(f"{new_file - i}{new_rank}") == ".":
            moves.append(f"{file}{rank}_{file - i}{new_rank}")
        if new_file + i <= 5 and board.get(f"{new_file + i}{new_rank}") == ".":
            moves.append(f"{file}{rank}_{file + i}{new_rank}")
    return moves

# Helper function to generate l-shape moves
def generate_l_shape_moves(file, board):
    moves = []
    for i in range(-1, 2):
        for j in range(-1, 2):
            if i != 0 and j != 0:
                new_file = file
                new_rank = 6 - int(file)
                if new_file + i >= 0 and new_file + i <= 5 and new_rank + j >= 0 and new_rank + j <= 5:
                    if board.get(f"{new_file + i}{new_rank + j}") in [".", "P"]:
                        moves.append(f"{file}{rank}_{new_file + i}{new_rank + j}")
    return moves

# Helper function to generate diagonal moves
def generate_diagonal_moves(file, board):
    moves = []
    for i in range(-1, 2):
        for j in range(-1, 2):
            if i != 0 and j != 0:
                new_file = file
                new_rank = 6 - int(file)
                if new_file + i >= 0 and new_file + i <= 5 and new_rank + j >= 0 and new_rank + j <= 5:
                    if board.get(f"{new_file + i}{new_rank + j}") in [".", "P"]:
                        moves.append(f"{file}{rank}_{new_file + i}{new_rank + j}")
    return moves

# Helper function to generate castle moves
def generate_castle_moves(file, board):
    moves = []
    if file == "a" and board.get("b1") == "R" and board.get("c1") == "." and board.get("d1") == ".":
        moves.append("K_a1_R_a1")
    if file == "e" and board.get("d5") == "R" and board.get("c5") == "." and board.get("b5") == ".":
        moves.append("K_e1_R_e1")
    return moves

# Function to get observations for each player
def get_observations(state: State) -> list[PlayerObservation]:
    # Observations include the board state
    return [{"board": state["board"]}]

# Main function to run the game loop
def main():
    state = get_initial_state()
    print("Initial State:")
    print(state)
    
    while True:
        current_player = get_current_player(state)
        print(f"\nCurrent Player: {get_player_name(current_player)}")
        
        legal_actions = get_legal_actions(state)
        print(f"Legal Actions: {legal_actions}")
        
        action = input("Enter your move (e.g., 'P_a2_a3'): ")
        new_state = apply_action(state, action)
        
        print("\nNew State:")
        print(new_state)
        
        rewards = get_rewards(new_state)
        print(f"Rewards: {rewards}")
        
        if rewards[0] != 0.0 or rewards[1] != 0.0:
            break
        
        state = new_state

if __name__ == "__main__":
    main()