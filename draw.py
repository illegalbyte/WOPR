import bext
import pyinputplus
import sys
import time
import math
from constants import *
from map import Map
from renderer import Renderer

class Draw(Renderer):
	"""
	A class for rendering visual elements in a game map, including targets, fallout effects, circles, lines, and bases.
	Methods:
		draw_targets: Places X marks on target locations aka silos
		draw_fallout_old: Creates an expanding radiation circle effect (legacy method)
		draw_fallout: Draws fallout around a target location 
		draw_circle: Creates a hollow circle at specified coordinates
		get_line: Calculates points for drawing a line between two coordinates
		draw_line: Renders a line between two points
		player_list: Displays lists of allies and enemies
		clear_lines: Erases content from specified line range
		clear_console: Clears the console area
		clear_screen: Erases entire screen
		clear_to_edge: Clears content from x position to screen edge
		get_original_map_character: Retrieves original character from map at position
		ocean: Draws ocean effect between points
		draw_bases: Places base markers on map
		_get_base_colour: Determines color for base markers
		base_message: Shows temporary message at a base location
	"""
 
	def __init__(self):
		super().__init__()

	def draw_targets(self, regions: dict):
		"""
		Draw targets for each region.

		Args:
			regions (dict): Dictionary containing regions and their targets.
		"""
		for region in regions.values():
			for country, target in region.items():
				x, y = target
				self.draw_char(x, y, r'{X}', COLOUR='WHITE')
	
	def draw_fallout_old(self, STRIKE_X, STRIKE_Y, RADIUS=2, SPEED=0.03, COLOUR="PURPLE", CHAR="X"):
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
				self.draw_char(x, y, CHAR, COLOUR=COLOUR)
				time.sleep(SPEED)
				theta += step
			RADIUS -=1


	def draw_fallout(self, target: tuple, RADIUS=2, SPEED=0.05, COLOUR="Green", CHAR="X"):
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
			coords = self.draw_circle(target[0], target[1], circles_drawn, COLOUR="PURPLE", erase_map_tiles=True, radius_modifier=1)
			for x, y in coords:
				self.draw_char(x, y, CHAR, COLOUR=COLOUR)
				time.sleep(SPEED)
			fallout_coords.extend(coords)
			circles_drawn += 1

		return fallout_coords

	def draw_circle(self, X, Y, RADIUS, COLOUR='RED', CHAR="X", erase_map_tiles=False, radius_modifier=2, visible=True) -> list:
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
			if self.get_original_map_character(x, y) == ' ':
				if visible:
					self.draw_char(x, y, CHAR, COLOUR=COLOUR)
				if (round(x), round(y)) not in circle:
					circle.append((round(x), round(y)))	
			elif erase_map_tiles:
				if visible:
					self.draw_char(x, y, CHAR, COLOUR=COLOUR)
				if (round(x), round(y)) not in circle:
					circle.append((round(x), round(y)))	
			theta += step

		return circle

	def get_line(self, start: tuple, end: tuple) -> list:
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

	def draw_line(self, x1, y1, x2, y2, COLOUR='RED', ocean_only=True) -> list:
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
		points = self.get_line((round(x1), round(y1)), (round(x2), round(y2)))
		valid_points = []
		for point in points:
			x, y = point
			if x > 152:
				continue
			if ocean_only and not Map.check_for_ocean(x,y):
				continue
			self.draw_char(x, y, 'X', COLOUR=COLOUR)
			valid_points.append((x,y))
		return valid_points



	def player_list(self, allies:list, enemies:list, player:str):
		"""
		Show a list of enemies and allies, as well as the player's country.

		Args:
			allies (list): List of allies.
			enemies (list): List of enemies.
			player (str): The player's country.
		"""
		self.clear_to_edge(2, 30, 180)

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

	def clear_lines(self, Y_START, Y_END):
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

	def clear_console(self):
		"""
		Clear the console.
		"""
		self.clear_lines(48, HEIGHT)
		bext.fg('reset')
		bext.bg('reset')
		bext.goto(0, 48)
	
	def clear_screen(self):
		"""
		Clear the entire screen.
		"""
		self.clear_to_edge(0, bext.height(), 0)

	def clear_to_edge(self, y_start, y_end, x_start):
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

	def get_original_map_character(self, x,y):
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

	def ocean(self, x1, x2, y):
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


	def draw_bases(self, countries: dict, player_country: str, enemies: list, allies: list):
		"""Draw bases on the map with appropriate colors"""
		for country in countries:
			x, y = countries[country]['location']
			colour = self._get_base_colour(country, countries[country]['status'], 
										 player_country, enemies, allies)
			self.draw_char(x, y, '@', COLOUR=colour)
			
	def _get_base_colour(self, country: str, status: bool, 
						player_country: str, enemies: list, allies: list) -> str:
		"""Determine color for a base based on its status"""
		if not status:
			return 'BLUE'
		elif country == player_country:
			return 'YELLOW'
		elif country in enemies:
			return 'RED'
		elif country in allies:
			return 'WHITE'
		return 'RESET'


	def base_message(self, text: str, country: str):
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
