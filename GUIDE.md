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
- Modifiers system
- Variables system
- Speaker system with conditional changes
- Text formatting and sanitization options

## Project Structure
```
project/
├── assets/           # Images and other media files
├── qtui/
│   ├── scenes/      # Scene definitions for different languages
│   │   ├── __init__.py
│   │   └── scenes_[lang].py
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
language = "en"             # Default language
languages = ["en"]          # Available languages
credits = "Credits text"    # Credits text
```

## Scene Definition
Scenes are defined in the `scenes_[language].py` files using the Scene class:

```python
from classes import Scene

example_scene = Scene(
    id_='example_scene',        # Unique scene identifier (matches variable name)
    header='Scene Title',       # Scene title
    text='Scene description',   # Main text
    image='image.jpg',         # Image file from assets folder (optional)
    speaker='Character Name',   # Speaking character name (optional)
    exits=[                     # Available choices
        ('Choice text', ('next_scene', 'condition')),
    ],
    on_enter=[                 # Actions when entering scene
        (('action_type', 'action', 'value'), 'condition'),
    ],
    if_texts=[                 # Conditional text changes
        ('Alternative text', 'condition'),
    ],
    if_text_additions=[        # Conditional text additions
        ('Additional text', 'condition'),
    ],
    if_images=[                # Conditional image changes
        ('alt_image.jpg', 'condition'),
    ],
    if_speakers=[              # Conditional speaker changes
        ('Alt Speaker', 'condition'),
    ],
    enable_formatting=True,     # Enable variable formatting in text
    sanitize=False             # Enable text sanitization
)
```

## Actions System

### Action Types
1. Inventory Actions
```python
(('inventory', 'add', 'Item'), 'condition')
(('inventory', 'add-many', ('Item', quantity)), 'condition')
(('inventory', 'remove', 'Item'), 'condition')
(('inventory', 'remove-all', 'Item'), 'condition')
(('inventory', 'clear', ''), 'condition')
```

2. Modifier Actions
```python
(('modifiers', 'add', 'mod'), 'condition')
(('modifiers', 'add-many', ('mod', quantity)), 'condition')
(('modifiers', 'remove', 'mod'), 'condition')
(('modifiers', 'remove-all', 'mod'), 'condition')
(('modifiers', 'clear', ''), 'condition')
```

3. Variable Actions
```python
(('variables', 'add', ('var', value)), 'condition')
(('variables', 'remove', 'var'), 'condition')
(('variables', 'update', ('var', value)), 'condition')
(('variables', 'inc', ('var', amount)), 'condition')
(('variables', 'dec', ('var', amount)), 'condition')
(('variables', 'set', ('var', 'expression')), 'condition')
```

4. Game Actions
```python
(('game', 'exit', ''), 'condition')
(('game', 'goto', 'scene_id'), 'condition')
(('game', 'restart', ''), 'condition')
(('game', 'notify', 'message'), 'condition')
(('game', 'destroy', ''), 'condition')
(('game', 'load', 'silent'), 'condition')
(('game', 'save', 'silent'), 'condition')
```

## Condition Context
In conditions, you have access to:
- `player`: Player object
- `inventory`: List of inventory items
- `invdict`: Dictionary of inventory items and counts
- `mods`: List of modifiers
- `modsdict`: Dictionary of modifiers and counts
- `vars`: Dictionary of variables
- `random`: Random module
- `rnum`: Random number (0-100)
- `SYS`: System scenes
- `MY`: Custom variables

## Required Language Constants
Each language file must define:
```python
START = 'Start'
LOAD = 'Load'
SAVE = 'Save'
LOAD_SHORT = 'L'
SAVE_SHORT = 'S'
CREDITS = 'Credits'
EXIT = 'Exit'
LANGUAGE = 'Language'
SAVED = 'Saved'
LOADED = 'Loaded'
RESTART_NEEDED = 'Restart needed'
```

## Global Scene Modifications
Define these lists in language files:
```python
GLOBAL_ADDITIONS = []  # Global text additions
GLOBAL_IMAGES = []     # Global image changes
VARS = {}             # Global variables
MY_VARS = {}          # Custom variables
```
