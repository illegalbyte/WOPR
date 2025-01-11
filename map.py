import bext
import pyinputplus
import sys
import time
import math
import ast
from draw import Draw
from missiles import Missiles
from constants import WIDTH, REFRESH_RATE, SMALL_PAUSE, COLOURS, countries, console_prompts, WORLD_MAP, WORLD_MAP_GRAPH


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

	def _find_oceans_dev():
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
					if Draw.get_original_map_character(start_x, start_y) != ' ':
						Draw.clear_console()
						Draw.console(f"The space is not empty, please try again")
						time.sleep(0.5)
						continue
					correct_positioning = str(pyinputplus.inputYesNo('Is this the correct position? ')).upper()
					if correct_positioning == "YES":
						x_left = start_x - 1
						while Draw.get_original_map_character(x_left, start_y) == ' ':
							Draw.draw_char(x_left, start_y, CHAR='~', COLOUR="BLUE")
							x_left -= 1
							time.sleep(SMALL_PAUSE)
						left_ocean = list(range(x_left+1, start_x))
						x_right = start_x + 1
						while Draw.get_original_map_character(x_right, start_y) == ' ' and x_right < 152:
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
