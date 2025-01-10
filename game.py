import bext
import pyinputplus
import sys
import time
import math
import ast
from draw import Draw
from missiles import Missiles
from map import Map
from utility import Utility
from random import randint, choice

# import constants from WOPR2.py
from WOPR2 import HEIGHT, WIDTH, REFRESH_RATE, SMALL_PAUSE, COLOURS, countries, console_prompts, WORLD_MAP, WORLD_MAP_GRAPH

def classic_mode():
    """
    Classic mode of the game.
    """
    bext.clear()
    Map.print_map("green", REFRESH_RATE)
    unassigned_countries = []

    for country in countries:
        countries[country]['status'] = True
        unassigned_countries.append(country)

    all_countries = unassigned_countries.copy()

    bext.goto(0, 48)
    player_country = pyinputplus.inputMenu(
        unassigned_countries, "CHOOSE A COUNTRY:\n", numbered=True)

    unassigned_countries.remove(player_country)

    allies = []
    enemies = []

    ally_limit = randint(2,5)
    enemies_limit = len(all_countries) - ally_limit

    for country in unassigned_countries:
        if len(allies) < ally_limit:
            allies.append(country)
        else:
            enemies.append(country)

    original_allies = allies.copy()
    original_enemies = enemies.copy()

    Draw.player_list(allies, enemies, player_country)

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
        """
        Ask the player what countries it should target.
        """
        Draw.clear_console()

        if len(enemies) > 1:
            target = pyinputplus.inputMenu(enemies, "CHOSE A COUNTRY TO TARGET:\n", lettered=True)
        else:
            target = enemies[0]            

        start_x = countries[player_country]['location'][0]
        start_y = countries[player_country]['location'][1]
        strike_x = countries[target]['location'][0]
        strike_y = countries[target]['location'][1]

        Missiles.ICBM_diag(start_x, start_y, strike_x, strike_y, REFRESH_RATE=0.05, COL='YELLOW', ICON='>')
        Draw.draw_fallout((strike_x, strike_y), 2, 0.05, "purple", "*")

        enemies.remove(target)
        countries[target]['status'] = False

    def automove():
        """
        Randomly selects a country to fire at one of its enemies.
        """
        remaining_countries = enemies + allies 
        start = choice(remaining_countries)
        remaining_countries.remove(start)
        if start in enemies:
            possible_targets = allies
            possible_targets.append(player_country)
        elif start in allies:
            possible_targets = enemies
        target = choice(possible_targets)

        start_x = countries[start]['location'][0]
        start_y = countries[start]['location'][1]
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


class SubsAndSilos():
    """
    Class containing functions for the Submarines and Silos game mode.
    """

    def display_map():
        """
        Display the map of the game.
        """
        bext.clear()
        Map.print_map("yellow", SPEED=REFRESH_RATE, ocean=True)
        Draw.clear_console()
        
    def ask_for_ocean_coords():
        """
        Ask the user for the coordinates of the ocean.

        Returns:
            tuple: The coordinates of the ocean.
        """
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
        """
        Perform a sonar around the submarine.

        Args:
            player_country (str): The player's country.
            enemies (list): List of enemies.
            allies (list): List of allies.
            radius (int): The radius of the sonar.

        Returns:
            list: List of coordinates that were made visible.
        """
        player_sub = countries[player_country]['subs'][0]
        sonar = Draw.draw_circle(player_sub[0], player_sub[1], RADIUS=radius, COLOUR="BLUE")
        visible_coords = []
        for xy in sonar:
            if Missiles.get_distance(player_sub[0], player_sub[1], xy[0], xy[1]) < (radius * 1.2):
                coords = Draw.draw_line(player_sub[0], player_sub[1], xy[0], xy[1], COLOUR="BLUE")
                time.sleep(0.0002)
                visible_coords.extend(coords) 
            else:
                if player_sub[0] < (152 / 2):
                    subx, suby = player_sub[0] + 154, player_sub[1]
                    visible_coords.extend( Draw.draw_line(subx - 154, suby, 1, xy[1], COLOUR="BLUE"))
                    visible_coords.extend( Draw.draw_line(subx, suby, xy[0], xy[1], COLOUR="BLUE"))
                else:
                    subx, suby = player_sub[0] - 154, player_sub[1]
                    visible_coords.extend( Draw.draw_line(player_sub[0], suby, 153, xy[1], COLOUR="BLUE"))
                    visible_coords.extend( Draw.draw_line(subx, suby, xy[0], xy[1], COLOUR="BLUE"))

                time.sleep(0.006)
        return Utility.remove_duplicates(visible_coords)

    def action_attack(player_country):
        """
        Perform an attack from the submarine.

        Args:
            player_country (str): The player's country.

        Returns:
            list: List of coordinates affected by the attack.
        """
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
        return Missiles.ICBM_bresenham(countries[player_country]['subs'][0], target_coords)
                
    def action_move(subxy: tuple, direction: str, distance: int):
        """
        Move the submarine in the specified direction.

        Args:
            subxy (tuple): The current coordinates of the submarine.
            direction (str): The direction to move.
            distance (int): The distance to move.

        Returns:
            tuple: The new coordinates of the submarine if valid, False otherwise.
        """
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
        """
        Search for submarines in the specified coordinates.

        Args:
            seeking_countries (list): List of countries to search for.
            search_coords (list): List of coordinates to search.

        Returns:
            list: List of found submarines.
        """
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
        """
        Set up the game.

        Returns:
            tuple: The player's country, list of enemies, list of allies, original list of allies, original list of enemies.
        """
        unassigned_countries = []

        for country in countries:
            countries[country]['status'] = True
            unassigned_countries.append(country)

        all_countries = unassigned_countries.copy()

        bext.goto(0, 48)
        player_country = pyinputplus.inputMenu(
            unassigned_countries, "CHOOSE A COUNTRY:\n", numbered=True)

        unassigned_countries.remove(player_country)

        allies = []
        enemies = []

        ally_limit = randint(2,5)
        enemies_limit = len(all_countries) - ally_limit

        for country in unassigned_countries:
            if len(allies) < ally_limit:
                allies.append(country)
            else:
                enemies.append(country)

        original_allies = allies.copy()
        original_enemies = enemies.copy()

        Draw.player_list(allies, enemies, player_country)

        Map.print_silos(player_country, enemies, allies)
        
        Draw.clear_console()
        player_sub_x, player_sub_y = SubsAndSilos.ask_for_ocean_coords()
        countries[player_country]['subs'].append((player_sub_x, player_sub_y))
        
        ocean_coords = Map.get_ocean_tiles()
        for country_name, country_data in countries.items():
            if country_name in enemies or country_name in allies and not country_name == player_country:
                country_data['subs'].append(choice(ocean_coords))
        
        Map.print_subs(player_country, allies=allies)

        return player_country, enemies, allies, original_allies, original_enemies
            

    def player_move(player_country, enemies, allies, original_allies, original_enemies):
        """
        Handle the player's turn.

        Args:
            player_country (str): The player's country.
            enemies (list): List of enemies.
            allies (list): List of allies.
            original_allies (list): Original list of allies.
            original_enemies (list): Original list of enemies.

        Returns:
            tuple: Updated player country, list of enemies, list of allies, original list of allies, original list of enemies.
        """
        Map.print_all_layers(player_country, enemies, allies, Found_Enemy_Subs=enemies)
        Draw.clear_console()
        action = pyinputplus.inputMenu(["Move", "Attack", "Detect", "End Turn"], "What would you like to do?\n", lettered=True)
        Draw.clear_console()
        player_sub_x, player_sub_y = countries[player_country]['subs'][0]
        if action == "Move":
            distance_max = 10
            Draw.draw_circle(player_sub_x, player_sub_y, RADIUS=distance_max, COLOUR="GREEN")
            Draw.clear_console()
            move_direction = pyinputplus.inputMenu(["N", "S", "E", "W"], "What direction would you like to move?\n", lettered=True)
            move_distance = pyinputplus.inputInt("How many tiles would you like to move?\n", min=1, max=distance_max-1)
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
        """
        Handle the enemy's turn.

        Args:
            player_country (str): The player's country.
            enemies (list): List of enemies.
            allies (list): List of allies.
            original_allies (list): Original list of allies.
            original_enemies (list): Original list of enemies.
        """
        Map.print_all_layers(player_country, enemies, allies, Found_Enemy_Subs=enemies)
        Draw.clear_console()
        for country in enemies:
            move_valid = False
            while not move_valid:
                move_distance = randint(5,10)
                possible_moves = Draw.draw_circle(countries[country]['subs'][0][0], countries[country]['subs'][0][1], RADIUS=move_distance, visible=False)
                new_sub_coords = choice(possible_moves)
                travel_line = Draw.get_line(countries[country]["subs"][0], new_sub_coords)
                if new_sub_coords and Map.check_for_obstruction(travel_line):
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
    """
    Main function for the Submarines and Silos game mode.
    """
    SubsAndSilos.display_map()
    player_country, enemies, allies, original_allies, original_enemies = SubsAndSilos.setup_game()

    while True:
        player_country, enemies, allies, original_allies, original_enemies = SubsAndSilos.player_move(player_country, enemies, allies, original_allies, original_enemies)
        SubsAndSilos.enemy_move(player_country, enemies, allies, original_allies, original_enemies)


def main():
    """
    Main game loop.
    """
    if WIDTH < 170 or HEIGHT < 60:
        print(f"TERMINAL WIDTH MUST BE > 170 characters wide and > 60 characters tall\nYour terminal is only: {WIDTH}px wide by {HEIGHT}px tall")

    while True:
        Draw.clear_console()
        classic_mode()
        sys.exit()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Bye!')
