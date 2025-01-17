#! python3

# WOPR.py 
#	> a text based game inspired by War Games 

from random import randint, choice
import bext
import pyinputplus
import sys
import archived_files.a_star as a_star

# BEXT REQUIREMENTS, for printing to the screen
WIDTH, HEIGHT = bext.size()
#	for Windows (OS) term width (prevents printing a newline when reaching the end of terminal)
WIDTH -= 1
# the speed of animations per second
REFRESH_RATE = 0.002
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

# READ THE WORLD MAP AND STORE IN CONSTANT: WORLD_MAP
from pprint import pprint as pp
with open('WORLD_MAP.txt', 'r') as map:
	WORLD_MAP = map.read()

# write to file
def logfile(text, file):
	with open(file, 'a') as f:
		f.write(f'\n{text}')

# prints the map
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

class Draw():
	def __init__(self) -> None:
		pass

	# DRAWS A CHARACTER AT A SPECIFIC LOCATION
	@staticmethod
	def draw_char(X, Y, CHAR: str, COLOUR='RED'):
			bext.goto(round(X), round(Y))
			bext.fg(COLOUR)
			print(f'{CHAR}', end='')
			sys.stdout.flush()

	@staticmethod
	def draw_targets(regions: dict):
		for region in regions.values():
			for country, target in region.items():
				x, y = target
				Draw.draw_char(x, y, r'{X}', COLOUR='WHITE')

	# DRAWS RADIATION MARKER
	def draw_fallout(STRIKE_X, STRIKE_Y, RADIUS=1, SPEED=0.003):
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
					Draw.draw_char(x, y, 'X', COLOUR='PURPLE')
					time.sleep(SPEED)
					theta += step
				RADIUS -=1				

	# prints dialogue at the bottom which asks for coordinates and returns a tuple of the (x, y)
	def ask_for_coordinates():
		bext.goto(0, 50)
		bext.fg('RED')
		X_COORD = pyinputplus.inputInt('ENTER X LOCTAION FOR FIRST STRIKE > ', min=0, max=154)
		bext.goto(0, 52)
		Y_COORD = pyinputplus.inputInt('ENTER Y LOCTAION FOR FIRST STRIKE > ', min=0, max=45)
		Draw.clear_lines(50, 56)
		return (X_COORD, Y_COORD)

	# write to the bottom console
	def console(input):
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

	def clear_to_edge(y_start, y_end, x_start):
		'''Clears lines from x to the end of the screen (ie the right edge)'''
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

class Missiles():
	'''A bunch of functions related to firing and drawing missiles'''
	def __init__(self) -> None:
		pass

	# Calculates the distance between two (x,y) coordinates
	def get_distance(x1, y1, x2 ,y2):
		return math.hypot(x2-x1, y2-y1)

	# this path algo launches a missile in a line and then when it is at a ~40° angle it will move diagonally towards target
	def ICBM_gentle(STRIKE_X, STRIKE_Y, START_X=40, START_Y=17, ICON='X', COLOUR='PURPLE'):
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

	# this path algo is incomplete
	def ICBM_miko():
			START_X, START_Y = (0, 0)
			STRIKE_X, STRIKE_Y = (80, 23)

			y_height = abs(STRIKE_X - START_X)
			x_height = abs(STRIKE_Y - START_Y)

			if y_height > x_height:
				x_delta = x_height / y_height
				y_delta = 1
				for i in range(y_height):
					Draw.draw_char(START_X+x_delta, START_Y+y_delta, '🌞', 'PURPLE')
					time.sleep(0.2)
					START_X += x_delta
					START_Y += y_delta
			elif x_height > y_height:
				x_delta = 1
				y_delta = y_height / x_height
				for i in range(x_height):
					Draw.draw_char(START_X+x_delta, START_Y+y_delta, '🌞', 'PURPLE')
					time.sleep(0.2)
					START_X += x_delta
					START_Y += y_delta

	# uses a shortest path breadth algorithm – should be used for obstacle avoidance 
	# TODO: requires the map characters are in a 2D list format, not a string 
	def ICBM_shortestPath(START_X, START_Y, STRIKE_X, STRIKE_Y):
		shortest_path = a_star.getShortestPath(
			WORLD_MAP_GRAPH, [START_X, START_Y], [STRIKE_X, STRIKE_Y])
		for coordinate in shortest_path:
			x, y = coordinate
			Draw.draw_char(x, y, 'X', COLOUR='PURPLE')
			time.sleep(0.02)

	# launches the missiles in an angled diagonal line
	# TODO: add a wind effect to randomise missile paths
	def ICBM_diag(START_X, START_Y, STRIKE_X, STRIKE_Y, COL='PURPLE', ICON='🌞', REFRESH_RATE=REFRESH_RATE):
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
					Draw.draw_char(prev_xy[0], prev_xy[1], prev_char, COLOUR='GREEN')
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
					Draw.draw_char(prev_xy[0], prev_xy[1], prev_char, COLOUR='GREEN')
			

		Draw.draw_char(STRIKE_X, STRIKE_Y-1, '🌞')

	def simultanious_launch(number_of_launches):
		launch_coords = [] # list of tuples (x, y)
		while number_of_launches > 0: 
			launch_coords.append(Draw.ask_for_coordinates())
			number_of_launches -= 1
		
		return launch_coords


	# TODO: get this to fix diag algo so it properly prints vertical firing paths (ie iterates over distance, not the difference of the x coordinates)
	def launch_ICBM_diag2(START_X, START_Y, STRIKE_X, STRIKE_Y, COL='PURPLE', ICON='🌞'):
		# to prevent divide by 0 errors when calculating slope:
		if STRIKE_X == START_X:
			STRIKE_X += 1
		elif STRIKE_Y == STRIKE_Y:
			STRIKE_Y += 1
		# Slope formula y2-y1 / x2-x1
		slope = (STRIKE_Y - START_Y) / (STRIKE_X - START_X)
		# this is the range we need to iterate over when drawing the animation
		distance = round(Missiles.get_distance(START_X, START_Y, STRIKE_X, STRIKE_Y))
		# if the destination is to the right of the start/launch site
		if STRIKE_X > START_X:
			# iterate over the distance that has to be travelled
			for x in range(distance+START_X, distance+STRIKE_X):
				Draw.draw_char(x, START_Y, ICON, COLOUR=COL)
				START_Y += slope
				time.sleep(REFRESH_RATE)
		# if the destination is to the left
		elif STRIKE_X < START_X:
		
			for x in range(distance+STRIKE_X, distance+START_X):
				Draw.draw_char(START_X-x, START_Y, ICON, COLOUR=COL)
				START_Y -= slope
				time.sleep(REFRESH_RATE)

class Weapons:
	def __init__(self, xy: tuple, missiles: int, status: bool, country: str, base_icon='@'):
		self.xy = xy
		self.missiles = missiles
		self.status = status
		self.country = country
		self.base_icon = base_icon

	def draw_base(self):
		x, y = self.xy
		if self.status == True:
			color = 'WHITE'
		else:
			color = 'RED'
		Draw.draw_char(x, y, self.base_icon, COLOUR=color)

class Silo(Weapons):
	pass

class Submarine(Silo):
	def move(self, x2, y2):
		# move the submarine
		# check that the next path is empty
		if Draw.get_original_character(x2, y2) != ' ' \
		or Draw.get_original_character(x2-1, y2-1) != ' ' \
		or Draw.get_original_character(x2+1, y2+1) != ' ' \
		or Draw.get_original_character(x2-1, y2+2) != ' ' \
		or Draw.get_original_character(x2+1, y2-2) != ' ': 
			Draw.console(f'SUBMARINE COLISION AT X: {x2} Y: {y2}')
		else:
			# clear current position (draw the original map tile)
			Draw.draw_char(self.xy[0], self.xy[1], CHAR=Draw.get_original_character(self.xy[0],self.xy[1]))
			# move the submarine
			self.xy = (x2, y2)
			# draw at new position:
			self.draw_base()
			return self.xy

class Defcon():
	

	defcon = [0,1,2,3,4,5]
	
	defcon_status = defcon[5]

	def display(defcon_status):
		box =["#################", \
			  "#               #", \
			  "#               #", \
			  "#               #", \
			  "#               #", \
			  "#               #", \
			  "#################"]
		# draw each line of the box
		for y, line in enumerate(box):
			Draw.draw_char(170, y+2, line, COLOUR='YELLOW')

			if defcon_status == 5:
				Draw.draw_char(175, 7, f'DEFCON {Defcon.defcon_status}')
			elif defcon_status == 4:
				Draw.draw_char(175, 6, f'DEFCON {Defcon.defcon_status}')
			elif defcon_status == 3:
				Draw.draw_char(175, 5, f'DEFCON {Defcon.defcon_status}')
			elif defcon_status == 2:
				Draw.draw_char(175, 4, f'DEFCON {Defcon.defcon_status}')
			elif defcon_status == 1:
				Draw.draw_char(175, 3, f'DEFCON {Defcon.defcon_status}')


def game(scenario='autofire'):
	'''The main game functions, takes one parameter scenario, which determines
	what game will be played'''
	if scenario == 'autofire':
		# resets the console prompt buffer to be empty
		global console_prompts
		console_prompts = []

		# draw silos on top of map
		Draw.draw_targets(regions)

		# add targets to a list
		targets = []
		for region in regions.values():
			for country, target in region.items():
				targets.append(target)
		
		# set initial defcon to 5
		Defcon.defcon_status = 5
		# LOOP: until all targets are eliminated
		while len(targets) != 0:

			# print the defcon status before the shot
			Defcon.display(Defcon.defcon_status)

			# the counrty which launches an icbm
			start = choice(targets)
			# removes the launch country from the list of potential targets
			targets.remove(start)
			# randomly choses the target country
			strike = targets.pop(randint(0, len(targets)-1))
			# add the start country as a potential target again
			targets.append(start)

			x1, y1 = start
			x2, y2 = strike

			Missiles.ICBM_diag(x1, y1, x2, y2, ICON='@', REFRESH_RATE=0.09)
			Draw.draw_fallout(x2, y2, 2, SPEED=0.0009)

			if Defcon.defcon_status != 1:
					Defcon.defcon_status -= 1
			Defcon.display(Defcon.defcon_status)

			# print remaining countries by name:
			remaining_countries = []
			for region in regions.values():
				for country, target in region.items():
					if target in targets:
						remaining_countries.append(country)
			Draw.console(f"REMAINING COUNTRIES >> {' '.join(remaining_countries)}")

			time.sleep(1)
			if len(targets) == 1:
				Draw.console(f' > WINNER: {remaining_countries[0]}')
				time.sleep(3)
				break

			# sample code which explains how to query the regions dict for a target
			# for region in regions.values():
			# 	for country, target in region.items():
			# 		(f'{country} >> {target}')

	if scenario == 'interactive':
		while True:
			# CLear terminal
			bext.clear()
			# PRINT THE WORLD_MAP
			print_map('GREEN', 0.000002)

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
				# clear bottom text area
				Draw.clear_lines(48, HEIGHT)
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


				




washington = Silo((31,13), 10, True, country='USA')
berlin = Silo((94,9), 10, True, country='Germany')
arch1 = Submarine((100,37), missiles=2, status=True, country='USA', base_icon='🛥')





# MAIN GAME LOOP
def main():
	# Ensure enough space to print the entire map
	if WIDTH < 170 or HEIGHT < 60:
		print(f"TERMINAL WIDTH MUST BE > 170 characters wide and > 60 characters tall\nYour terminal is only: {WIDTH}px wide by {HEIGHT}px tall")
		sys.exit()

	# MAIN LOOP AFTER MAP IS PRINTED
	while True:
		
		game(scenario='interactive')


if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		print('Bye!')
