import bext
import pyinputplus
import sys
import time
import math
import ast

# BEXT REQUIREMENTS, for printing to the screen
WIDTH, HEIGHT = bext.size()
#	for Windows (OS) term width (prevents printing a newline when reaching the end of terminal)
WIDTH -= 1
# the speed of animations per second
REFRESH_RATE = 0.00002
SMALL_PAUSE = 0.0008
# colours which can be used by BEXT
COLOURS = ['red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white']
# console prompts list (stores the prompts for the game)
console_prompts = []
# Read world map from map .txt file 
with open('WORLD_MAP.txt', 'r') as map:
	WORLD_MAP = map.read()

class Draw():
	"""
	Class containing functions for drawing on the game map.
	"""

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

	def draw_targets(regions: dict):
		"""
		Draw targets for each region.

		Args:
			regions (dict): Dictionary containing regions and their targets.
		"""
		for region in regions.values():
			for country, target in region.items():
				x, y = target
				Draw.draw_char(x, y, r'{X}', COLOUR='WHITE')
	
	def draw_fallout_old(STRIKE_X, STRIKE_Y, RADIUS=2, SPEED=0.03, COLOUR="PURPLE", CHAR="X"):
		"""
		Draw radiation circle.

		Args:
			STRIKE_X (int): The x-coordinate of the strike.
			STRIKE_Y (int): The y-coordinate of the strike.
			RADIUS (int): The radius of the fallout.
			SPEED (float): The speed of drawing the fallout.
			COLOUR (str): The color of the fallout.
			CHAR (str): The character representing the fallout.
		"""
		while RADIUS != 0:
			theta = 0
			h = STRIKE_X
			k = STRIKE_Y
			step = 15
			while theta <= 360:
				x = h + RADIUS*math.cos(theta)
				y = k + RADIUS*math.sin(theta)
				if x > WIDTH:
					continue
				if y > HEIGHT:
					continue
				Draw.draw_char(x, y, CHAR, COLOUR=COLOUR)
				time.sleep(SPEED)
				theta += step
			RADIUS -=1

	def draw_fallout(target: tuple, RADIUS=2, SPEED=0.03, COLOUR="Green", CHAR="X"):
		"""
		Draw fallout around a target.

		Args:
			target (tuple): The coordinates of the target.
			RADIUS (int): The radius of the fallout.
			SPEED (float): The speed of drawing the fallout.
			COLOUR (str): The color of the fallout.
			CHAR (str): The character representing the fallout.

		Returns:
			list: List of coordinates affected by the fallout.
		"""
		circles_drawn = 0
		fallout_coords = []
		while circles_drawn < RADIUS+1:
			coords = Draw.draw_circle(target[0], target[1], circles_drawn, COLOUR="PURPLE", erase_map_tiles=True, radius_modifier=1)
			for x, y in coords:
				Draw.draw_char(x, y, CHAR, COLOUR=COLOUR)
				time.sleep(0.4)
			fallout_coords.extend(coords)
			circles_drawn += 1

		return fallout_coords

	def draw_circle(X, Y, RADIUS, COLOUR='RED', CHAR="X", erase_map_tiles=False, radius_modifier=2, visible=True) -> list:
		"""
		Draw a hollow circle around a specific location.

		Args:
			X (int): The x-coordinate of the center.
			Y (int): The y-coordinate of the center.
			RADIUS (int): The radius of the circle.
			COLOUR (str): The color of the circle.
			CHAR (str): The character representing the circle.
			erase_map_tiles (bool): Whether to erase map tiles.
			radius_modifier (int): Modifier for the radius.
			visible (bool): Whether the circle is visible.

		Returns:
			list: List of coordinates of the circle's perimeter.
		"""
		circle = []
		theta = 0
		step = 2*math.pi/2000
		while theta <= 2*math.pi:
			x = X + RADIUS*math.cos(theta)
			y = Y - (RADIUS/radius_modifier)*math.sin(theta)
			if x > 152:
				x = x - 152
			if x < 0:
				x = x + 152
			if y > 45:
				theta += step
				continue
			if Draw.get_original_character(x, y) == ' ':
				if visible:
					Draw.draw_char(x, y, CHAR, COLOUR=COLOUR)
				if (round(x), round(y)) not in circle:
					circle.append((round(x), round(y)))	
			elif erase_map_tiles:
				if visible:
					Draw.draw_char(x, y, CHAR, COLOUR=COLOUR)
				if (round(x), round(y)) not in circle:
					circle.append((round(x), round(y)))	
			theta += step

		return circle

	def get_line(start: tuple, end: tuple) -> list:
		"""
		Generate a list of points forming a line between two coordinates.

		Args:
			start (tuple): The starting coordinates.
			end (tuple): The ending coordinates.

		Returns:
			list: List of points forming the line.
		"""
		x1, y1 = start
		x2, y2 = end
		dx = x2 - x1
		dy = y2 - y1

		is_steep = abs(dy) > abs(dx)

		if is_steep:
			x1, y1 = y1, x1
			x2, y2 = y2, x2

		swapped = False
		if x1 > x2:
			x1, x2 = x2, x1
			y1, y2 = y2, y1
			swapped = True

		dx = x2 - x1
		dy = y2 - y1

		error = int(dx / 2.0)
		ystep = 1 if y1 < y2 else -1

		y = y1
		points = []
		for x in range(x1, x2 + 1):
			coord = (y, x) if is_steep else (x, y)
			points.append(coord)
			error -= abs(dy)
			if error < 0:
				y += ystep
				error += dx

		if swapped:
			points.reverse()
		return points

	def draw_line(x1, y1, x2, y2, COLOUR='RED', ocean_only=True) -> list:
		"""
		Draw a line between two points.

		Args:
			x1 (int): The x-coordinate of the starting point.
			y1 (int): The y-coordinate of the starting point.
			x2 (int): The x-coordinate of the ending point.
			y2 (int): The y-coordinate of the ending point.
			COLOUR (str): The color of the line.
			ocean_only (bool): Whether to draw only on ocean tiles.

		Returns:
			list: List of coordinates of the line.
		"""
		points = Draw.get_line((round(x1), round(y1)), (round(x2), round(y2)))
		valid_points = []
		for point in points:
			x, y = point
			if x > 152:
				continue
			if ocean_only and not Map.check_for_ocean(x,y):
				continue
			Draw.draw_char(x, y, 'X', COLOUR=COLOUR)
			valid_points.append((x,y))
		return valid_points

	def ask_for_coordinates() -> tuple:
		"""
		Ask for coordinates from the user.

		Returns:
			tuple: The coordinates entered by the user.
		"""
		Draw.clear_console()
		bext.fg('RED')
		x_coord = "0"
		while not x_coord.isalpha() or len(x_coord) != 1:
			bext.goto(0, 50)
			x_coord = pyinputplus.inputStr('ENTER X LOCTAION [A,B,C...] > ')
			Draw.clear_console()

		x_coord_letter = x_coord
		x_coord = Map.convert_x_coord(x_coord)
		Draw.console(f"TARGET X AXIS: {(x_coord_letter.upper())} / {x_coord}")
		bext.fg('RED')
		y_coord = pyinputplus.inputInt('ENTER Y LOCTAION [1,2,3...] > ', min=0, max=45)
		Draw.clear_lines(50, 56)
		

		return (x_coord, y_coord)

	def console(input):
		"""
		Write to the bottom console.

		Args:
			input (str): The input to be written to the console.
		"""
		bext.fg('RED')
		if len(console_prompts) > 9:
			console_prompts.pop(0)
		console_prompts.append(input)
		Draw.clear_lines(50, 60)
		for i, output in enumerate(console_prompts):
			bext.goto(2, 50+i)
			if type(output) == str:
				print(f">> {output}")
			else:
				output
		bext.fg('reset')
		sys.stdout.flush()

	def player_list(allies:list, enemies:list, player:str):
		"""
		Show a list of enemies and allies, as well as the player's country.

		Args:
			allies (list): List of allies.
			enemies (list): List of enemies.
			player (str): The player's country.
		"""
		Draw.clear_to_edge(2, 30, 180)

		disabled_colour = 'yellow'

		bext.fg('reset')
		bext.goto(180,2)
		print('##############')
		bext.goto(180, 3)
		print('#   ALLIES:  #')
		for y, ally in enumerate(allies):
			status = countries[ally]['status']
			if status == True:
				bext.fg('purple')
			elif status == False:
				bext.fg(disabled_colour)
			bext.goto(184,4+y)
			print(ally)
			bext.fg('RESET')

		bext.fg('reset')
		bext.goto(195,2)
		print('##############')
		bext.goto(195, 3)
		print('#   ENEMIES:  #')
		for y, enemy in enumerate(enemies):
			status = countries[enemy]['status']
			if status == True:
				bext.fg('RED')
			elif status == False:
				bext.fg(disabled_colour)
			bext.goto(199, 4+y)
			print(enemy)
			bext.fg('RESET')

		bext.goto(60,47)
		bext.fg('BLACK')
		bext.bg('YELLOW')
		print(f" YOU ARE: {player} ")
		bext.fg('reset')
		bext.bg('reset')

	def clear_lines(Y_START, Y_END):
		"""
		Clear a range of lines.

		Args:
			Y_START (int): The starting y-coordinate.
			Y_END (int): The ending y-coordinate.
		"""
		for y in range(Y_START, Y_END):
			for x in range(WIDTH):
				bext.goto(x, y)
				print(' ', end='')

	def clear_console():
		"""
		Clear the console.
		"""
		Draw.clear_lines(48, HEIGHT)
		bext.fg('reset')
		bext.bg('reset')
		bext.goto(0, 48)
	
	def clear_screen():
		"""
		Clear the entire screen.
		"""
		Draw.clear_to_edge(0, bext.height(), 0)

	def clear_to_edge(y_start, y_end, x_start):
		"""
		Clear lines from x to the right end of the screen.

		Args:
			y_start (int): The starting y-coordinate.
			y_end (int): The ending y-coordinate.
			x_start (int): The starting x-coordinate.
		"""
		for y in range(y_start, y_end):
			for x in range(x_start, WIDTH):
				bext.goto(x, y)
				print(' ', end='')

	def get_original_character(x,y):
		"""
		Get the original character from the map.

		Args:
			x (int): The x-coordinate.
			y (int): The y-coordinate.

		Returns:
			str: The original character at the specified coordinates.
		"""
		map_lines = WORLD_MAP.splitlines()
		characters = list(map_lines[round(y)])

		return characters[round(x)] 

	def ocean(x1, x2, y):
		"""
		Draw an ocean between two points.

		Args:
			x1 (int): The starting x-coordinate.
			x2 (int): The ending x-coordinate.
			y (int): The y-coordinate.
		"""
		for x in range(x1, x2):
			bext.goto(x, y)
			bext.bg('BLUE')
			bext.fg('white')
			print('-', end='')
