# Visual Novel Development Guide

This guide will help you create a visual novel using this engine. Let's break down the features and implementation details.

## 1. Configuration Setup

Create a `config.toml` file with the following settings:
```toml
name = "Your Game Name"
credits = "Your Credits Text"
color = "white"  # Main UI color
background = "black"  # Main UI background color
utilise_inventory = true  # Enable/disable inventory system
utilise_saveload = true  # Enable/disable save/load functionality
```

## 2. Scene Structure

Create scenes in `scenes.py`. Each scene requires:

```python
from classes import Scene

scene_name = Scene(
    id_="unique_scene_id",
    header="Scene Name",
    text="Scene description text",
    image="image_filename.png",  # Store in assets folder
    exits=[
        ("Choice Text", ("next_scene", "condition")),  # Conditional transition
    ]
)
```

### Scene Properties:
- `id_`: Unique identifier (has to match the variable name)
- `name`: Scene name
- `text`: Main scene text
- `image`: Scene image filename
- `exits`: List of tuples containing choices and their destinations

## 3. Advanced Scene Features

### 3.1 Conditional Text
```python
scene = Scene(
    # ...
    if_texts=[
        ("Alternative text", "condition_expression"),
    ],
    if_text_additions=[
        ("Additional text", "condition_expression"),
    ]
)
```

### 3.2 Conditional Images
```python
scene = Scene(
    # ...
    if_images=[
        ("alternative_image.png", "condition_expression"),
    ]
)
```

### 3.3 Scene Actions
```python
scene = Scene(
    # ...
    on_enter=[
        (("inventory", "add", "item"), "condition"),
        (("variables", "set", ("var_name", "value")), "condition"),
    ]
)
```

## 4. Game State Management

### 4.1 Inventory System
- Add items: `("inventory", "add", "item_name")`
- Add multiple items: `("inventory", "add-many", ("item_name", quantity))`
- Remove items: `("inventory", "remove", "item_name")`
- Remove all of an item: `("inventory", "remove-all", "item_name")`
- Clear inventory: `("inventory", "clear", None)`

### 4.2 Variables
- Set variable: `("variables", "set", ("var_name", "value"))`
- Update variable: `("variables", "update", ("var_name", "new_value"))`
- Increment: `("variables", "inc", ("var_name", amount))`
- Decrement: `("variables", "dec", ("var_name", amount))`
- Remove variable: `("variables", "remove", "var_name")`
- Clear variables: `("variables", "clear", None)`

### 4.3 Modifiers
- Add modifier: `("modifiers", "add", "modifier_name")`
- Add multiple modifiers: `("modifiers", "add-many", ("modifier_name", quantity))`
- Remove modifier: `("modifiers", "remove", "modifier_name")`
- Remove all of a modifier: `("modifiers", "remove-all", "modifier_name")`
- Clear modifiers: `("modifiers", "clear", None)`

## 5. Game Flow Control

### 5.1 Game Actions
```python
scene = Scene(
    # ...
    on_enter=[
        (("game", "exit", None), "condition"),  # Exit application
        (("game", "goto", "scene_id"), "condition"),  # Jump to scene
        (("game", "restart", None), "condition"),  # Restart game
        (("game", "destroy", None), "condition"),  # Destroy current screen
        (("game", "save", "silent"), "condition"),  # Save game (silent/normal)
        (("game", "load", "silent"), "condition"),  # Load game (silent/normal)
        (("game", "notify", "message"), "condition"),  # Show notification
    ]
)
```

## 6. Conditions and Expressions

Use Python expressions for conditions:
```python
"'item' in player.inventory"  # Check inventory
"invdict.get('item', 0) >= amount"  # Check item quantity
"'modifier' in mods"  # Check modifiers
"modsdict.get('modifier', 0) > amount"  # Check modifier count
"vars['variable'] > 5"  # Check variables
"player.previous.id_ == 'scene_id'"  # Check previous scene
"random_number > 50"  # Use random number (0-100)
```

## 7. Assets Management

1. Create an `assets` folder
2. Store images as PNG/JPG/JPEG
3. Optional: Add `banner.png` for main menu
4. Images are automatically resized and converted to ASCII art

## 8. Save/Load System

The game automatically handles save/load functionality if enabled in config:
- Save button: "S"
- Load button: "L"
- Saves are stored in `save.json` using BSON format
