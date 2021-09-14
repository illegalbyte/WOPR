#! python3

# WOPR.py 
#	> a text based game inspired by War Games 


from random import randint, choice
from typing import Collection
import bext
import pyinputplus
import sys
import time
import math
import a_star


# BEXT REQUIREMENTS, for printing to the screen
WIDTH, HEIGHT = bext.size()
#	for windows term width (prevents printing a newline when reaching the end of terminal)
WIDTH -= 1
REFRESH_RATE = 0.02
COLOURS = ['red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white']


# SAVE THE WORLD MAP AS WORLD_MAP
with open('WORLD_MAP.txt', 'r') as map:
	WORLD_MAP = map.read()
WORLD_MAP_GRAPH = WORLD_MAP.splitlines()

def print_map(COLOUR: str, SPEED: float):
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

def ask_for_coordinates():
	bext.goto(0, 50)
	bext.fg('RED')
	X_COORD = pyinputplus.inputInt('ENTER X LOCTAION FOR FIRST STRIKE > ', min=0, max=154)
	bext.goto(0, 52)
	Y_COORD = pyinputplus.inputInt('ENTER Y LOCTAION FOR FIRST STRIKE > ', min=0, max=45)
	clear_lines(50, 56)
	return (X_COORD, Y_COORD)

# CLEARES A RANGE OF LINES, USED FOR TEXT ENTRY AT BOTTOM OF SCREEN 
def clear_lines(Y_START, Y_END):
	for y in range(Y_START, Y_END):
		for x in range(WIDTH):
			bext.goto(x, y)
			print(' ', end='')

# DRAWS A CHARACTER AT A SPECIFIC LOCATION, Requires X,Y coordinates, a CHAR to print
# Optional colour
def draw_char(NUKE_LOCATION_X, NUKE_LOCATION_Y, CHAR: str, COLOUR='RED'):
		bext.goto(round(NUKE_LOCATION_X), round(NUKE_LOCATION_Y))
		bext.fg(COLOUR)
		print(f'{CHAR}', end='')
		sys.stdout.flush()
		
# For re-printing the previous character and keeping the map in tact
# takes an x,y and returns the original character from the original map
# assumes that WORLD_MAP is not changed
def get_original_character(x,y):
	map_lines = WORLD_MAP.splitlines()
	characters = list(map_lines[y])
	return characters[x]

def get_distance(x1, y1, x2 ,y2):
	return math.hypot(x2-x1, y2-y1)

def launch_ICBM_gentle(STRIKE_X, STRIKE_Y, START_X=40, START_Y=17):
	while (START_X, START_Y) != (STRIKE_X, STRIKE_Y):

		draw_char(START_X, START_Y, 'X', COLOUR='PURPLE')

		# CALCULATES WHETHER A REDUCTION OR ADDITION TO X OR Y WILL CREATE THE NEW SHORTEST DISTANCE
		NEW_SHORTEST_DIST = get_distance(START_X, START_Y + 1, STRIKE_X, STRIKE_Y)
		if get_distance(START_X - 1, START_Y, STRIKE_X, STRIKE_Y) < NEW_SHORTEST_DIST:
			NEW_SHORTEST_DIST = get_distance(START_X - 1, START_Y, STRIKE_X, STRIKE_Y)
		if get_distance(START_X + 1, START_Y, STRIKE_X, STRIKE_Y) < NEW_SHORTEST_DIST:
			NEW_SHORTEST_DIST = get_distance(START_X + 1, START_Y, STRIKE_X, STRIKE_Y)
		if get_distance(START_X, START_Y - 1, STRIKE_X, STRIKE_Y) < NEW_SHORTEST_DIST:
			NEW_SHORTEST_DIST = get_distance(START_X, START_Y - 1, STRIKE_X, STRIKE_Y)
		# CHOSES THE +/- X OR +/- Y WHICH CREATES THE NEW SHORTEST DISTANCE
		if get_distance(START_X, START_Y + 1, STRIKE_X, STRIKE_Y) == NEW_SHORTEST_DIST:
			START_Y += 1
		elif get_distance(START_X - 1, START_Y, STRIKE_X, STRIKE_Y) == NEW_SHORTEST_DIST:
			START_X -= 1
		elif get_distance(START_X + 1, START_Y, STRIKE_X, STRIKE_Y) == NEW_SHORTEST_DIST:
			START_X += 1
		elif get_distance(START_X, START_Y - 1, STRIKE_X, STRIKE_Y) == NEW_SHORTEST_DIST:
			START_Y -= 1

		time.sleep(REFRESH_RATE)
	draw_char(STRIKE_X, STRIKE_Y, '🌞')

def launch_ICBM_miko():
		START_X, START_Y = (0, 0)
		STRIKE_X, STRIKE_Y = (80, 23)

		y_height = abs(STRIKE_X - START_X)
		x_height = abs(STRIKE_Y - START_Y)

		if y_height > x_height:
			x_delta = x_height / y_height
			y_delta = 1
			for i in range(y_height):
				draw_char(START_X+x_delta, START_Y+y_delta, '🌞', 'PURPLE')
				time.sleep(0.2)
				START_X += x_delta
				START_Y += y_delta
		elif x_height > y_height:
			x_delta = 1
			y_delta = y_height / x_height
			for i in range(x_height):
				draw_char(START_X+x_delta, START_Y+y_delta, '🌞', 'PURPLE')
				time.sleep(0.2)
				START_X += x_delta
				START_Y += y_delta

def launch_ICBM_shortestPath(START_X, START_Y, STRIKE_X, STRIKE_Y):
	shortest_path = a_star.getShortestPath(
		WORLD_MAP_GRAPH, [START_X, START_Y], [STRIKE_X, STRIKE_Y])
	for coordinate in shortest_path:
		x, y = coordinate
		draw_char(x, y, 'X', COLOUR='PURPLE')
		time.sleep(0.02)

def launch_ICBM_diag(START_X, START_Y, STRIKE_X, STRIKE_Y, COL='PURPLE', ICON='🌞'):
	# to prevent divide by 0 errors when calculating slope:
	if STRIKE_X == START_X:
		STRIKE_X += 1
	elif STRIKE_Y == STRIKE_Y:
		STRIKE_Y += 1
	# Slope formula y2-y1 / x2-x1
	slope = (STRIKE_Y - START_Y) / (STRIKE_X - START_X)
	# if the destination is to the right of the start/launch site
	if STRIKE_X > START_X:
		for x in range(START_X, STRIKE_X+1):
			draw_char(x, START_Y, ICON, COLOUR=COL)
			START_Y += slope
			time.sleep(REFRESH_RATE)
	# if the destination is to the left
	elif STRIKE_X < START_X:
		for x in range(START_X-STRIKE_X+1):
			draw_char(START_X-x, START_Y, ICON, COLOUR=COL)
			START_Y -= slope
			time.sleep(REFRESH_RATE)


	# TODO: dict of each country: 
		# Each country has a unique pathfinding algo
		# each country is assigned a colour
		# each contry has a payload (area of effect)
		# each country has a unique number of missiles
		# some countries have nuclear submarines
		# you can only view your own submarine and missile base locations
		# have to guess where the other countries are
		# friendly countries appear coloured in
		# implemnent a DEFCON warning system
		# the DEFCON system will affect other countries Hostility


# MAIN GAME LOOP
def main():
	# Ensure enough space to print the entire map
	if WIDTH < 170 or HEIGHT < 60:
		print("TERMINAL WIDTH MUST BE > 170 characters")
		sys.exit()

	# CLear terminal 
	bext.clear()
	# PRINT THE WORLD_MAP
	print_map('GREEN', 0.0002)

	LAUNCH_LOCATIONS = [
		(42,14),()
	]

	# MAIN LOOP AFTER MAP IS PRINTED
	while True:
		START_X, START_Y = (randint(10,150), randint(3,44))
		STRIKE_X, STRIKE_Y = (randint(10, 150), randint(3, 44))

		launch_ICBM_diag(START_X, START_Y, STRIKE_X, STRIKE_Y, COL=choice(COLOURS), ICON='X')
		print_map('GREEN', 0.000001)

		





if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		print('Bye!')
