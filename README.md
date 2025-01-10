# WOPR

A text-based game inspired by the movie War Games.

## How to Run the Game

1. Clone the repository:
   ```sh
   git clone https://github.com/illegalbyte/WOPR.git
   cd WOPR
   ```

2. Install the required dependencies:
   ```sh
   pip install -r requirements.txt
   ```

3. Run the game:
   ```sh
   python WOPR.py
   ```

## Game Overview

WOPR is a text-based game inspired by the movie War Games. The game simulates a global thermonuclear war scenario where players can control different countries, launch missiles, and engage in strategic warfare.

### Features

- Multiple countries with unique attributes and missile capabilities.
- Real-time missile launches and animations.
- DEFCON warning system affecting the hostility of other countries.
- Submarine and missile base locations with hidden and visible elements.
- Interactive gameplay with options for both automated and manual control.

### Game Modes

1. **Autofire Mode**: In this mode, the game runs automatically, and countries launch missiles at each other until only one country remains. The player can observe the missile launches and the changing DEFCON status.

2. **Interactive Mode**: In this mode, the player can choose a country to control and engage in strategic warfare against other countries. The player can launch missiles, move submarines, and make strategic decisions to achieve victory.

### Controls

- Use the arrow keys to navigate the map.
- Press 'Enter' to select a target for missile launch.
- Follow on-screen prompts for specific actions and decisions.

### DEFCON System

The DEFCON (Defense Readiness Condition) system represents the level of military readiness and threat. The DEFCON levels range from 5 (least severe) to 1 (most severe). The DEFCON status affects the behavior and hostility of other countries in the game.

### Submarines and Silos

- Submarines can move stealthily in the ocean and launch missiles from hidden locations.
- Missile silos are fixed locations that can launch missiles but are vulnerable to enemy attacks.

### Winning the Game

The objective of the game is to be the last country standing by strategically launching missiles, defending against enemy attacks, and managing resources effectively.

## Contributing

Contributions are welcome! If you have any suggestions, bug reports, or feature requests, please open an issue or submit a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
