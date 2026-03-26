# Gobblet Gobblers AI Game

This project implements the Gobblet Gobblers game as a graphical desktop application, combining Artificial Intelligence with application programming.

## AI Implementation

The AI opponent is implemented using **alpha-beta pruning**, an optimized version of the minimax algorithm.  
This allows efficient decision-making and strategic gameplay while reducing unnecessary computations.

## Application Features

- Graphical User Interface (Tkinter)
- Play vs AI or vs another player
- Multiple difficulty levels (easy, medium, hard)
- Animated piece placement
- Sound effects
- Score tracking system
- Highlighting of valid moves and winning lines

## Game Rules (Simplified Gobblet Gobblers)

- 3x3 board
- Each player has:
  - 2 small pieces
  - 2 medium pieces
  - 2 large pieces
- Larger pieces can cover smaller ones
- Pieces are placed from reserve only (no movement after placement)
- First player to align 3 visible pieces wins

## Project Structure
