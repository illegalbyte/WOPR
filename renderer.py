'''
a class for rendering the game in the terminal using bext. Difference between this and draw.py is that this class is more general, whilst draw.py is more specific to animations and drawing on the map.
'''

import bext
import sys

class Renderer():
    """
    Class for rendering the game in the terminal.
    """

    def __init__(self):
        """
        Constructor for the Renderer class.
        """
        pass

    @staticmethod
    def clear_screen():
        """
        Clear the screen.
        """
        bext.clear()

    @staticmethod
    def draw_char(X, Y, CHAR: str, COLOUR='RED'):
        """
        Draw a character at a specific location.

        Args:
            X (int): The x-coordinate.
            Y (int): The y-coordinate.
            CHAR (str): The character to be drawn.
            COLOUR (str): The color of the character.
        """
        bext.goto(round(X), round(Y))
        bext.fg(COLOUR)
        print(f'{CHAR}', end='')
        sys.stdout.flush()

    @staticmethod
    def draw_text(X, Y, TEXT: str, COLOUR='RED'):
        """
        Draw text at a specific location.

        Args:
            X (int): The x-coordinate.
            Y (int): The y-coordinate.
            TEXT (str): The text to be drawn.
            COLOUR (str): The color of the text.
        """
        bext.goto(round(X), round(Y))
        bext.fg(COLOUR)
        print(f'{TEXT}', end='')
        sys.stdout.flush()
