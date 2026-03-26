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
  
  gobblet-gobblers-ai/
  │
  ├── app.py # Main GUI application
  ├── game_logic.py # Game rules and state management
  ├── ai_engine.py # Alpha-beta AI implementation
  ├── performance_test.py # AI performance benchmarking
  ├── sound_generator.py # Generates sound effects
  ├── icon.png # Application icon
  ├── sounds/ # Audio files
  │ ├── click.wav
  │ ├── place.wav
  │ └── win.wav
  └── README.md


## How to Run

1. Install dependencies (if not already installed):
  pip install pygame

2. Run the game:
   python app.py

##  Future Improvements

- Add background music system
- Improve AI behavior and decision variation
- Expand to web-based version (AI + web development)

##  Purpose

This project demonstrates:
- Application of AI algorithms in games
- Integration of logic with a full GUI application
- Strong application programming and software design skills
