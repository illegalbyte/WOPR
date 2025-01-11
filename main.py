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
from constants import *


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
