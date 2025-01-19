<h1 align="center">Maya Procedural Building Generator</h1>
<p align="center">
  <img src="https://img.shields.io/badge/Python-FFD43B?style=for-the-badge&logo=python&logoColor=blue">
  <img src="https://img.shields.io/badge/Maya-37A5CC?style=for-the-badge&logo=autodeskmaya&logoColor=white">
</p>

<img src="https://github.com/user-attachments/assets/a664f15e-642f-4f39-859c-ade85ee31e48">


<img align="right" width=400 src="https://github.com/user-attachments/assets/4fd094b0-bdbd-49b4-a7e5-6308cd561de4">

### Overview

**Maya Procedural Building Generator** is a script for generating 3D urban environments in Autodesk Maya.
The system creates customizable building facades and layouts through procedural methods.
It is ideal for quickly creating buildings from simple geometry.
> [!IMPORTANT]  
> This script may not function on other systems without modifications, and updates or support are not planned.


### Features

- **Procedural Generation**:
  - Automated placement of windows, doors, trims, and bricks.
- **Customizability**:
  - User-defined parameters like floor density, ground floor height, and trim dimensions..

## Technologies Used

- Python 3.10.8
- Autodesk Maya with `pymel` and `cmds` modules
- UI elements via `PySide2`

## Core Components

1. **Building Generator** (`building_gen.py`)
   - Generates buildings from a reference cube geometry.
   - Applies shaders, trims, and geometry adjustments.
2. **Building Facade Logic** (`building_side.py`)
   - Manages facade elements like windows, doors, and trims.
   - Supports density-based distributions and bilinear sampling for precise placements.
3. **Stair Generator** (`stairs.py`)
   - Creates spiral or straight staircases with randomized dimensions.
4. **Ball Animation** (`ball.py`)
   - Implements bouncing ball animations synchronized with stair geometry.
5. **Scene Management** (`scene_data.py`)
   - Centralizes scene-wide parameters like step dimensions and ball sizes.

## Usage

### Prerequisites

- Autodesk Maya installed with `pymel` module.
- Basic knowledge of Python and Maya scripting.
- Appropriately named primitive geometry to populate the building with.

### Installation

1. Clone the repository to your maya scripts directory.
 ```bash
git clone https://github.com/ParkerBritt/maya_building_generator
```
