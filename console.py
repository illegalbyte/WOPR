'''
The console class handles the console panel and user input. 
It uses an instance of the Draw class to draw in the terminal. 
The panel is created at the bottom of the terminal window, and user input is displayed in this panel. 
The console class also keeps a history of messages displayed in the panel.
'''

import os
import pyinputplus
from draw import Draw


class Console:
	'''
	A class that manages a console interface with a panel for displaying messages and getting user input.
	The Console class provides functionality for creating and managing a panel at the bottom of the terminal
	window, displaying messages, handling user input, and maintaining a history of messages.
	Attributes:
		draw (Draw): An instance of Draw class used to render content on the console
		height (int): Total height of the terminal window in lines
		width (int): Total width of the terminal window in columns
		panel_height (int): Height of the console panel in lines
		panel_start (int): Starting y-coordinate of the panel
		history (list): List of messages displayed in the panel
		max_history (int): Maximum number of messages to keep in history
	Methods:
		create_panel(): Creates the console panel with a border
		clear_console(): Clears the panel area
		write(message, color): Writes a message to the panel with optional color
		get_input(prompt, options): Gets user input with optional menu choices
		ask_for_coordinates(): Gets x,y coordinates from user input
		console(input): Writes messages to the bottom console area
  	'''
	def __init__(self, draw: Draw):
		self.draw = draw  # Use an instance of Draw to draw on the console
		self.height = int(os.get_terminal_size().lines)
		self.width = int(os.get_terminal_size().columns)
		self.panel_height = 7
		self.panel_start = 48 # Start of the panel at the bottom of the terminal
		self.history = []
		self.max_history = 5

	def create_panel(self):
		"""Initialize console panel using Draw methods"""
		# Draw top border of panel
		for x in range(self.width):
			self.draw.draw_char(x, self.panel_start, '═', COLOUR='WHITE')
		self.clear_console()
    
	def clear_console(self):
		"""Clear panel area using Draw methods"""
		for y in range(self.panel_start + 1, self.height):
			for x in range(self.width):
				self.draw.draw_char(x, y, ' ', COLOUR='RESET')

	def write(self, message: str, color: str = 'WHITE'):
		"""Write message to panel using Draw"""
		self.history.append(message)
		if len(self.history) > self.max_history:
			self.history.pop(0)
		self.clear_console()
		
		# Keep messages within panel height
		max_lines = self.panel_height - 2
		if len(self.history) > max_lines:
			self.history = self.history[-max_lines:]
			
		for i, msg in enumerate(self.history):
			y_pos = self.panel_start + 1 + i
			self.draw.draw_text(2, y_pos, f">> {msg}", color)


	def get_input(self, prompt: str, options: list = None) -> str:
		"""Get user input using pyinputplus"""
		self.write(prompt)
		
		if options:
			try:
				# Clear area for menu while keeping prompt visible
				for i in range(1, len(options) + 2):
					self.draw.draw_text(2, self.panel_start + i, " " * (self.width - 4))
				
				# Position menu at fixed location
				menu_prompt = f"\n{prompt}\n> "
				return pyinputplus.inputMenu(
					options,
					prompt=menu_prompt,
					numbered=False,
					lettered=True,
					blank=False
				)
			except pyinputplus.RetryLimitException:
				self.write("Too many invalid attempts", 'RED')
				return None
		else:
			# Position single input at fixed location
			return pyinputplus.inputStr(
				prompt=f"\033[{self.panel_start + 2};2H> ",
				blank=False
			)


			
	def ask_for_coordinates(self) -> tuple:
		"""
		Ask for coordinates from the user.
		
		Returns:
			tuple: The coordinates entered by the user.
		"""
		self.clear_console()
		x_coord = "0"
		while not x_coord.isalpha() or len(x_coord) != 1:
			self.write('ENTER X LOCATION [A,B,C...] >', 'RED')  
			x_coord = self.get_input("")
			self.clear_console()

		x_coord_letter = x_coord
		x_coord = Map.convert_x_coord(x_coord)
		self.write(f"TARGET X AXIS: {(x_coord_letter.upper())} / {x_coord}", 'RED')
		
		# Use get_input with numeric validation
		y_coord = pyinputplus.inputInt(
			prompt=f"\033[{self.panel_start + 6};2H> ",
			min=0, 
			max=45
		)
		self.clear_console()

		return (x_coord, y_coord)
		

	def console(self, input_text: str):
		"""
		Write to the bottom console using Draw methods.

		Args:
			input_text (str): The text to be written to the console.
		"""
		# Add input to history
		self.history.append(input_text)
		if len(self.history) > self.max_history:
			self.history.pop(0)
			
		# Clear the console area
		self.clear_console()
		
		# Draw each history message
		for i, msg in enumerate(self.history):
			self.draw.draw_char(2, self.panel_start + 1 + i, f">> {msg}", COLOUR='RED')
			