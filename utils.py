from PIL import Image
from pathlib import Path
import numpy as np


def reduce(image: Path, width: int) -> Image:
    """
    Reduce the size of the image to 160x...
    :param width: Width of the image
    :param image: Path to the image
    :return: Image
    """
    img = Image.open(image)
    dimensions = img.size

    if dimensions[0] > width:
        ratio = width / dimensions[0]
        img = img.resize((width, int(dimensions[1] * ratio)))

    return img


def image_to_block_art(img, output_width=100, output_height=None):
    """
    Convert an image to ASCII art using Unicode blocks.
    """
    # Unicode block characters (from darkest to lightest)
    BLOCK_CHARS = [' ', '░', '▒', '▓', '█']

    # Load and process image (same as before)

    img = img.convert('L')

    # Calculate dimensions
    aspect_ratio = img.height / img.width
    if output_height is None:
        output_height = int(output_width * aspect_ratio * 0.5)

    img = img.resize((output_width, output_height), Image.Resampling.LANCZOS)
    pixels = np.array(img)

    # Convert to blocks
    block_art = ''
    for row in pixels:
        for pixel in row:
            # Map pixel values to block characters
            block_index = int(pixel / 255 * (len(BLOCK_CHARS) - 1))
            block_art += BLOCK_CHARS[block_index]
        block_art += '\n'

    return block_art
