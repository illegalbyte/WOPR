import os
from random import randint, choice
from typing import Collection
import bext
import pyinputplus
import sys
import time
import math
import a_star
import game



# BEXT REQUIREMENTS, for printing to the screen
WIDTH, HEIGHT = bext.size()
#	for Windows (OS) term width (prevents printing a newline when reaching the end of terminal)
WIDTH -= 1
# the speed of animations per second
REFRESH_RATE = 0.0002
# colours which can be used by BEXT
COLOURS = ['red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white']
# silo locations, organised by regions
countries = {
		'GERMANY': { 
			'location': (91, 10), 
			'status': True,
			'region': 'EUROPE'
			},
		'FRANCE': { 
			'location': (81, 12),
			'status': True,
			'region': 'EUROPE'
			},
		'RUSSIA': { 
			'location': (99, 9),
			'status': True,
			'region': 'EUROPE'
			},
		'COLOMBIA': { 
			'location': (49, 23),
			'status': True,
			'region': 'AMERICAS'
			},
		'USA': { 
			'location': (34, 14),
			'status': True,
			'region': 'AMERICAS'
			},
		'CHINA': { 
			'location': (121, 15),
			'status': True,
			'region': 'ASIA'
			},
		'INDIA': {
			'location': (110, 20),
			'status': True,
			'region': 'ASIA'
			},
		'PAKISTAN': {
			'location': (107, 17),
			'status': True,
			'region': 'ASIA'
		},
		'AUSTRALIA': {
			'location': (132, 30),
			'status': True,
			'region': 'PACIFIC'
			}
}
# console prompts list (stores the prompts for the game)
console_prompts = []
# Read world map from map .txt file 
with open('WORLD_MAP.txt', 'r') as map:
	WORLD_MAP = map.read()
WORLD_MAP_GRAPH = WORLD_MAP.splitlines()


class draw():

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
				draw.draw_char(x, y, r'{X}', COLOUR='WHITE')
	
	def draw_fallout(STRIKE_X, STRIKE_Y, RADIUS=2, SPEED=0.03):
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
				draw.draw_char(x, y, 'X', COLOUR='PURPLE')
				time.sleep(SPEED)
				theta += step
			RADIUS -=1				
	
	def ask_for_coordinates():
		'''prints dialogue at the bottom which asks for coordinates and returns a tuple of the (x, y)'''
		bext.goto(0, 50)
		bext.fg('RED')
		X_COORD = pyinputplus.inputInt('ENTER X LOCTAION FOR FIRST STRIKE > ', min=0, max=154)
		bext.goto(0, 52)
		Y_COORD = pyinputplus.inputInt('ENTER Y LOCTAION FOR FIRST STRIKE > ', min=0, max=45)
		draw.clear_lines(50, 56)
		return (X_COORD, Y_COORD)

	# write to the bottom console
	def console(input):
		bext.fg('RED')
		# ensures console the prompts don't print past the height of terminal
		if len(console_prompts) > 9:
			console_prompts.pop(0)
		console_prompts.append(input)
		# for each 
		draw.clear_lines(50, 60)
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
		draw.clear_to_edge(2, 30, 180)

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
		characters = list(map_lines[y])
		return characters[x]

class missiles():
	'''A bunch of functions related to firing and drawing missiles'''

	
	def get_distance(x1: int, y1: int, x2: int , y2: int) -> int:
		'''Returns the distance between two x,y coordinates'''
		return math.hypot(x2-x1, y2-y1)
	
	def ICBM_gentle(STRIKE_X, STRIKE_Y, START_X=40, START_Y=17, ICON='X', COLOUR='PURPLE'):
		'''this path algo launches a missile in a line and then when it is at a ~40° angle it will move diagonally towards target'''
		while (START_X, START_Y) != (STRIKE_X, STRIKE_Y):

			draw.draw_char(START_X, START_Y, ICON, COLOUR=COLOUR)

			START_X += randint(0,1)

			# CALCULATES WHETHER A REDUCTION OR ADDITION TO X OR Y WILL CREATE THE NEW SHORTEST DISTANCE
			NEW_SHORTEST_DIST = missiles.get_distance(START_X, START_Y + 1, STRIKE_X, STRIKE_Y)
			if missiles.get_distance(START_X - 1, START_Y, STRIKE_X, STRIKE_Y) < NEW_SHORTEST_DIST:
				NEW_SHORTEST_DIST = missiles.get_distance(START_X - 1, START_Y, STRIKE_X, STRIKE_Y)
			if missiles.get_distance(START_X + 1, START_Y, STRIKE_X, STRIKE_Y) < NEW_SHORTEST_DIST:
				NEW_SHORTEST_DIST = missiles.get_distance(START_X + 1, START_Y, STRIKE_X, STRIKE_Y)
			if missiles.get_distance(START_X, START_Y - 1, STRIKE_X, STRIKE_Y) < NEW_SHORTEST_DIST:
				NEW_SHORTEST_DIST = missiles.get_distance(START_X, START_Y - 1, STRIKE_X, STRIKE_Y)
			# CHOSES THE +/- X OR +/- Y WHICH CREATES THE NEW SHORTEST DISTANCE
			if missiles.get_distance(START_X, START_Y + 1, STRIKE_X, STRIKE_Y) == NEW_SHORTEST_DIST:
				START_Y += 1
			elif missiles.get_distance(START_X - 1, START_Y, STRIKE_X, STRIKE_Y) == NEW_SHORTEST_DIST:
				START_X -= 1
			elif missiles.get_distance(START_X + 1, START_Y, STRIKE_X, STRIKE_Y) == NEW_SHORTEST_DIST:
				START_X += 1
			elif missiles.get_distance(START_X, START_Y - 1, STRIKE_X, STRIKE_Y) == NEW_SHORTEST_DIST:
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
			missiles.ICBM_gentle(STRIKE_X, STRIKE_Y, START_X, START_Y)
		else:
			# if the destination is to the right of the start/launch site
			if STRIKE_X > START_X:
				# xy of prev character for omitting the missile paths
				prev_xy = []
				for x in range(START_X, STRIKE_X):
					# stores original x,y and the character originally on the map at that x,y
					prev_xy = [x, START_Y]
					prev_char = draw.get_original_character(prev_xy[0], round(prev_xy[1]))
					# print the missile location
					draw.draw_char(x, START_Y, ICON, COLOUR=COL)
					START_Y += slope
					time.sleep(REFRESH_RATE)
					# draw the previous character to clear the missile path
					draw.draw_char(prev_xy[0], prev_xy[1], prev_char, COLOUR='YELLOW')
			# if the destination is to the left
			elif STRIKE_X < START_X:
				prev_xy = []
				for x in range(START_X-STRIKE_X):
					# stores original x,y and the character originally on the map at that x,y
					prev_xy = [START_X-x, START_Y]
					prev_char = draw.get_original_character(prev_xy[0], round(prev_xy[1]))
					# draw the new missile location
					draw.draw_char(START_X-x, START_Y, ICON, COLOUR=COL)
					START_Y -= slope
					time.sleep(REFRESH_RATE)
					# draw the previous character to clear the missile path
					draw.draw_char(prev_xy[0], prev_xy[1], prev_char, COLOUR='YELLOW')
			
		draw.draw_char(STRIKE_X, STRIKE_Y-1, '🌞')

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




def new_game():
	bext.clear()
	print_map("yellow", REFRESH_RATE)
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
	# so that it can be used in the draw.playerlist function
	original_allies = allies.copy()
	original_enemies = enemies.copy()

	# display the box of enemies and allies
	draw.player_list(allies, enemies, player_country)

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
		# clear bottom text area
		draw.clear_lines(48, HEIGHT)
		bext.goto(0, 48)

		# if there is more than 1 enemy, ask the user which country to target
		if len(enemies) > 1:
			target = pyinputplus.inputMenu(enemies, "CHOSE A COUNTRY TO TARGET:\n", lettered=True)
		else:
			target = enemies[0]			

		start_x = countries[player_country]['location'][0]
		start_y = countries[player_country]['location'][1]
		strike_x = countries[target]['location'][0]
		strike_y = countries[target]['location'][1]

		missiles.ICBM_diag(start_x, start_y, strike_x, strike_y, REFRESH_RATE=0.05, COL='YELLOW', ICON='>')
		draw.draw_fallout(strike_x, strike_y, RADIUS=1)

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

		missiles.ICBM_diag(start_x, start_y, strike_x, strike_y, REFRESH_RATE=0.05, COL='YELLOW', ICON='>')
		draw.draw_fallout(strike_x, strike_y, RADIUS=1)
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
		draw.player_list(original_allies, original_enemies, player_country)
		if turn % 2 == 0 and countries[player_country]['status'] == True:
			automove()
		else:
			playermove()
		turn += 1
		draw.player_list(original_allies, original_enemies, player_country)

	if countries[player_country]['status'] == False:
		base_message(f'YOU LOST IN {turn} TURNS, RESTARTING IN 10s', player_country)
	else:
		base_message(f'YOU WON IN {turn} TURNS, RESTARTING IN 10s', player_country)













##############################################################################################################################
# MAIN GAME LOOP
##############################################################################################################################

def main():
	if WIDTH < 170 or HEIGHT < 60:
		# Ensure enough space to print the entire map
		print(f"TERMINAL WIDTH MUST BE > 170 characters wide and > 60 characters tall\nYour terminal is only: {WIDTH}px wide by {HEIGHT}px tall")
		sys.exit()

	while True:
		# Runs at the start of each game
		new_game()


##############################################################################################################################

if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		print('Bye!')