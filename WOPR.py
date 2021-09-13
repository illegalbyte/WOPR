#! python3

# WOPR.py 
#	> a text based game inspired by War Games 


import bext
import pyinputplus

with open('WORLD_MAP.txt', 'r') as map:
	WORLD_MAP = map.read()


# MAIN GAME LOOP
def main():
	print(WORLD_MAP)


if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		print('Bye!')
