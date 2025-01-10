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
from utility import Utility
from draw import Draw
from missiles import Missiles
from map import Map
from game import classic_mode, SubsAndSilos, submarinesandsilos, main

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


if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		print('Bye!')
