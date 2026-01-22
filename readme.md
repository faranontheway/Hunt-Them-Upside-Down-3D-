# Hunt Them Upside Down 🎮

A 3D maze game inspired by Stranger Things, where you play as Vecna hunting children through the Upside Down maze. Built with Python and OpenGL.

## 🎯 Game Overview

In this thrilling maze game, you control Vecna navigating through a dark, twisted maze. Three children are trying to escape through doors scattered around the maze. Your goal is to prevent their escape while managing your power levels and dealing with various obstacles.

## ✨ Features

- **3D Maze Environment**: Navigate through a procedurally rendered maze with walls, floors, and doors
- **Dual Camera System**: Switch between bird's-eye view and first-person perspective
- **AI-Powered Children**: Three children with pathfinding AI trying to escape through doors
- **Strategic Doors**: One safe door (green) and two trap doors (red) that change each game
- **Sticky Floor Traps**: Random floor patches that slow down children's movement
- **Power System**: Your power increases when children hit traps and decreases when they escape
- **Health System**: Track each child's health through visual health bars
- **Cheat Mode**: Activate Demogorgons to hunt the children for you

## 🎮 Controls

### Movement
- **W** - Move forward
- **S** - Move backward
- **A** - Rotate left
- **D** - Rotate right

### Camera (Bird's Eye View)
- **Arrow Up** - Move camera up
- **Arrow Down** - Move camera down
- **Arrow Left** - Rotate camera left
- **Arrow Right** - Rotate camera right

### Game Controls
- **V** - Toggle split screen (Bird's Eye + First Person view)
- **C** - Toggle Cheat Mode (spawns 5 Demogorgons)
- **R** - Restart game (when game is over)

## 🏆 Win/Lose Conditions

### You Win If:
- All 3 children die
- 2 children die and 1 escapes

### You Lose If:
- All 3 children escape
- 2 children escape and 1 dies

## 🎲 Game Mechanics

### Children Behavior
- Children use A* pathfinding to navigate to the nearest door
- Each child has 100 health points
- Children respawn after hitting their first trap (with 50 health)
- Second trap hit or reaching 0 health results in permanent death
- Children move slower on sticky floor patches (75% speed)

### Doors
- **Green Door**: Safe exit - children escape successfully
- **Red Doors**: Traps - children lose 50 health
- Door roles shuffle each game

### Power System
- Starts at 50%
- Increases by 20% when a child hits a trap
- Decreases by 20% when a child escapes
- Visual power bar in top-right corner

### Cheat Mode
- Spawns 5 Demogorgons in the maze
- Demogorgons actively hunt and kill children
- Provides an easier path to victory

## 🛠️ Installation

### Prerequisites
- Python 3.7 or higher
- OpenGL compatible graphics card

### Required Libraries
```bash
pip install PyOpenGL PyOpenGL-accelerate
```

Or install from requirements.txt:
```bash
pip install -r requirements.txt
```

### Linux Additional Requirements
```bash
sudo apt-get install freeglut3-dev
```

### macOS Additional Requirements
```bash
brew install freeglut
```

## 🚀 Running the Game

1. Clone the repository:
```bash
git clone https://github.com/yourusername/Hunt-Them-Upside-Down.git
cd Hunt-Them-Upside-Down
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the game:
```bash
python src/Hunt_them_upside_down.py
```

## 🎨 Game Elements

### Visual Design
- **Maze**: Dark red/maroon walls with procedural lighting
- **Floor**: Dark purple base with darker sticky patches
- **Children**: Colorful characters (blue, red, green shirts)
- **Vecna**: Detailed 3D model with dark red coloring
- **Demogorgons**: Brown body with distinctive flower-petal mouth

### Maze Layout
- 19x19 grid maze
- Multiple pathways and dead ends
- Strategic door placements
- 20 randomly placed sticky floor cells

## 🧩 Technical Details

### Technologies Used
- **Python**: Core programming language
- **PyOpenGL**: 3D graphics rendering
- **OpenGL GLU/GLUT**: Utility libraries for 3D primitives and window management
- **A* Algorithm**: Pathfinding for AI children
- **Heap Queue**: Efficient priority queue for pathfinding

### Key Features
- Real-time 3D rendering
- Collision detection
- AI pathfinding with A* algorithm
- Dynamic camera systems
- State management for game logic

## 📝 Code Structure

```
src/
└── Hunt_them_upside_down.py
    ├── Maze generation and rendering
    ├── Character classes (Vecna, Children, Demogorgons)
    ├── Pathfinding algorithms
    ├── Game state management
    ├── Camera systems
    └── UI rendering
```

## 🐛 Known Issues

- First-person camera may clip through walls at certain angles
- Demogorgons in cheat mode can occasionally get stuck in corners


## 🤝 Contributors

Project conducted and documented by
- [@faranontheway](https://github.com/faranontheway)
- [@mourinpixels](https://github.com/mourinpixels)


## 📜 License

This project is open source and available under the MIT License.

## 👏 Acknowledgments

- Inspired by the Netflix series "Stranger Things"
- A* pathfinding algorithm implementation
- OpenGL community for documentation and resources

## 📧 Contact

For questions or feedback, please open an issue on GitHub.

---

**Note**: This game is a fan-made project and is not affiliated with or endorsed by Netflix or the creators of Stranger Things.
