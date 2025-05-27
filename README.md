# Rhythm Game 
This Pygame-based rhythm game offers an engaging musical experience where players hit falling notes represented by animated animals across multiple tracks. The game features adaptive difficulty progression, responsive design scaling, and a comprehensive scoring system that rewards precise timing and accuracy.

The game combines classic rhythm game mechanics with unique animated characters (bird, frog, rabbit, and cat) that respond dynamically to player input. Each difficulty level introduces new challenges through adjusted note speeds, spawn rates, and timing thresholds, creating an engaging progression system that keeps players motivated to improve their skills. The game automatically scales to the player's screen resolution while maintaining playability and visual clarity.

## Repository Structure
```
.
├── requirements.txt     # Python package dependencies with version specifications
└── rhythm_game.py      # Main game implementation with animation and gameplay logic
```

## Usage Instructions
### Prerequisites
- Python 3.6 or higher
- The following Python packages (specified in requirements.txt):
  - pygame >= 2.0.0
  - pygame_gui >= 0.6.0
  - Pillow >= 8.0.0
  - numpy >= 1.19.0
  - boto3 >= 1.26.0
  - requests >= 2.25.0

### Installation
1. Clone the repository:
```bash
git clone https://github.com/hiepnguyendt/Rhythm-Game
cd Rhythm-Game
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

### Quick Start
1. Run the game:
```bash
python rhythm_game.py
```

2. Game Controls:
- Use the corresponding keys to hit notes in each track when they reach the target line
- Aim for perfect timing to maximize your score
- Progress through difficulty levels by maintaining high accuracy

### More Detailed Examples
1. Scoring System:
- Perfect hits: Notes hit within 5-20 pixels of the target line (varies by difficulty)
- Good hits: Notes hit within 10-40 pixels of the target line (varies by difficulty)
- Score multipliers increase with consecutive successful hits

2. Difficulty Progression:
```python
# Example difficulty settings
'normal': {
    'note_speed': 5,
    'spawn_rate_min': 0.5,
    'spawn_rate_max': 1.5,
    'perfect_threshold': 15,
    'good_threshold': 30,
    'notes_to_pass': 100,
    'accuracy_to_pass': 75
}
```

### Troubleshooting
1. Audio Latency Issues
- Problem: Note hit timing feels off
- Solution: Adjust audio buffer size in pygame.mixer.pre_init()
```python
pygame.mixer.pre_init(44100, -16, 2, 512)  # Reduce audio latency
```

2. Performance Issues
- Problem: Game running slowly
- Solution: Check your screen resolution settings
```python
# Adjust screen scale in game settings
SCREEN_WIDTH = max(800, int(user_screen_width * 0.8))  # Default screen scale
```

3. Display Scaling Issues
- Problem: Game elements appear too large/small
- Solution: Modify scaling factors
```python
SCALE_X = SCREEN_WIDTH / BASE_WIDTH
SCALE_Y = SCREEN_HEIGHT / BASE_HEIGHT
```

## Data Flow
The game processes input and updates game state in a continuous loop, handling note spawning, movement, collision detection, and scoring.

```ascii
[User Input] -> [Input Processing] -> [Game State Update]
      ^                                      |
      |                                     v
[Display Update] <- [Animation Update] <- [Physics Update]
```

Key component interactions:
1. Input handler processes keyboard events for note hits
2. Note spawner creates new notes based on difficulty settings
3. Animation system updates animal positions and states
4. Collision detection system checks note timing accuracy
5. Scoring system calculates points and tracks progression
6. Display system renders all game elements with proper scaling
7. Difficulty manager adjusts game parameters based on player performance
