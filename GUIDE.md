# Hoofd TUIQ Engine Guide

## Overview
Hoofd TUIQ is a text-based game engine built with Python and Textual that allows you to create interactive narrative games with choices, inventory systems, and multiple languages support.

## Features
- Text-based narrative gameplay
- Choice-based progression
- Inventory system
- Save/Load functionality
- Multiple language support
- Image display support (converted to authentic ASCII art)
- Scene conditions and state tracking
- Dynamic text and image changes based on game state

## Project Structure
```
project/
├── assets/           # Images and other media files
├── qtui/
│   ├── scenes/      # Scene definitions for different languages
│   │   ├── __init__.py
│   │   ├── scenes_en.py
│   │   └── scenes_ru.py
│   ├── classes.py   # Core classes
│   ├── config.toml  # Configuration file
│   └── main.py      # Main game engine
```

## Configuration (config.toml)
```toml
name = "Game Name"           # Game title
color = "green"             # Text color
background = "black"        # Background color
utilise_inventory = true    # Enable inventory system
utilise_saveload = true     # Enable save/load functionality
language = "en"            # Default language
credits = "Credits text"    # Credits text
```

## Creating Scenes
Scenes are defined in the `scenes_[language].py` files. Here's an example:

```python
from classes import Scene

example_scene = Scene(
    id_='example_scene',        # Unique scene identifier, matches variable name
    header='Scene Title',       # Scene title
    text='Scene description',   # Main text
    image='image.jpg',         # Image file from assets folder
    speaker='Character Name',   # Speaking character name
    exits=[                     # Available choices
        ('Choice text', ('next_scene', 'condition')),
    ],
    on_enter=[                 # Actions when entering scene
        (('inventory', 'add', 'Item'), 'condition'),
    ],
    if_texts=[                 # Conditional text changes
        ('Alternative text', 'condition'),
    ],
    if_images=[               # Conditional image changes
        ('alt_image.jpg', 'condition'),
    ],
    if_speakers=[             # Conditional speaker changes
        ('Alt Speaker', 'condition'),
    ]
)
```

## Actions and Conditions

### Available Actions
```python
# Inventory actions
(('inventory', 'add', 'Item'), 'condition')
(('inventory', 'add-many', ('Item', 5)), 'condition')
(('inventory', 'remove', 'Item'), 'condition')
(('inventory', 'remove-all', 'Item'), 'condition')
(('inventory', 'clear', ''), 'condition')

# Modifier actions
(('inventory', 'add', 'mod'), 'condition')
(('inventory', 'add-many', ('mod', 5)), 'condition')
(('inventory', 'remove', 'mod'), 'condition')
(('inventory', 'remove-all', 'mod'), 'condition')
(('inventory', 'clear', ''), 'condition')

# Variable actions
(('variables', 'add', ('var', value)), 'condition')
(('variables', 'remove', 'var'), 'condition')
(('variables', 'update', ('var', value)), 'condition')
(('variables', 'inc', ('var', amount)), 'condition')
(('variables', 'dec', ('var', amount)), 'condition')

# Game actions
(('game', 'exit', ''), 'condition')
(('game', 'goto', 'scene_id'), 'condition')
(('game', 'restart', ''), 'condition')
(('game', 'notify', 'message'), 'condition')
```

### Condition Context Variables
In conditions, you have access to:
- `player`: Player object
- `inventory`: List of inventory items
- `invdict`: Dictionary of inventory items and counts
- `mods`: List of modifiers
- `modsdict`: Dictionary of modifiers and counts
- `vars`: Dictionary of variables
- `random`: Random module
- `rnum`: Random number (0-100)

## Example Game Implementation

```python
# scenes_en.py
from classes import Scene

start = Scene(
    id_='start',
    header='Forest',
    text='You find yourself in a dark forest.',
    image='forest.jpg',
    exits=[
        ('Go north', ('north', 'True')),
    ],
    on_enter=[
        (('inventory', 'add', 'Map'), '"Map" not in inventory'),
    ]
)

# Add more scenes...

# Required constants for UI
START = 'Start'
LOAD = 'Load'
SAVE = 'Save'
CREDITS = 'Credits'
EXIT = 'Exit'
LANGUAGE = 'Language'
