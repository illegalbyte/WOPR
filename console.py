'''
The console class handles the console panel and user input. 
It uses an instance of the Draw class to draw in the terminal. 
The panel is created at the bottom of the terminal window, and user input is displayed in this panel. 
The console class also keeps a history of messages displayed in the panel.
'''

import os
import sys
import pyinputplus
from draw import Draw
import bext
from map import Map # needed for convert_x_coord function for getting user input coordinates


class Console:
    def __init__(self, draw: Draw, map: Map):
        self.draw = draw
        self.height = int(os.get_terminal_size().lines)
        self.width = int(os.get_terminal_size().columns)
        self.map_width = 154	# Width of the map
        self.panel_Y_start = 50  # Fixed panel position
        self.panel_Y_end = 80  # Fixed panel position
        self.history = []
        self.max_history = 5
        self.console_prompts = []

    def clear_console(self):
        """
		Clear the console panel.
		"""
        self.draw.clear_lines(self.panel_Y_start, self.panel_Y_end)
        self.draw.draw_text(0, self.panel_Y_start - 1, "+" + "-" * 152 + "+", "GREEN")

    def console_log(self, prompt_text: str):
        """
		Write to the bottom console.
		Args:
				prompt_text (str): The input to be written to the console.
		"""
        bext.fg("RED")
        if len(self.console_prompts) > 9:
            self.console_prompts.pop(0)
        self.console_prompts.append(prompt_text)
        self.draw.clear_lines(self.panel_Y_start, self.panel_Y_end)
        for i, output in enumerate(self.console_prompts):
            bext.goto(2, 50 + i)
            if type(output) == str:
                print(f">> {output}")
            else:
                output
        bext.fg("reset")
        sys.stdout.flush()

    def get_input_choice(self, prompt_text: str, choices_list: list) -> str:
        """
		Get user input.
		Args:
			prompt_text (str): The prompt text to be displayed.
		Returns:
			str: The user input.
		"""
        self.clear_console()
        bext.goto(0, self.panel_Y_start)
        user_choice = pyinputplus.inputMenu(choices_list, prompt=prompt_text, numbered=True)
        sys.stdout.flush()
        return user_choice

    def get_input_int(self, prompt_text: str) -> int:
        """
		Get user input.
		Args:
			prompt_text (str): The prompt text to be displayed.
		Returns:
			int: The user input.
		"""
        self.clear_console()
        bext.goto(0, self.panel_Y_start)
        return pyinputplus.inputInt(prompt=prompt_text)

    def get_input_coordinates(self) -> tuple:
        """
		Ask for coordinates from the user.

		Returns:
				tuple: The coordinates entered by the user.
		"""
        self.clear_console()
        bext.fg("RED")
        x_coord = "0"
        # Get x coordinate, validate for single letter input
        while not (x_coord.isalpha() and len(x_coord) == 1):
            bext.goto(0, self.panel_Y_start)
            x_coord = pyinputplus.inputStr("ENTER X LOCATION [A,B,C...] > ").upper()
            Draw.clear_console()

        x_coord_letter = x_coord
        x_coord = self.map.convert_x_coord(x_coord)
        self.console_log(f"TARGET X AXIS: {(x_coord_letter.upper())} / {x_coord}")
        bext.fg("RED")
        y_coord = pyinputplus.inputInt("ENTER Y LOCTAION [1,2,3...] > ", min=0, max=45)
        self.clear_console()

        return (x_coord, y_coord)
