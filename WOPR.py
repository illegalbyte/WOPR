#! python3

# WOPR.py 
#	> a text based game inspired by War Games 


from random import randint
import bext
import pyinputplus
import sys
import time
import math


# BEXT REQUIREMENTS, for printing to the screen
WIDTH, HEIGHT = bext.size()
#	for windows term width (prevents printing a newline when reaching the end of terminal)
WIDTH -= 1
REFRESH_RATE = 0.02


# SAVE THE WORLD MAP AS WORLD_MAP
with open('WORLD_MAP.txt', 'r') as map:
	WORLD_MAP = map.read()

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
		bext.goto(NUKE_LOCATION_X, NUKE_LOCATION_Y)
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

def launch_ICBM(STRIKE_X, STRIKE_Y, START_X=40, START_Y=17):
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


# MAIN GAME LOOP
def main():
	# Ensure enough space to print the entire map
	if WIDTH < 170 or HEIGHT < 60:
		print("TERMINAL WIDTH MUST BE > 170 characters")
		sys.exit()

	# CLear terminal 
	bext.clear()


	# PRINT THE WORLD_MAP
	print_map('GREEN', 0.00002)

	# MAIN LOOP AFTER MAP IS PRINTED

	while True:
		# STRIKE_X, STRIKE_Y = ask_for_coordinates()

		# X_DISTANCE = range(20, 60)
		# prev_character = ' '
		# for x in X_DISTANCE:
		# 	draw_char(x-1, 15, prev_character, COLOUR='GREEN')
		# 	prev_character = get_original_character(x, 15)
		# 	draw_char(x, 15, '🐲', COLOUR='PURPLE')
		# 	time.sleep(0.02)

		START_X, START_Y = (40, 14)

		for i in range(20):
			launch_ICBM(randint(1,100), randint(2,43))
		break
		




if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		print('Bye!')
