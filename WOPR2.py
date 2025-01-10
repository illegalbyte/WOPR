from decimal import ROUND_DOWN
from pprint import pprint
from random import randint, choice
import bext
import pyinputplus
import sys
import time
import math
import a_star
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
# silo locations, organised by regions
countries = {
		'GERMANY': { 
			'location': (91, 10), 
			'status': True,
			'region': 'EUROPE',
			'subs': [],
			},
		'FRANCE': { 
			'location': (81, 12),
			'status': True,
			'region': 'EUROPE',
			'subs': [],
			},
		'RUSSIA': { 
			'location': (99, 9),
			'status': True,
			'region': 'EUROPE',
			'subs': [],
			},
		'COLOMBIA': { 
			'location': (49, 23),
			'status': True,
			'region': 'AMERICAS',
			'subs': [],
			},
		'USA': { 
			'location': (34, 14),
			'status': True,
			'region': 'AMERICAS',
			'subs': [],
			},
		'CHINA': { 
			'location': (121, 15),
			'status': True,
			'region': 'ASIA',
			'subs': [],
			},
		'INDIA': {
			'location': (110, 20),
			'status': True,
			'region': 'ASIA',
			'subs': [],
			},
		'PAKISTAN': {
			'location': (107, 17),
			'status': True,
			'region': 'ASIA',
			'subs': [],
		},
		'AUSTRALIA': {
			'location': (132, 30),
			'status': True,
			'region': 'PACIFIC',
			'subs': [],
			}
}
# console prompts list (stores the prompts for the game)
console_prompts = []
# Read world map from map .txt file 
with open('WORLD_MAP.txt', 'r') as map:
	WORLD_MAP = map.read()
WORLD_MAP_GRAPH = WORLD_MAP.splitlines() # splits the string into a list, using "\n" as the delimiter
WORLD_MAP_GRAPH = [list(line) for line in WORLD_MAP_GRAPH] # converts each line of the map to a list (mutable) instead of a string (immutable)
# CHANGE RECURSION LIMIT FOR FLOOD FILL
sys.setrecursionlimit(len(WORLD_MAP_GRAPH)*len(WORLD_MAP_GRAPH[0])*2)


class Utility():
	"""
	Utility class containing helper functions for the game.
	"""

	def remove_duplicates(lst):
		"""
		Remove duplicates from a list.

		Args:
			lst (list): The list from which duplicates need to be removed.

		Returns:
			list: A list with duplicates removed.
		"""
		return list(set([i for i in lst]))

	def reverse_lookup_submarine(submarine: tuple) -> str:
		"""
		Reverse lookup to find the country of a submarine.

		Args:
			submarine (tuple): The coordinates of the submarine.

		Returns:
			str: The country to which the submarine belongs.
		"""
		for country in countries:
			if countries[country]['subs']:
				if submarine in countries[country]['subs']:
					return country


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


class Submarine:
	"""
	Class representing a submarine.
	"""
	allies = []
	enemies = []

	def __init__(self, xy: tuple, country: str):
		"""
		Initialize a submarine.

		Args:
			xy (tuple): The coordinates of the submarine.
			country (str): The country to which the submarine belongs.
		"""
		self.country = country
		self.coords = xy
		self.status = True
		self.destroyed = False
		self.allies.append(self.country)


class Missiles():
	"""
	Class containing functions related to firing and drawing missiles.
	"""

	def get_distance(x1: int, y1: int, x2: int , y2: int) -> int:
		"""
		Calculate the distance between two coordinates.

		Args:
			x1 (int): The x-coordinate of the first point.
			y1 (int): The y-coordinate of the first point.
			x2 (int): The x-coordinate of the second point.
			y2 (int): The y-coordinate of the second point.

		Returns:
			int: The distance between the two points.
		"""
		return math.hypot(x2-x1, y2-y1)
	
	def ICBM_gentle(STRIKE_X, STRIKE_Y, START_X=40, START_Y=17, ICON='X', COLOUR='PURPLE'):
		"""
		Launch a missile in a line and then move diagonally towards the target.

		Args:
			STRIKE_X (int): The x-coordinate of the strike.
			STRIKE_Y (int): The y-coordinate of the strike.
			START_X (int): The starting x-coordinate.
			START_Y (int): The starting y-coordinate.
			ICON (str): The icon representing the missile.
			COLOUR (str): The color of the missile.
		"""
		while (START_X, START_Y) != (STRIKE_X, STRIKE_Y):

			Draw.draw_char(START_X, START_Y, ICON, COLOUR=COLOUR)

			START_X += randint(0,1)

			NEW_SHORTEST_DIST = Missiles.get_distance(START_X, START_Y + 1, STRIKE_X, STRIKE_Y)
			if Missiles.get_distance(START_X - 1, START_Y, STRIKE_X, STRIKE_Y) < NEW_SHORTEST_DIST:
				NEW_SHORTEST_DIST = Missiles.get_distance(START_X - 1, START_Y, STRIKE_X, STRIKE_Y)
			if Missiles.get_distance(START_X + 1, START_Y, STRIKE_X, STRIKE_Y) < NEW_SHORTEST_DIST:
				NEW_SHORTEST_DIST = Missiles.get_distance(START_X + 1, START_Y, STRIKE_X, STRIKE_Y)
			if Missiles.get_distance(START_X, START_Y - 1, STRIKE_X, STRIKE_Y) < NEW_SHORTEST_DIST:
				NEW_SHORTEST_DIST = Missiles.get_distance(START_X, START_Y - 1, STRIKE_X, STRIKE_Y)
			if Missiles.get_distance(START_X, START_Y + 1, STRIKE_X, STRIKE_Y) == NEW_SHORTEST_DIST:
				START_Y += 1
			elif Missiles.get_distance(START_X - 1, START_Y, STRIKE_X, STRIKE_Y) == NEW_SHORTEST_DIST:
				START_X -= 1
			elif Missiles.get_distance(START_X + 1, START_Y, STRIKE_X, STRIKE_Y) == NEW_SHORTEST_DIST:
				START_X += 1
			elif Missiles.get_distance(START_X, START_Y - 1, STRIKE_X, STRIKE_Y) == NEW_SHORTEST_DIST:
				START_Y -= 1

			time.sleep(REFRESH_RATE)

	def ICBM_diag(START_X, START_Y, STRIKE_X, STRIKE_Y, COL='PURPLE', ICON='🌞', REFRESH_RATE=REFRESH_RATE):
		"""
		Launch a missile in an angled diagonal line.

		Args:
			START_X (int): The starting x-coordinate.
			START_Y (int): The starting y-coordinate.
			STRIKE_X (int): The x-coordinate of the strike.
			STRIKE_Y (int): The y-coordinate of the strike.
			COL (str): The color of the missile.
			ICON (str): The icon representing the missile.
			REFRESH_RATE (float): The speed of the missile.
		"""
		if STRIKE_X == START_X:
			STRIKE_X += 1
		elif STRIKE_Y == STRIKE_Y:
			STRIKE_Y += 1
		slope = (STRIKE_Y - START_Y) / (STRIKE_X - START_X)

		if (abs(START_X - STRIKE_X) < 4):
			Missiles.ICBM_gentle(STRIKE_X, STRIKE_Y, START_X, START_Y)
		else:
			if STRIKE_X > START_X:
				prev_xy = []
				for x in range(START_X, STRIKE_X):
					prev_xy = [x, START_Y]
					prev_char = Draw.get_original_character(prev_xy[0], round(prev_xy[1]))
					Draw.draw_char(x, START_Y, ICON, COLOUR=COL)
					START_Y += slope
					time.sleep(REFRESH_RATE)
					Draw.draw_char(prev_xy[0], prev_xy[1], prev_char, COLOUR='YELLOW')
			elif STRIKE_X < START_X:
				prev_xy = []
				for x in range(START_X-STRIKE_X):
					prev_xy = [START_X-x, START_Y]
					prev_char = Draw.get_original_character(prev_xy[0], round(prev_xy[1]))
					Draw.draw_char(START_X-x, START_Y, ICON, COLOUR=COL)
					START_Y -= slope
					time.sleep(REFRESH_RATE)
					Draw.draw_char(prev_xy[0], prev_xy[1], prev_char, COLOUR='YELLOW')
			
		Draw.draw_char(STRIKE_X, STRIKE_Y-1, '🌞')

	def ICBM_bresenham(start: tuple, strike: tuple, chemtrail=True, speed=0.4):
		"""
		Launch a missile from start to strike using the Bresenham algorithm.

		Args:
			start (tuple): The starting coordinates.
			strike (tuple): The coordinates of the strike.
			chemtrail (bool): Whether to draw a chemtrail.
			speed (float): The speed of the missile.

		Returns:
			list: List of coordinates affected by the missile.
		"""
		chemtrail_colour = "WHITE"
		chemtrail_icon = "*"
		line = Draw.get_line(start, strike)
		for xy in line:
			Draw.draw_char(xy[0], xy[1], chemtrail_icon, COLOUR=chemtrail_colour)
			time.sleep(speed)
			if xy == strike:
				fallout = Draw.draw_fallout(strike, 2, speed/2, "purple", "*")
				break

		return fallout


class Map():
	"""
	Class containing methods and attributes for the game map.
	"""

	def print_map(COLOUR: str, SPEED: float, ocean=False):
		"""
		Print the game map.

		Args:
			COLOUR (str): The color of the map.
			SPEED (float): The speed of printing the map.
			ocean (bool): Whether to print the ocean.
		"""
		bext.clear()
		X = 0
		Y = 0
		for character in WORLD_MAP:
			bext.goto(X, Y)
			bext.fg(COLOUR)
			print(character, end='')
			time.sleep(SPEED)
			X += 1
			if character == '\n':
				Y += 1
				X = 0
			sys.stdout.flush()
		if ocean:
			Map.print_ocean()

	def print_ocean(SYMBOL: str="^", OCEAN_COLOUR: str="CYAN"):
		"""
		Print the ocean on the map.

		Args:
			SYMBOL (str): The symbol representing the ocean.
			OCEAN_COLOUR (str): The color of the ocean.
		"""
		with open('WATER_COORDS.txt', 'r') as f:
			xy_ocean_coords = ast.literal_eval(f.read())
			
		for xy in xy_ocean_coords:
			Draw.draw_char(xy[0], xy[1], SYMBOL, COLOUR=OCEAN_COLOUR)

	def get_ocean_tiles() -> list:
		"""
		Get the coordinates of ocean tiles.

		Returns:
			list: List of coordinates of ocean tiles.
		"""
		with open('WATER_COORDS.txt', 'r') as f:
			xy_ocean_coords = ast.literal_eval(f.read())
		return xy_ocean_coords

	def check_for_ocean(x, y) -> bool:
		"""
		Check if a tile is an ocean tile.

		Args:
			x (int): The x-coordinate.
			y (int): The y-coordinate.

		Returns:
			bool: True if the tile is an ocean tile, False otherwise.
		"""
		ocean_tiles = Map.get_ocean_tiles()
		if x < 2:
			return False
		if (x, y) in ocean_tiles:
			return True
		else:
			return False

	def check_for_obstruction(list_of_coords: list) -> bool:
		"""
		Check if a list of coordinates is entirely ocean.

		Args:
			list_of_coords (list): List of coordinates to check.

		Returns:
			bool: True if all coordinates are ocean tiles, False otherwise.
		"""
		for xy in list_of_coords:
			if not Map.check_for_ocean(xy[0], xy[1]):
				return False
		return True

	def convert_x_coord(x: str) -> int:
		"""
		Convert a grid coordinate to a screen coordinate.

		Args:
			x (str): The grid coordinate.

		Returns:
			int: The screen coordinate.
		"""
		alpha = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]
		x_values = [6, 12, 18, 24, 30, 36, 42, 48, 54, 60, 66, 72, 78, 84, 90, 96, 102, 108, 114, 120, 126, 132, 138, 144, 150]
		x_values_dict = dict(zip(alpha, x_values))
		return x_values_dict[x.upper()]-2

	def get_coordinates_inside_circle(circle_center: tuple, circle_coords: list) -> list:
		"""
		Get coordinates inside a circle.

		Args:
			circle_center (tuple): The center of the circle.
			circle_coords (list): List of coordinates of the circle's perimeter.

		Returns:
			list: List of coordinates inside the circle.
		"""
		coords_in_circle = []
		for x, y in circle_coords:
			line = Draw.get_line((circle_center[0], circle_center[1]), (x, y))
			for x, y in line:
				if (x, y) not in coords_in_circle:
					coords_in_circle.append((x, y))
		
		return coords_in_circle

	def print_subs(player="", enemies=[], allies=[], REVEALED_ENEMIES=[]):
		"""
		Draw enemy submarines.

		Args:
			player (str): The player's country.
			enemies (list): List of enemies.
			allies (list): List of allies.
			REVEALED_ENEMIES (list): List of revealed enemy submarines.
		"""
		for country_name, country_data in countries.items():
			if country_name in enemies:
				for sub in country_data['subs']:
					Draw.draw_char(sub[0], sub[1], '𝑆', COLOUR="RED")
			elif country_name in allies:
				for sub in country_data['subs']:
					Draw.draw_char(sub[0], sub[1], '𝑆', COLOUR="WHITE")
			elif country_name == player:
				for sub in country_data['subs']:
					Draw.draw_char(sub[0], sub[1], '𝑆', COLOUR="PURPLE")
		for XY_tuple in REVEALED_ENEMIES:
			Draw.draw_char(XY_tuple[0], XY_tuple[1], '𝑆', COLOUR="RED")

	def print_silos(player: str, enemies: list, allies: list):
		"""
		Draw silos on the map.

		Args:
			player (str): The player's country.
			enemies (list): List of enemies.
			allies (list): List of allies.
		"""
		for country in countries:
			if country == player:
				bext.fg('purple')
			elif country in enemies:
				bext.fg('red')
			elif country in allies:
				bext.fg('white')
			elif countries[country]['status'] == False:
				bext.fg('blue')
			bext.goto(countries[country]['location'][0],
					countries[country]['location'][1])
			print('@')

	def print_all_layers(player: str, enemies: list, allies: list, Found_Enemy_Subs: list = []):
		"""
		Print all layers of the map.

		Args:
			player (str): The player's country.
			enemies (list): List of enemies.
			allies (list): List of allies.
			Found_Enemy_Subs (list): List of found enemy submarines.
		"""
		Map.print_map(COLOUR='GREEN', SPEED=REFRESH_RATE)
		Map.print_ocean()
		Map.print_subs(player=player, allies=allies, enemies=enemies)
		Draw.player_list(allies, enemies, player)
		Map.print_silos(player=player, enemies=enemies, allies=allies)
		

	def print_ocean_dev(MAP, TERRAIN_COLOUR="yellow", OCEAN_COLOUR="cyan"):
		"""
		Print the ocean for development purposes.

		Args:
			MAP (list): The map.
			TERRAIN_COLOUR (str): The color of the terrain.
			OCEAN_COLOUR (str): The color of the ocean.
		"""
		for y in range(len(MAP)):
			for x in range(len(MAP[y])):
				if MAP[y][x] == ' ':
					Draw.draw_char(x, y, MAP[y][x], COLOUR=TERRAIN_COLOUR)
				elif MAP[y][x] == '^':
					Draw.draw_char(x, y, MAP[y][x], COLOUR=OCEAN_COLOUR)
				else:
					Draw.draw_char(x, y, MAP[y][x], COLOUR=TERRAIN_COLOUR)
				sys.stdout.flush()

	def find_oceans_dev():
		"""
		Tool for mapping the ocean onto the map.
		"""
		def draw_waters(colour="cyan", char="+"):
			water_coords_list = []
			with open('waters.txt', 'r') as waters:
				for line in waters:
					coords = ast.literal_eval(line)
					for xy in coords:
						water_coords_list.append(xy)
			for xy in water_coords_list:
				Draw.draw_char(xy[0], xy[1], COLOUR=colour, CHAR=char)
				time.sleep(0.0002)
		
		
		while not True:
			try:
				start_y += 1
			except UnboundLocalError:
				Draw.clear_screen()
				Map.print_map('yellow', 0.00002)
				Draw.clear_console()
				start_y =  pyinputplus.inputInt('Enter starting y coordinate: ', min=1, max=45)
			else:
				MapStatus = True
				while MapStatus:
					Draw.clear_screen()
					Map.print_map('yellow', 0.00002)
					draw_waters(colour="cyan", char="^")
					Draw.clear_console()

					draw_waters(colour="cyan", char="^")

					Draw.clear_console()		
					Draw.console(f"y coordinate is: {start_y}")
					
					start_x = convert_x_coord(pyinputplus.inputStr('Enter starting x coordinate (ABC...): '))
					Draw.clear_console()
					bext.goto(start_x, start_y)
					Draw.draw_char(start_x, start_y, CHAR='X', COLOUR="WHITE")
					Draw.clear_console()
					if Draw.get_original_character(start_x, start_y) != ' ':
						Draw.clear_console()
						Draw.console(f"The space is not empty, please try again")
						time.sleep(0.5)
						continue
					correct_positioning = str(pyinputplus.inputYesNo('Is this the correct position? ')).upper()
					if correct_positioning == "YES":
						x_left = start_x - 1
						while Draw.get_original_character(x_left, start_y) == ' ':
							Draw.draw_char(x_left, start_y, CHAR='~', COLOUR="BLUE")
							x_left -= 1
							time.sleep(SMALL_PAUSE)
						left_ocean = list(range(x_left+1, start_x))
						x_right = start_x + 1
						while Draw.get_original_character(x_right, start_y) == ' ' and x_right < 152:
							Draw.draw_char(x_right, start_y, CHAR='~', COLOUR="BLUE")
							x_right += 1
							time.sleep(SMALL_PAUSE)
						right_ocean = list(range(start_x, x_right))

						new_ocean_tiles_list = left_ocean + right_ocean

						Map.print_map('yellow', 0.00002)
						Draw.clear_console()
						for x in new_ocean_tiles_list:
							Draw.draw_char(x, start_y, CHAR='~', COLOUR="BLUE")
							time.sleep(SMALL_PAUSE)

						Draw.clear_console()
						correctly_drawn = str(pyinputplus.inputYesNo('Is this the correct ocean? ')).upper()
						if correctly_drawn == "YES":
							ocean_tiles_coords = []
							for x in new_ocean_tiles_list:
								ocean_tiles_coords.append((x, start_y))
							with open('waters.txt', 'a') as file:
								file.write(str(ocean_tiles_coords))
								file.write('\n')
								file.close()
							Draw.clear_console()
							print('Ocean saved!')
							time.sleep(SMALL_PAUSE)
						else:
							continue

						more_maps = pyinputplus.inputMenu(["Yes", "No"], 'Do you want to save more maps?\n', numbered=True)
						Draw.console(more_maps)

						Draw.clear_console()

						if more_maps == "Yes":
							start_y += 1
							continue
						else:
							MapStatus = False
					else:
						continue

		def flood_fill(matrix, x, y, old, new):
			if x < 0 or x >= len(matrix[0]) or y < 1 or y >= len(matrix)-1:
				return
			if matrix[y][x] != old:
				return

			matrix[y][x] = new
			flood_fill(matrix, x+1, y, old, new)
			flood_fill(matrix, x-1, y, old, new)
			flood_fill(matrix, x, y+1, old, new)
			flood_fill(matrix, x, y-1, old, new)
			return matrix


		ocean_map = flood_fill(WORLD_MAP_GRAPH, 110, 28, " ", "^")
		WATER_COORDS = [] 
		for y in range(len(ocean_map)):
			for x in range(len(ocean_map[y])):
				if ocean_map[y][x] == "^":
					WATER_COORDS.append((x, y))
		with open("WATER_COORDS.txt", "a") as f:
			f.write(str(WATER_COORDS))


def classic_mode():
	"""
	Classic mode of the game.
	"""
	bext.clear()
	Map.print_map("green", REFRESH_RATE)
	unassigned_countries = []

	for country in countries:
		countries[country]['status'] = True
		unassigned_countries.append(country)

	all_countries = unassigned_countries.copy()

	bext.goto(0, 48)
	player_country = pyinputplus.inputMenu(
		unassigned_countries, "CHOOSE A COUNTRY:\n", numbered=True)

	unassigned_countries.remove(player_country)

	allies = []
	enemies = []

	ally_limit = randint(2,5)
	enemies_limit = len(all_countries) - ally_limit

	for country in unassigned_countries:
		if len(allies) < ally_limit:
			allies.append(country)
		else:
			enemies.append(country)

	original_allies = allies.copy()
	original_enemies = enemies.copy()

	Draw.player_list(allies, enemies, player_country)

	def draw_bases():
		for country in countries:
			if country == player_country:
				bext.fg('yellow')
			elif country in enemies:
				bext.fg('red')
			elif country in allies:
				bext.fg('white')
			elif countries[country]['status'] == False:
				bext.fg('blue')
			bext.goto(countries[country]['location'][0],
					countries[country]['location'][1])
			print('@')

	def playermove():
		"""
		Ask the player what countries it should target.
		"""
		Draw.clear_console()

		if len(enemies) > 1:
			target = pyinputplus.inputMenu(enemies, "CHOSE A COUNTRY TO TARGET:\n", lettered=True)
		else:
			target = enemies[0]			

		start_x = countries[player_country]['location'][0]
		start_y = countries[player_country]['location'][1]
		strike_x = countries[target]['location'][0]
		strike_y = countries[target]['location'][1]

		Missiles.ICBM_diag(start_x, start_y, strike_x, strike_y, REFRESH_RATE=0.05, COL='YELLOW', ICON='>')
		Draw.draw_fallout((strike_x, strike_y), 2, 0.05, "purple", "*")

		enemies.remove(target)
		countries[target]['status'] = False

	def automove():
		"""
		Randomly selects a country to fire at one of its enemies.
		"""
		remaining_countries = enemies + allies 
		start = choice(remaining_countries)
		remaining_countries.remove(start)
		if start in enemies:
			possible_targets = allies
			possible_targets.append(player_country)
		elif start in allies:
			possible_targets = enemies
		target = choice(possible_targets)

		start_x = countries[start]['location'][0]
		start_y = countries[start]['location'][1]
		strike_x = countries[target]['location'][0]
		strike_y = countries[target]['location'][1]


		if target in enemies:
			enemies.remove(target)
			countries[target]['status'] = False
		elif target in allies:
			allies.remove(target)
			countries[target]['status'] = False
		elif target == player_country:
			countries[target]['status'] = False

		Missiles.ICBM_diag(start_x, start_y, strike_x, strike_y, REFRESH_RATE=0.05, COL='YELLOW', ICON='>')
		Draw.draw_fallout(strike_x, strike_y, RADIUS=1)
		draw_bases()

	def base_message(text: str, country: str):
		"""
		Print a message at a specific country's silo location.

		Args:
			text (str): The message to be printed.
			country (str): The country where the message will be printed.
		"""
		bext.goto(countries[country]['location'][0],
					countries[country]['location'][1])
		bext.bg('RED')
		bext.fg('BLACK')
		print(text)
		bext.bg('reset')
		bext.fg('reset')
		time.sleep(10)
		



	turn = 1
	while len(enemies) != 0 and (countries[player_country]['status'] == True):
		draw_bases()
		Draw.player_list(original_allies, original_enemies, player_country)
		if turn % 2 == 0 and countries[player_country]['status'] == True:
			automove()
		else:
			playermove()
		turn += 1
		Draw.player_list(original_allies, original_enemies, player_country)

	if countries[player_country]['status'] == False:
		base_message(f'YOU LOST IN {turn} TURNS, RESTARTING IN 10s', player_country)
	else:
		base_message(f'YOU WON IN {turn} TURNS, RESTARTING IN 10s', player_country)


class SubsAndSilos():
	"""
	Class containing functions for the Submarines and Silos game mode.
	"""

	def display_map():
		"""
		Display the map of the game.
		"""
		bext.clear()
		Map.print_map("yellow", SPEED=REFRESH_RATE, ocean=True)
		Draw.clear_console()
		
	def ask_for_ocean_coords():
		"""
		Ask the user for the coordinates of the ocean.

		Returns:
			tuple: The coordinates of the ocean.
		"""
		space_is_not_ocean = True
		while space_is_not_ocean:
			x = Map.convert_x_coord(pyinputplus.inputStr(prompt="What is your sub's X coordinate in the ocean (A, B, C, etc): "))
			y = pyinputplus.inputInt("What is your sub's Y coordinate in the ocean (1, 2, 3, etc): ", min=1, max=45)
			if Map.check_for_ocean(x, y):
				space_is_not_ocean = False
			else:
				Draw.clear_console()
				Draw.console("That space is not ocean. Please try again.")
		return (x, y)

	def action_sonar(player_country: str, enemies: list, allies: list, radius: int) -> list:
		"""
		Perform a sonar around the submarine.

		Args:
			player_country (str): The player's country.
			enemies (list): List of enemies.
			allies (list): List of allies.
			radius (int): The radius of the sonar.

		Returns:
			list: List of coordinates that were made visible.
		"""
		player_sub = countries[player_country]['subs'][0]
		sonar = Draw.draw_circle(player_sub[0], player_sub[1], RADIUS=radius, COLOUR="BLUE")
		visible_coords = []
		for xy in sonar:
			if Missiles.get_distance(player_sub[0], player_sub[1], xy[0], xy[1]) < (radius * 1.2):
				coords = Draw.draw_line(player_sub[0], player_sub[1], xy[0], xy[1], COLOUR="BLUE")
				time.sleep(0.0002)
				visible_coords.extend(coords) 
			else:
				if player_sub[0] < (152 / 2):
					subx, suby = player_sub[0] + 154, player_sub[1]
					visible_coords.extend( Draw.draw_line(subx - 154, suby, 1, xy[1], COLOUR="BLUE"))
					visible_coords.extend( Draw.draw_line(subx, suby, xy[0], xy[1], COLOUR="BLUE"))
				else:
					subx, suby = player_sub[0] - 154, player_sub[1]
					visible_coords.extend( Draw.draw_line(player_sub[0], suby, 153, xy[1], COLOUR="BLUE"))
					visible_coords.extend( Draw.draw_line(subx, suby, xy[0], xy[1], COLOUR="BLUE"))

				time.sleep(0.006)
		return Utility.remove_duplicates(visible_coords)

	def action_attack(player_country):
		"""
		Perform an attack from the submarine.

		Args:
			player_country (str): The player's country.

		Returns:
			list: List of coordinates affected by the attack.
		"""
		circle = Draw.draw_circle(countries[player_country]['subs'][0][0], countries[player_country]['subs'][0][1], RADIUS=20, COLOUR="RED", erase_map_tiles=True)
		coords_inside_circle = Map.get_coordinates_inside_circle((countries[player_country]['subs'][0][0], countries[player_country]['subs'][0][1]), circle)	
		missile_coords_valid = False
		while not missile_coords_valid:
			Draw.clear_console()
			target_coords = Draw.ask_for_coordinates()
			if target_coords in coords_inside_circle:
				missile_coords_valid = True
			else:
				Draw.clear_console()
				Draw.console("ERR: TARGET NOT IN PROXIMITY!")
				time.sleep(2)
		return Missiles.ICBM_bresenham(countries[player_country]['subs'][0], target_coords)
				
	def action_move(subxy: tuple, direction: str, distance: int):
		"""
		Move the submarine in the specified direction.

		Args:
			subxy (tuple): The current coordinates of the submarine.
			direction (str): The direction to move.
			distance (int): The distance to move.

		Returns:
			tuple: The new coordinates of the submarine if valid, False otherwise.
		"""
		if direction == "N":
			moveto = (subxy[0], subxy[1] - distance)
		elif direction == "S":
			moveto = (subxy[0], subxy[1] + distance)
		elif direction == "W":
			moveto = (subxy[0] - distance, subxy[1])
		elif direction == "E":
			moveto = (subxy[0] + distance, subxy[1])

		if Map.check_for_ocean(moveto[0], moveto[1]):
			return moveto
		else:
			return False

	def search_for_subs(seeking_countries: list, search_coords: list):
		"""
		Search for submarines in the specified coordinates.

		Args:
			seeking_countries (list): List of countries to search for.
			search_coords (list): List of coordinates to search.

		Returns:
			list: List of found submarines.
		"""
		sub_coords = []
		for country_name, country_data in countries.items():
			if country_name in seeking_countries:
				sub_coords.extend(country_data["subs"])
		
		found_subs = []
		for sub_coords in sub_coords:
			if sub_coords in search_coords:
				found_subs.append(sub_coords)

		return found_subs

	def setup_game():
		"""
		Set up the game.

		Returns:
			tuple: The player's country, list of enemies, list of allies, original list of allies, original list of enemies.
		"""
		unassigned_countries = []

		for country in countries:
			countries[country]['status'] = True
			unassigned_countries.append(country)

		all_countries = unassigned_countries.copy()

		bext.goto(0, 48)
		player_country = pyinputplus.inputMenu(
			unassigned_countries, "CHOOSE A COUNTRY:\n", numbered=True)

		unassigned_countries.remove(player_country)

		allies = []
		enemies = []

		ally_limit = randint(2,5)
		enemies_limit = len(all_countries) - ally_limit

		for country in unassigned_countries:
			if len(allies) < ally_limit:
				allies.append(country)
			else:
				enemies.append(country)

		original_allies = allies.copy()
		original_enemies = enemies.copy()

		Draw.player_list(allies, enemies, player_country)

		Map.print_silos(player_country, enemies, allies)
		
		Draw.clear_console()
		player_sub_x, player_sub_y = SubsAndSilos.ask_for_ocean_coords()
		countries[player_country]['subs'].append((player_sub_x, player_sub_y))
		
		ocean_coords = Map.get_ocean_tiles()
		for country_name, country_data in countries.items():
			if country_name in enemies or country_name in allies and not country_name == player_country:
				country_data['subs'].append(choice(ocean_coords))
		
		Map.print_subs(player_country, allies=allies)

		return player_country, enemies, allies, original_allies, original_enemies
			

	def player_move(player_country, enemies, allies, original_allies, original_enemies):
		"""
		Handle the player's turn.

		Args:
			player_country (str): The player's country.
			enemies (list): List of enemies.
			allies (list): List of allies.
			original_allies (list): Original list of allies.
			original_enemies (list): Original list of enemies.

		Returns:
			tuple: Updated player country, list of enemies, list of allies, original list of allies, original list of enemies.
		"""
		Map.print_all_layers(player_country, enemies, allies, Found_Enemy_Subs=enemies)
		Draw.clear_console()
		action = pyinputplus.inputMenu(["Move", "Attack", "Detect", "End Turn"], "What would you like to do?\n", lettered=True)
		Draw.clear_console()
		player_sub_x, player_sub_y = countries[player_country]['subs'][0]
		if action == "Move":
			distance_max = 10
			Draw.draw_circle(player_sub_x, player_sub_y, RADIUS=distance_max, COLOUR="GREEN")
			Draw.clear_console()
			move_direction = pyinputplus.inputMenu(["N", "S", "E", "W"], "What direction would you like to move?\n", lettered=True)
			move_distance = pyinputplus.inputInt("How many tiles would you like to move?\n", min=1, max=distance_max-1)
			new_sub_coords = SubsAndSilos.action_move((player_sub_x, player_sub_y), move_direction, move_distance)
			if new_sub_coords:
				countries[player_country]['subs'][0] = SubsAndSilos.action_move(countries[player_country]['subs'][0], move_direction, move_distance)
				Draw.clear_console()
		elif action == "Attack":
			destroyed_coords = SubsAndSilos.action_attack(player_country)
			destroyed_subs = SubsAndSilos.search_for_subs(enemies, destroyed_coords)
			for sub in destroyed_subs:
				country = Utility.reverse_lookup_submarine(sub)
				Draw.console(f"IDENTIFIED TARGET: {country} SUBMARINE WARHEAD CARRIER DESTROYED")
				time.sleep(0.4)
				countries[country]['subs'].remove(sub)
				if sub in enemies:
					enemies.remove(sub)
				if sub in allies:
					allies.remove(sub)
			time.sleep(2)
		elif action == "Detect":
			visible_coords = SubsAndSilos.action_sonar(player_country, enemies, allies, 13)
			visible_subs = SubsAndSilos.search_for_subs(enemies, visible_coords)
			if visible_subs:
				Draw.console(f"Detected enemies at: {visible_subs}")
				time.sleep(5)
			
		return player_country, enemies, allies, original_allies, original_enemies

	def enemy_move(player_country, enemies, allies, original_allies, original_enemies):
		"""
		Handle the enemy's turn.

		Args:
			player_country (str): The player's country.
			enemies (list): List of enemies.
			allies (list): List of allies.
			original_allies (list): Original list of allies.
			original_enemies (list): Original list of enemies.
		"""
		Map.print_all_layers(player_country, enemies, allies, Found_Enemy_Subs=enemies)
		Draw.clear_console()
		for country in enemies:
			move_valid = False
			while not move_valid:
				move_distance = randint(5,10)
				possible_moves = Draw.draw_circle(countries[country]['subs'][0][0], countries[country]['subs'][0][1], RADIUS=move_distance, visible=False)
				new_sub_coords = choice(possible_moves)
				travel_line = Draw.get_line(countries[country]["subs"][0], new_sub_coords)
				if new_sub_coords and Map.check_for_obstruction(travel_line):
					move_valid = True
			countries[country]["subs"][0] = new_sub_coords
			
			Draw.console(f"{country} SUBMARINE WARHEAD CARRIER MOVED")
			time.sleep(0.8)
			for tile in travel_line:
				if tile == new_sub_coords:
					Draw.draw_char(tile[0], tile[1], "𝑆", COLOUR="RED")
				else:
					Draw.draw_char(tile[0], tile[1], ">", COLOUR="GREEN")
				time.sleep(0.1)
			time.sleep(3)



def submarinesandsilos():
	"""
	Main function for the Submarines and Silos game mode.
	"""
	SubsAndSilos.display_map()
	player_country, enemies, allies, original_allies, original_enemies = SubsAndSilos.setup_game()

	while True:
		player_country, enemies, allies, original_allies, original_enemies = SubsAndSilos.player_move(player_country, enemies, allies, original_allies, original_enemies)
		SubsAndSilos.enemy_move(player_country, enemies, allies, original_allies, original_enemies)


def main():
	"""
	Main game loop.
	"""
	if WIDTH < 170 or HEIGHT < 60:
		print(f"TERMINAL WIDTH MUST BE > 170 characters wide and > 60 characters tall\nYour terminal is only: {WIDTH}px wide by {HEIGHT}px tall")

	while True:
		Draw.clear_console()
		classic_mode()
		sys.exit()


if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		print('Bye!')
