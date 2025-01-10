from random import randint, choice
import bext
import pyinputplus
import sys
import time
import math
from playsound import playsound

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
# Read world map from map .txt file 
with open('WORLD_MAP.txt', 'r') as map:
	WORLD_MAP = map.read()
WORLD_MAP_GRAPH = WORLD_MAP.splitlines() # splits the string into a list, using "\n" as the delimiter
WORLD_MAP_GRAPH = [list(line) for line in WORLD_MAP_GRAPH] # converts each line of the map to a list (mutable) instead of a string (immutable)
# CHANGE RECURSION LIMIT FOR FLOOD FILL
sys.setrecursionlimit(len(WORLD_MAP_GRAPH)*len(WORLD_MAP_GRAPH[0])*2)


class Utility():
	def remove_duplicates(lst):
		return list(set([i for i in lst]))

	def reverse_lookup_submarine(submarine: tuple) -> str:
		for country in countries:
			if countries[country]['subs']:
				if submarine in countries[country]['subs']:
					return country


class Draw():

	def draw_char(X, Y, CHAR: str, COLOUR='RED'):
		# DRAWS A CHARACTER AT A SPECIFIC LOCATION
		bext.goto(round(X), round(Y))
		bext.fg(COLOUR)
		print(f'{CHAR}', end='')
		sys.stdout.flush()

	def draw_targets(regions: dict):
		'''DRAWS TARGETS FOR EACH REGION'''
		for region in regions.values():
			for country, target in region.items():
				x, y = target
				Draw.draw_char(x, y, r'{X}', COLOUR='WHITE')
	
	def draw_fallout_old(STRIKE_X, STRIKE_Y, RADIUS=2, SPEED=0.03, COLOUR="PURPLE", CHAR="X"):
		'''DRAWS RADIATION CIRCLE'''
		# https://www.mathopenref.com/coordcirclealgorithm.html
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
		'''
		Draws a hollow circle around the X, Y coords with specific RADIUS
		By default, the circle's perimeter will not draw over any spaces which are not blank in the WORLD_MAP matrix 

		--> raiud_modifier: divide the height of the circle by this number, so that it appears normally in terminals where the height of a char is usually 2x the width

		Returns a list of the coords of the perimiter of the circle
		'''
		# https://www.mathopenref.com/coordcirclealgorithm.html
		'''DRAWS A HOLLOW CIRCLE AROUND A SPECIFIC LOCATION
			Returns a list of the coordinates of the circle'''
			# TODO: separate the drawing of the circle from getting the coordinates
		circle = []
		theta = 0
		step = 2*math.pi/2000
		while theta <= 2*math.pi:
			# make circle twice as wide as it is tall
			x = X + RADIUS*math.cos(theta)
			y = Y - (RADIUS/radius_modifier)*math.sin(theta) # radius / 2 because the circle is drawn twice as wide as it is tall
			if x > 152:
				x = x - 152
			if x < 0: # prevent the circle from going off the screen, and wrap around
				x = x + 152
			if y > 45:
				theta += step
				continue
			if Draw.get_original_character(x, y) == ' ': # prevents drawing on top of map tiles
				if visible:
					Draw.draw_char(x, y, CHAR, COLOUR=COLOUR)
				if (round(x), round(y)) not in circle: # prevents duplicate x, y coords being added due to decimal differences
					circle.append((round(x), round(y)))	
			elif erase_map_tiles: # if we don't care about the map tiles, draw over them
				if visible:
					Draw.draw_char(x, y, CHAR, COLOUR=COLOUR)
				if (round(x), round(y)) not in circle: # prevents duplicate x, y coords being added due to decimal differences
					circle.append((round(x), round(y)))	
			theta += step

		return circle

	def get_line(start: tuple, end: tuple) -> list:
		"""Bresenham's Line Algorithm
		http://www.roguebasin.com/index.php/Bresenham%27s_Line_Algorithm#Python
		Produces a list of tuples from start and end

		>>> points1 = get_line((0, 0), (3, 4))
		>>> points2 = get_line((3, 4), (0, 0))
		>>> assert(set(points1) == set(points2))
		>>> print points1
		[(0, 0), (1, 1), (1, 2), (2, 3), (3, 4)]
		>>> print points2
		[(3, 4), (2, 3), (1, 2), (1, 1), (0, 0)]
		"""
		# Setup initial conditions
		x1, y1 = start
		x2, y2 = end
		dx = x2 - x1
		dy = y2 - y1

		# Determine how steep the line is
		is_steep = abs(dy) > abs(dx)

		# Rotate line
		if is_steep:
			x1, y1 = y1, x1
			x2, y2 = y2, x2

		# Swap start and end points if necessary and store swap state
		swapped = False
		if x1 > x2:
			x1, x2 = x2, x1
			y1, y2 = y2, y1
			swapped = True

		# Recalculate differentials
		dx = x2 - x1
		dy = y2 - y1

		# Calculate error
		error = int(dx / 2.0)
		ystep = 1 if y1 < y2 else -1

		# Iterate over bounding box generating points between start and end
		y = y1
		points = []
		for x in range(x1, x2 + 1):
			coord = (y, x) if is_steep else (x, y)
			points.append(coord)
			error -= abs(dy)
			if error < 0:
				y += ystep
				error += dx

		# Reverse the list if the coordinates were swapped
		if swapped:
			points.reverse()
		return points

	def draw_line(x1, y1, x2, y2, COLOUR='RED', ocean_only=True) -> list:
		'''draws a line between two points – returns a list of all the coords that were drawn'''
		points = Draw.get_line((round(x1), round(y1)), (round(x2), round(y2)))
		valid_points = []
		for point in points:
			x, y = point
			if x > 152: # prevent the line from going off the screen, and wrap around
				continue
			# check if ocean tile
			if ocean_only and not Map.check_for_ocean(x,y):
				continue
			Draw.draw_char(x, y, 'X', COLOUR=COLOUR)
			valid_points.append((x,y))
		return valid_points

	def ask_for_coordinates() -> tuple:
		'''prints dialogue at the bottom which asks for coordinates and returns a tuple of the (x, y)'''
		Draw.clear_console()
		bext.fg('RED')
		x_coord = "0" # placeholder val so we can start a while loop below
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
		'''write to the bottom console'''
		bext.fg('RED')
		# ensures console the prompts don't print past the height of terminal
		if len(console_prompts) > 9:
			console_prompts.pop(0)
		console_prompts.append(input)
		# for each 
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
		'''Shows a list of enemies and allies, as well as the player's country
		Colour of country printed will change when it's status is False ie when it's destroyed'''
		# clear the screen so that updated info can be displayed
		Draw.clear_to_edge(2, 30, 180)

		'''Takes the list of allies, enemies, and the player's country
		and displays a list of them to the right of the map'''
		disabled_colour = 'yellow'

		# print the list of allies
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

		# print the list of enemies
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

		# prints the player's country at the bottom of the map
		bext.goto(60,47)
		bext.fg('BLACK')
		bext.bg('YELLOW')
		print(f" YOU ARE: {player} ")
		bext.fg('reset')
		bext.bg('reset')

	def clear_lines(Y_START, Y_END):
		'''CLEARES A RANGE OF LINES, USED FOR TEXT ENTRY AT BOTTOM OF SCREEN'''
		for y in range(Y_START, Y_END):
			for x in range(WIDTH):
				bext.goto(x, y)
				print(' ', end='')

	def clear_console():
		Draw.clear_lines(48, HEIGHT)
		bext.fg('reset')
		bext.bg('reset')
		bext.goto(0, 48)
	
	def clear_screen():
		Draw.clear_to_edge(0, bext.height(), 0)

	def clear_to_edge(y_start, y_end, x_start):
		'''Clears lines from x to the right end of the screen (ie the right edge)'''
		for y in range(y_start, y_end):
			for x in range(x_start, WIDTH):
				bext.goto(x, y)
				print(' ', end='')

	def get_original_character(x,y):
		'''For re-printing the previous character and keeping the map in tact
		takes an x,y and returns the original character from the original map
		assumes that WORLD_MAP variable has not changed from initial state'''
		map_lines = WORLD_MAP.splitlines()
		characters = list(map_lines[round(y)])

		return characters[round(x)] 

	def ocean(x1, x2, y):
		'''Draws an ocean between two points'''
		for x in range(x1, x2):
			bext.goto(x, y)
			bext.bg('BLUE')
			bext.fg('white')
			print('-', end='')


class Submarine:
	allies = []
	enemies = []

	def __init__(self, xy: tuple, country: str):
		self.country = country
		self.coords = xy
		self.status = True
		self.destroyed = False
		self.allies.append(self.country)


class Missiles():
	'''A bunch of functions related to firing and drawing missiles'''
	
	def get_distance(x1: int, y1: int, x2: int , y2: int) -> int:
		'''Returns the distance between two x,y coordinates'''
		return math.hypot(x2-x1, y2-y1)
	
	def ICBM_gentle(STRIKE_X, STRIKE_Y, START_X=40, START_Y=17, ICON='X', COLOUR='PURPLE'):
		'''this path algo launches a missile in a line and then when it is at a ~40° angle it will move diagonally towards target'''
		while (START_X, START_Y) != (STRIKE_X, STRIKE_Y):

			Draw.draw_char(START_X, START_Y, ICON, COLOUR=COLOUR)

			START_X += randint(0,1)

			# CALCULATES WHETHER A REDUCTION OR ADDITION TO X OR Y WILL CREATE THE NEW SHORTEST DISTANCE
			NEW_SHORTEST_DIST = Missiles.get_distance(START_X, START_Y + 1, STRIKE_X, STRIKE_Y)
			if Missiles.get_distance(START_X - 1, START_Y, STRIKE_X, STRIKE_Y) < NEW_SHORTEST_DIST:
				NEW_SHORTEST_DIST = Missiles.get_distance(START_X - 1, START_Y, STRIKE_X, STRIKE_Y)
			if Missiles.get_distance(START_X + 1, START_Y, STRIKE_X, STRIKE_Y) < NEW_SHORTEST_DIST:
				NEW_SHORTEST_DIST = Missiles.get_distance(START_X + 1, START_Y, STRIKE_X, STRIKE_Y)
			if Missiles.get_distance(START_X, START_Y - 1, STRIKE_X, STRIKE_Y) < NEW_SHORTEST_DIST:
				NEW_SHORTEST_DIST = Missiles.get_distance(START_X, START_Y - 1, STRIKE_X, STRIKE_Y)
			# CHOSES THE +/- X OR +/- Y WHICH CREATES THE NEW SHORTEST DISTANCE
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
		'''launches the missiles in an angled diagonal line'''
		# to prevent divide by 0 errors when calculating slope:
		if STRIKE_X == START_X:
			STRIKE_X += 1
		elif STRIKE_Y == STRIKE_Y:
			STRIKE_Y += 1
		# Slope formula y2-y1 / x2-x1
		slope = (STRIKE_Y - START_Y) / (STRIKE_X - START_X)

		# if the horizontal distance is < 4, use the gentle algo instead
		if (abs(START_X - STRIKE_X) < 4):
			Missiles.ICBM_gentle(STRIKE_X, STRIKE_Y, START_X, START_Y)
		else:
			# if the destination is to the right of the start/launch site
			if STRIKE_X > START_X:
				# xy of prev character for omitting the missile paths
				prev_xy = []
				for x in range(START_X, STRIKE_X):
					# stores original x,y and the character originally on the map at that x,y
					prev_xy = [x, START_Y]
					prev_char = Draw.get_original_character(prev_xy[0], round(prev_xy[1]))
					# print the missile location
					Draw.draw_char(x, START_Y, ICON, COLOUR=COL)
					START_Y += slope
					time.sleep(REFRESH_RATE)
					# draw the previous character to clear the missile path
					Draw.draw_char(prev_xy[0], prev_xy[1], prev_char, COLOUR='YELLOW')
			# if the destination is to the left
			elif STRIKE_X < START_X:
				prev_xy = []
				for x in range(START_X-STRIKE_X):
					# stores original x,y and the character originally on the map at that x,y
					prev_xy = [START_X-x, START_Y]
					prev_char = Draw.get_original_character(prev_xy[0], round(prev_xy[1]))
					# draw the new missile location
					Draw.draw_char(START_X-x, START_Y, ICON, COLOUR=COL)
					START_Y -= slope
					time.sleep(REFRESH_RATE)
					# draw the previous character to clear the missile path
					Draw.draw_char(prev_xy[0], prev_xy[1], prev_char, COLOUR='YELLOW')
			
		Draw.draw_char(STRIKE_X, STRIKE_Y-1, '🌞')

	def ICBM_bresenham(start: tuple, strike: tuple, chemtrail=True, speed=0.4):
		'''
		Launch a missile from start to strike using the Bresenham algorithm.
		returns a list of tuples representing the coords which were detonated. 
		'''
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
	'''Methods and attributes for the map'''

	def print_map(COLOUR: str, SPEED: float, ocean=False):
		# clear entire terminal 
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
		with open('WATER_COORDS.txt', 'r') as f:
			xy_ocean_coords = ast.literal_eval(f.read())
			
		for xy in xy_ocean_coords:
			Draw.draw_char(xy[0], xy[1], SYMBOL, COLOUR=OCEAN_COLOUR)

	def get_ocean_tiles() -> list:
		'''returns a list of coordinates of ocean tiles'''
		with open('WATER_COORDS.txt', 'r') as f:
			xy_ocean_coords = ast.literal_eval(f.read())
		return xy_ocean_coords

	def check_for_ocean(x, y) -> bool:
		'''checks if a tile is ocean'''
		ocean_tiles = Map.get_ocean_tiles()
		if x < 2: # prevents drawing on the numbers
			return False
		if (x, y) in ocean_tiles:
			return True
		else:
			return False

	def check_for_obstruction(list_of_coords: list) -> bool:
		'''checks if a list of coordinates is entirely ocean'''
		for xy in list_of_coords:
			if not Map.check_for_ocean(xy[0], xy[1]):
				return False
		return True

	def convert_x_coord(x: str) -> int:
		'''Converts a grid coordinate (X, 3) to a screen coordinate (100, 3)'''
		alpha = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]
		x_values = [6, 12, 18, 24, 30, 36, 42, 48, 54, 60, 66, 72, 78, 84, 90, 96, 102, 108, 114, 120, 126, 132, 138, 144, 150]
		x_values_dict = dict(zip(alpha, x_values))
		return x_values_dict[x.upper()]-2 # minus 2 due to an error offset with x_values (A is actually 4, etc) too lazy to fix rn

	def get_coordinates_inside_circle(circle_center: tuple, circle_coords: list) -> list:
		'''
		circle = a list of coordinates of the circle's circumference
		Returns all the coordinates that are within a circle drawn.
		'''
		coords_in_circle = []
		for x, y in circle_coords:
			line = Draw.get_line((circle_center[0], circle_center[1]), (x, y))
			for x, y in line:
				if (x, y) not in coords_in_circle:
					coords_in_circle.append((x, y))
		
		return coords_in_circle

	def print_subs(player="", enemies=[], allies=[], REVEALED_ENEMIES=[]):
		'''Draws the enemy subs, takes in a list of enemies, a list of allies, and the player's countries name (string)'''
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
		'''
		SHOW_ENEMY_SUBS = []: List of enemy sub (tuples) to reveal to player, default is none
		'''
		Map.print_map(COLOUR='YELLOW', SPEED=REFRESH_RATE)
		Map.print_ocean()
		Map.print_subs(player=player, allies=allies, enemies=enemies)
		Draw.player_list(allies, enemies, player)
		Map.print_silos(player=player, enemies=enemies, allies=allies)
		


	# region Dev Tool

	def print_ocean_dev(MAP, TERRAIN_COLOUR="yellow", OCEAN_COLOUR="cyan"):
		'''used for printing the ocean, but requires a pre-defined map which already displays the ocean'''

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
		'''Tool for mapping the ocean onto the map'''
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
		
		
		# original sample code for finding oceans manually – superseded by flood_fill()
		while not True:
			try:
				start_y += 1 # = int(xy[1])
			except UnboundLocalError:
				Draw.clear_screen()
				Map.print_map('yellow', 0.00002)
				Draw.clear_console()  # always clear console before writing to it
				start_y =  pyinputplus.inputInt('Enter starting y coordinate: ', min=1, max=45)
			else:
				MapStatus = True # initial state, is set to false to exit loop
				while MapStatus: # main loop after initial start_y is set
					Draw.clear_screen()
					Map.print_map('yellow', 0.00002)
					draw_waters(colour="cyan", char="^")
					Draw.clear_console()  # always clear console before writing to it

					# read and draw the oceans that are already saved in the .txt file
					draw_waters(colour="cyan", char="^")

					Draw.clear_console()		
					Draw.console(f"y coordinate is: {start_y}")
					
					start_x = convert_x_coord(pyinputplus.inputStr('Enter starting x coordinate (ABC...): ')) #int(xy[0]) #
					Draw.clear_console()
					# check if the space is correct, otherwise prompt again
					bext.goto(start_x, start_y)
					Draw.draw_char(start_x, start_y, CHAR='X', COLOUR="WHITE")
					Draw.clear_console()
					if Draw.get_original_character(start_x, start_y) != ' ':
						Draw.clear_console()
						Draw.console(f"The space is not empty, please try again")
						time.sleep(SMALL_PAUSE)
						continue
					correct_positioning = str(pyinputplus.inputYesNo('Is this the correct position? ')).upper()
					if correct_positioning == "YES":
						# check if the space to the left is a water tile aka " "
						x_left = start_x - 1
						while Draw.get_original_character(x_left, start_y) == ' ':
							Draw.draw_char(x_left, start_y, CHAR='~', COLOUR="BLUE")
							x_left -= 1
							time.sleep(SMALL_PAUSE)
						left_ocean = list(range(x_left+1, start_x))
						# check if the space to the right is a water tile aka " "
						x_right = start_x + 1
						while Draw.get_original_character(x_right, start_y) == ' ' and x_right < 152:
							Draw.draw_char(x_right, start_y, CHAR='~', COLOUR="BLUE")
							x_right += 1
							time.sleep(SMALL_PAUSE)
						right_ocean = list(range(start_x, x_right)) # +1 because it is off by 1

						new_ocean_tiles_list = left_ocean + right_ocean

						# completely redraw the new ocean and check if its correct?
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

						# ask dev if they want to continue marking oceans, else quit
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
			# we need the x and y of the start position, the old value,
			# and the new value
			# the flood fill has 4 parts
			# firstly, make sure the x and y are inbounds
			if x < 0 or x >= len(matrix[0]) or y < 1 or y >= len(matrix)-1:
				return
			# secondly, check if the current position equals the old value
			if matrix[y][x] != old:
				return

			# thirdly, set the current position to the new value
			matrix[y][x] = new
			# fourthly, attempt to fill the neighboring positions
			flood_fill(matrix, x+1, y, old, new)
			flood_fill(matrix, x-1, y, old, new)
			flood_fill(matrix, x, y+1, old, new)
			flood_fill(matrix, x, y-1, old, new)
			# return the matrix
			return matrix


		ocean_map = flood_fill(WORLD_MAP_GRAPH, 110, 28, " ", "^")
		WATER_COORDS = [] 
		for y in range(len(ocean_map)):
			for x in range(len(ocean_map[y])):
				if ocean_map[y][x] == "^":
					WATER_COORDS.append((x, y))
		with open("WATER_COORDS.txt", "a") as f:
			f.write(str(WATER_COORDS))
	# endregion


# region Classic Mode Code

def classic_mode():
	bext.clear()
	Map.print_map("yellow", REFRESH_RATE)
	# create list of countries / players: 
	unassigned_countries = []

	for country in countries:
		# reset status of all countries:
		countries[country]['status'] = True
		unassigned_countries.append(country)

	all_countries = unassigned_countries.copy()

	# ask player which country they want to be
	bext.goto(0, 48)
	player_country = pyinputplus.inputMenu(
		unassigned_countries, "CHOOSE A COUNTRY:\n", numbered=True)

	unassigned_countries.remove(player_country)

	allies = []
	enemies = []

	# set limit of allies: 
	ally_limit = randint(2,5)
	# set number of enemies
	enemies_limit = len(all_countries) - ally_limit

	# randomly assisgn allies and enemies
	for country in unassigned_countries:
		if len(allies) < ally_limit:
			allies.append(country)
		else:
			enemies.append(country)

	# make a copy the original allies and enemies
	# so that it can be used in the Draw.playerlist function
	original_allies = allies.copy()
	original_enemies = enemies.copy()

	# display the box of enemies and allies
	Draw.player_list(allies, enemies, player_country)

	# draw ally bases 
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
		'''Ask the player what countries it should target'''
		
		Draw.clear_console()  # clear bottom text area

		# if there is more than 1 enemy, ask the user which country to target
		if len(enemies) > 1:
			target = pyinputplus.inputMenu(enemies, "CHOSE A COUNTRY TO TARGET:\n", lettered=True)
		else: # otherwise automatically fire at the last enemy
			target = enemies[0]			

		start_x = countries[player_country]['location'][0]
		start_y = countries[player_country]['location'][1]
		strike_x = countries[target]['location'][0]
		strike_y = countries[target]['location'][1]

		Missiles.ICBM_diag(start_x, start_y, strike_x, strike_y, REFRESH_RATE=0.05, COL='YELLOW', ICON='>')
		Draw.draw_fallout(strike_x, strike_y, RADIUS=1)

		# remove country from list of targettable enemies
		enemies.remove(target)
		# change countries status to false
		countries[target]['status'] = False

	def automove():
		'''Randomly selects a country to fire at one of its enemies.'''
		remaining_countries = enemies + allies 
		# randomly assign which country is firing
		start = choice(remaining_countries)
		# ensure country doesn't fire at itself
		remaining_countries.remove(start)
		# set possible targets to a state's enemies only
		if start in enemies:
			possible_targets = allies
			possible_targets.append(player_country)
		elif start in allies:
			possible_targets = enemies
		target = choice(possible_targets)

		# start (x,y) for missile base location
		start_x = countries[start]['location'][0]
		start_y = countries[start]['location'][1]
		# strike (x,y) for missile's target location
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
		'''PRINTS A MESSAGE AT A SPECIFIC COUNRTY'S SILO LOCATION
		Mainly used for printing 'You lose' at game end'''
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


# endregion


class SubsAndSilos():

	def audio(type:str):
		if type == "sub_launch":
			playsound("sounds/sfx_exp_medium7.wav")


	def display_map():
		'''Display the map of the game'''
		bext.clear()
		Map.print_map("yellow", SPEED=REFRESH_RATE, ocean=True)
		Draw.clear_console()
		
	def ask_for_ocean_coords():
		'''Ask the user for the coordinates of the ocean'''
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
		'''
		Performs a sonar around the submarine, displaying a blue circle around the submarine like a sonar
		returns a list of x,y coords that were made visible
		'''
		player_sub = countries[player_country]['subs'][0] # the x, y coordinates of the player's sub
		# draw a blue circle around the player's sub, indicating possible detect locations (10 tile radius)
		sonar = Draw.draw_circle(player_sub[0], player_sub[1], RADIUS=radius, COLOUR="BLUE") # returns a list of the tiles that are in the radius of the sub
		visible_coords = [] # used to store the x,y of the lines that were drawn during the sonar so we can return what was visible to the submarine
		for xy in sonar:
			# draw a blue line between the sub and the sonar
			# if the radius * 1.2 is less than the distance between the sub and the sonar, draw a normal line
			if Missiles.get_distance(player_sub[0], player_sub[1], xy[0], xy[1]) < (radius * 1.2):
				coords = Draw.draw_line(player_sub[0], player_sub[1], xy[0], xy[1], COLOUR="BLUE")
				time.sleep(0.0002)
				visible_coords.extend(coords) 
			else:
				# otherwise it must have wrapped around the map, so draw a line starting at the otherside of the map, but only if x < 154 and y < 45
				
				if player_sub[0] < (152 / 2): # handles when the sub is on the left edge of the map:
					subx, suby = player_sub[0] + 154, player_sub[1] # if the sub is on the left side, then we add 154 to the x coord in order to wrap it around
					visible_coords.extend( Draw.draw_line(subx - 154, suby, 1, xy[1], COLOUR="BLUE")) # this one draws the line from the submarine's original location (since we still need a line there too)
					visible_coords.extend( Draw.draw_line(subx, suby, xy[0], xy[1], COLOUR="BLUE")) # this one is for drawing the line at the other side of the map
				else: # handles when the sub is on the left edge of the map:
					subx, suby = player_sub[0] - 154, player_sub[1] # if the sub is on the right side, then we need to subtract 154 
					visible_coords.extend( Draw.draw_line(player_sub[0], suby, 153, xy[1], COLOUR="BLUE")) # this one draws the line from the submarine's original location (since we still need a line there too)
					visible_coords.extend( Draw.draw_line(subx, suby, xy[0], xy[1], COLOUR="BLUE")) # this one is for drawing the line at the other side of the map

				time.sleep(0.006)
		return Utility.remove_duplicates(visible_coords) # remove duplicate x,y tuples

	def action_attack(player_country):
		# draw a red circle around the player's sub, indicating possible attack locations (10 tile radius)
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
		SubsAndSilos.audio("sub_launch")
		return Missiles.ICBM_bresenham(countries[player_country]['subs'][0], target_coords)
				
	def action_move(subxy: tuple, direction: str, distance: int):
		'''
		Moves the submarine in the specified direction
		returns the new x,y coordinates of the submarine if they are valid (ie in the ocean)
		otherwise returns the False
		'''
		# validate that it is an ocean tile
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
		
		# create list of countries / players: 
		unassigned_countries = []

		for country in countries:
			# reset status of all countries:
			countries[country]['status'] = True
			unassigned_countries.append(country)

		all_countries = unassigned_countries.copy()

		# ask player which country they want to be
		bext.goto(0, 48)
		player_country = pyinputplus.inputMenu(
			unassigned_countries, "CHOOSE A COUNTRY:\n", numbered=True)

		unassigned_countries.remove(player_country)

		allies = []
		enemies = []

		# set limit of allies: 
		ally_limit = randint(2,5)
		# set number of enemies
		enemies_limit = len(all_countries) - ally_limit

		# randomly assisgn allies and enemies
		for country in unassigned_countries:
			if len(allies) < ally_limit:
				allies.append(country)
			else:
				enemies.append(country)

		# make a copy the original allies and enemies
		# so that it can be used in the Draw.playerlist function
		original_allies = allies.copy()
		original_enemies = enemies.copy()

		# display the box of enemies and allies
		Draw.player_list(allies, enemies, player_country)

		# draw bases
		Map.print_silos(player_country, enemies, allies)
		
		# ask player for their sub's coords
		Draw.clear_console()
		player_sub_x, player_sub_y = SubsAndSilos.ask_for_ocean_coords()
		countries[player_country]['subs'].append((player_sub_x, player_sub_y))
		
		# randomly generate sub coordinates for other players by choosing a random ocean tile
		ocean_coords = Map.get_ocean_tiles()
		for country_name, country_data in countries.items():
			if country_name in enemies or country_name in allies and not country_name == player_country:
				country_data['subs'].append(choice(ocean_coords))
		
		Map.print_subs(player_country, allies=allies) # draw subs minus enemies

		return player_country, enemies, allies, original_allies, original_enemies
			

	def player_move(player_country, enemies, allies, original_allies, original_enemies):
		'''Player's turn'''
		Map.print_all_layers(player_country, enemies, allies, Found_Enemy_Subs=enemies)
		Draw.clear_console()
		action = pyinputplus.inputMenu(["Move", "Attack", "Detect", "End Turn"], "What would you like to do?\n", lettered=True)
		Draw.clear_console()
		player_sub_x, player_sub_y = countries[player_country]['subs'][0]
		if action == "Move":
			distance_max = 10
			# draw a green circle around the player's sub, indicating possible move locations (4 tile radius)
			Draw.draw_circle(player_sub_x, player_sub_y, RADIUS=distance_max, COLOUR="GREEN")
			# ask player to move N, S, E, W
			Draw.clear_console()
			move_direction = pyinputplus.inputMenu(["N", "S", "E", "W"], "What direction would you like to move?\n", lettered=True)
			move_distance = pyinputplus.inputInt("How many tiles would you like to move?\n", min=1, max=distance_max-1)
			# move the sub
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
		'''Enemy's turn'''
		Map.print_all_layers(player_country, enemies, allies, Found_Enemy_Subs=enemies)
		Draw.clear_console()
		# for each enemy sub, randomly move 1-8 tiles
		for country in enemies:
			move_valid = False
			while not move_valid:
				move_distance = randint(5,10)
				possible_moves = Draw.draw_circle(countries[country]['subs'][0][0], countries[country]['subs'][0][1], RADIUS=move_distance, visible=False)
				new_sub_coords = choice(possible_moves)
				travel_line = Draw.get_line(countries[country]["subs"][0], new_sub_coords)
				if new_sub_coords and Map.check_for_obstruction(travel_line): # validate that it is a possible travel path
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
	'''
		This is the main function for the submarines and silos game.
		It is called when the user selects the 'Submarines and Silos' option.
		It is responsible for setting up the game, and calling the functions
		that handle the game logic.
	'''
	# display map
	SubsAndSilos.display_map()
	# set up the game
	player_country, enemies, allies, original_allies, original_enemies = SubsAndSilos.setup_game()


	# ...

	# Ask Player to Move
	while True:
		player_country, enemies, allies, original_allies, original_enemies = SubsAndSilos.player_move(player_country, enemies, allies, original_allies, original_enemies)
		SubsAndSilos.enemy_move(player_country, enemies, allies, original_allies, original_enemies)








##############################################################################################################################
# MAIN GAME LOOP
##############################################################################################################################

def main():
	if WIDTH < 170 or HEIGHT < 60:
		# Ensure enough space to print the entire map
		print(f"TERMINAL WIDTH MUST BE > 170 characters wide and > 60 characters tall\nYour terminal is only: {WIDTH}px wide by {HEIGHT}px tall")
		# sys.exit()

	while True:
		# Runs at the start of each game
		Draw.clear_console()
		submarinesandsilos()
		sys.exit()


##############################################################################################################################

if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		print('Bye!')
