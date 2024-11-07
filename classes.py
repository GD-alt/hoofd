from dataclasses import dataclass, field
from typing import List, Dict, Union


@dataclass
class Scene:
    """
    A class to represent a scene in the game.
    name — the name of the scene.
    text — the text that will be displayed in the scene.
    exits — a dictionary with the names of the exits and the objs of the scenes to which they lead.
    image — the path to the image that will be displayed in the scene (if empty, will appear empty).
    on_enter — actions to be executed when the scene is entered and conditions to match.
    if_texts — a list of tuples with the text to be displayed and the condition to match.
    if_text_additions — a list of tuples with the text to be added to the scene and the condition to match.
    if_images — a list of tuples with the path to the image to be added to the scene and the condition to match.
    speaker — the name of the speaker.
    if_speakers — a list of tuples with the name of the speaker and the condition to match.
    enable_formatting — a boolean to enable or disable formatting (variables, etc.).
    sanitize — a boolean to enable or disable sanitization.
    """
    id_: str
    header: str
    text: str
    exits: List[tuple[str, tuple[str, str]]]
    image: str = ''
    on_enter: List[tuple[tuple, str]] = field(default_factory=list)
    if_texts: List[tuple[str, str]] = field(default_factory=list)
    if_text_additions: List[tuple[str, str]] = field(default_factory=list)
    if_images: List[tuple[str, str]] = field(default_factory=list)
    speaker: str = ''
    if_speakers: List[tuple[str, str]] = field(default_factory=list)
    enable_formatting: bool = True
    sanitize: bool = False


@dataclass
class Player:
    """
    A class to represent a player in the game.
    name — the name of the player.
    inventory — a dictionary with the names of the items in the inventory and their quantity.
    """
    current: Scene = None
    inventory: List[str] = field(default_factory=list)
    previous: Scene = None

    def inventory_dict(self):
        """
        Returns the inventory as a dictionary.
        :return: Dict[str, int]
        """
        if not self.inventory:
            return {}

        result = {}

        for item in self.inventory:
            if item in result:
                result[item] += 1
            else:
                result[item] = 1

        return result

    def inventory_with_count(self):
        """
        Returns the inventory with the quantity of each item removing duplicates (they'll stack).
        :return: List[str]
        """
        result = self.inventory_dict()

        return '\n'.join([f'{k} x{v}' for k, v in result.items()])
