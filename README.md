<div align="center">

```
██████╗ ██╗   ██╗███╗   ██╗ ██████╗ ███████╗ ██████╗ ███╗   ██╗
██╔══██╗██║   ██║████╗  ██║██╔════╝ ██╔════╝██╔═══██╗████╗  ██║
██║  ██║██║   ██║██╔██╗ ██║██║  ███╗█████╗  ██║   ██║██╔██╗ ██║
██║  ██║██║   ██║██║╚██╗██║██║   ██║██╔══╝  ██║   ██║██║╚██╗██║
██████╔╝╚██████╔╝██║ ╚████║╚██████╔╝███████╗╚██████╔╝██║ ╚████║
╚═════╝  ╚═════╝ ╚═╝  ╚═══╝ ╚═════╝ ╚══════╝ ╚═════╝ ╚═╝  ╚═══╝
                          A R E N A
```

**A turn-based roguelike for the terminal: race an AI rival through a procedurally generated dungeon, then face it in the arena.**

[![Python](https://img.shields.io/badge/python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/) [![License: GPL v3](https://img.shields.io/badge/license-GPLv3-blue.svg)](LICENSE)

[Features](#features) · [Getting Started](#getting-started) · [How to Play](#how-to-play) · [How It Works](#how-it-works) · [Roadmap](#roadmap) · [Contributing](#contributing)

</div>

---

## About

**Dungeon Arena** (repository: `dungen-crawler`) is a turn-based dungeon crawler that runs entirely in your terminal. Each run generates a new dungeon that fills your terminal window. A wall splits the map into two halves: you explore one, an AI rival explores the other. Both of you collect gear, avoid traps and fight monsters to level up. Whoever is stronger when you meet in the arena at the center of the map wins.

The game started as a university project. This repository is where it is being refined and extended with new features.

## Features

- **Procedural generation:** every run builds a new maze, with rooms, open areas and a central arena, sized to your terminal.
- **AI rival:** the opponent works through three phases. It collects items, then hunts monsters, then heads for the arena to come after you.
- **Monster AI:** monsters wander at random until you come within their detection range. Then they chase you using breadth-first-search pathfinding.
- **Loot and hidden traps:** weapons raise attack, armor raises defense, and traps stay invisible until someone steps on them.
- **Progression:** defeating monsters and reaching the arena level you up.
- **Light on dependencies:** pure Python with two small libraries, no game engine.

## Getting Started

### Requirements

| Requirement | Details |
| --- | --- |
| Python | 3.10 or newer (developed with 3.12) |
| Terminal | At least **80 × 30** characters, with ANSI color support |
| Packages | [`readchar`](https://pypi.org/project/readchar/), [`colorist`](https://pypi.org/project/colorist/) |

### Installation

```bash
git clone https://github.com/LaJuMiRa/dungen-crawler.git
cd dungen-crawler

pip install readchar colorist
```

### Running the game

```bash
python3 dungeon.py
```

> [!IMPORTANT]
> The map is sized to your terminal when the game starts. Resize the window **before** you launch it, and don't resize it while you play. If the window is smaller than 80 × 30, the game exits with a message.

> [!NOTE]
> The text inside the game is currently in German.

## How to Play

### Goal

Defeat your rival `*`. If your health drops to 0, you lose. When a run ends, you see your stats: remaining HP, monsters defeated and items collected.

### Controls

| Key | Action |
| --- | --- |
| `W` / `↑` | Move up |
| `A` / `←` | Move left |
| `S` / `↓` | Move down |
| `D` / `→` | Move right |
| `Q` | Quit |

Moving into a monster or your rival attacks it. Each key press is one turn: you act first, then all monsters move, then the rival moves.

### Legend

| Symbol | Meaning |
| :---: | --- |
| `@` | You (blue, left half) |
| `*` | AI rival (green, right half) |
| `\|` | Arena doors (blue is yours, green is the rival's) |
| `)` | Weapon: +1 to +5 attack |
| `[` | Armor: +1 to +5 defense |
| `^` | Spike trap: −3 HP (shown once triggered) |
| `_` | Trapdoor: −3 HP (shown once triggered) |
| `&` | Poison cloud: −2 defense (shown once triggered) |
| `█` | Wall |

### Monsters

| Symbol | Monster | Level | HP | ATK | DEF | Detection range |
| :---: | --- | :---: | :---: | :---: | :---: | :---: |
| `G` | Gnome | 1 | 5 | 2 | 2 | 6 |
| `g` | Gremlin | 2 | 6 | 2 | 1 | 8 |
| `J` | Jelly | 3 | 8 | 3 | 0 | 10 |
| `D` | Dragon | 4 | 20 | 6 | 3 | 12 |

Monsters on your half only go after you. Monsters on the rival's half go after whichever player is closer.

### Rules

- **Damage:** `max(attacker ATK − defender DEF, 1)`. Every hit does at least 1 damage.
- **Level up:** each monster you defeat gives +1 level, +10 HP, +2 ATK and +1 DEF.
- **Arena:** the first player to go through their own door gets a level-up bonus. That door then closes behind them and the other door opens.
- **Status bar:** the bottom line shows level, HP, ATK and DEF for you (left) and your rival (right).

## How It Works

The whole game is in [`dungeon.py`](dungeon.py). Each new dungeon is built in this order:

1. **Maze:** a randomized depth-first search (recursive backtracker) carves passages through a grid that starts out as solid wall.
2. **Rooms:** square rooms of random size are cut into the maze. The number of rooms depends on the terminal size.
3. **Open areas:** about 2% of the cells are turned from wall into floor, twice, so there are loops instead of a perfect maze.
4. **Split:** a wall three cells wide divides the map into two halves, with a clear lane on each side of it.
5. **Arena:** a walled room in the center, about 15% of the screen, with a door on each side. Short corridors lead to the doors so they never sit at a dead end.
6. **Placement:** items, traps, monsters and both players are placed at random on floor tiles, the same amount on each half and never inside the arena.

Monsters and the rival find their way with **breadth-first search** (BFS) over the grid. They take the first step of the shortest path to their target on each turn.

## Roadmap

- [ ] **Restructure the project:** split `dungeon.py` into modules, add a test suite and add `pyproject.toml` / `requirements.txt` for installation
- [ ] **New content:** more monsters, items, traps and levels
- [ ] **Local two-player mode:** let a second person play the rival instead of the AI

Have an idea? [Open an issue](https://github.com/LaJuMiRa/dungen-crawler/issues).

## Contributing

Contributions are welcome: bug reports, ideas and pull requests.

1. Fork the repository and create a branch (`git checkout -b feat/my-feature`).
2. Make your changes and test them by playing a few runs.
3. Write commit messages in the [Conventional Commits](https://www.conventionalcommits.org/) style (`feat: …`, `fix: …`, `docs: …`).
4. Open a pull request that describes what you changed and why.

For bigger changes, please open an issue first so we can agree on the approach.

## License

This project is licensed under the **GNU General Public License v3.0**. See [`LICENSE`](LICENSE) for details.
