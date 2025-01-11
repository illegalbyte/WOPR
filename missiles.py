import math
import time
import a_star
from draw import Draw
from random import randint
from constants import WIDTH, REFRESH_RATE, SMALL_PAUSE, COLOURS, countries, console_prompts, WORLD_MAP, WORLD_MAP_GRAPH

class Missiles():
    """
    Class containing functions related to firing and drawing missiles.
    """

    def get_distance(x1: int, y1: int, x2: int , y2: int) -> int:
        """
        Calculate the distance between two coordinates.

        Args:
            x1 (int): The x-coordinate of the first point.
            y1 (int): The y-coordinate of the first point.
            x2 (int): The x-coordinate of the second point.
            y2 (int): The y-coordinate of the second point.

        Returns:
            int: The distance between the two points.
        """
        return math.hypot(x2-x1, y2-y1)
    
    def ICBM_gentle(STRIKE_X, STRIKE_Y, START_X=40, START_Y=17, ICON='X', COLOUR='PURPLE'):
        """
        Launch a missile in a line and then move diagonally towards the target.

        Args:
            STRIKE_X (int): The x-coordinate of the strike.
            STRIKE_Y (int): The y-coordinate of the strike.
            START_X (int): The starting x-coordinate.
            START_Y (int): The starting y-coordinate.
            ICON (str): The icon representing the missile.
            COLOUR (str): The color of the missile.
        """
        while (START_X, START_Y) != (STRIKE_X, STRIKE_Y):

            Draw.draw_char(START_X, START_Y, ICON, COLOUR=COLOUR)

            START_X += randint(0,1)

            NEW_SHORTEST_DIST = Missiles.get_distance(START_X, START_Y + 1, STRIKE_X, STRIKE_Y)
            if Missiles.get_distance(START_X - 1, START_Y, STRIKE_X, STRIKE_Y) < NEW_SHORTEST_DIST:
                NEW_SHORTEST_DIST = Missiles.get_distance(START_X - 1, START_Y, STRIKE_X, STRIKE_Y)
            if Missiles.get_distance(START_X + 1, START_Y, STRIKE_X, STRIKE_Y) < NEW_SHORTEST_DIST:
                NEW_SHORTEST_DIST = Missiles.get_distance(START_X + 1, START_Y, STRIKE_X, STRIKE_Y)
            if Missiles.get_distance(START_X, START_Y - 1, STRIKE_X, STRIKE_Y) < NEW_SHORTEST_DIST:
                NEW_SHORTEST_DIST = Missiles.get_distance(START_X, START_Y - 1, STRIKE_X, STRIKE_Y)
            if Missiles.get_distance(START_X, START_Y + 1, STRIKE_X, STRIKE_Y) == NEW_SHORTEST_DIST:
                START_Y += 1
            elif Missiles.get_distance(START_X - 1, START_Y, STRIKE_X, STRIKE_Y) == NEW_SHORTEST_DIST:
                START_X -= 1
            elif Missiles.get_distance(START_X + 1, START_Y, STRIKE_X, STRIKE_Y) == NEW_SHORTEST_DIST:
                START_X += 1
            elif Missiles.get_distance(START_X, START_Y - 1, STRIKE_X, STRIKE_Y) == NEW_SHORTEST_DIST:
                START_Y -= 1

            time.sleep(REFRESH_RATE)

    def ICBM_diag(START_X, START_Y, STRIKE_X, STRIKE_Y, COL='PURPLE', ICON='🌞', REFRESH_RATE=REFRESH_RATE):
        """
        Launch a missile in an angled diagonal line.

        Args:
            START_X (int): The starting x-coordinate.
            START_Y (int): The starting y-coordinate.
            STRIKE_X (int): The x-coordinate of the strike.
            STRIKE_Y (int): The y-coordinate of the strike.
            COL (str): The color of the missile.
            ICON (str): The icon representing the missile.
            REFRESH_RATE (float): The speed of the missile.
        """
        if STRIKE_X == START_X:
            STRIKE_X += 1
        elif STRIKE_Y == STRIKE_Y:
            STRIKE_Y += 1
        slope = (STRIKE_Y - START_Y) / (STRIKE_X - START_X)

        if (abs(START_X - STRIKE_X) < 4):
            Missiles.ICBM_gentle(STRIKE_X, STRIKE_Y, START_X, START_Y)
        else:
            if STRIKE_X > START_X:
                prev_xy = []
                for x in range(START_X, STRIKE_X):
                    prev_xy = [x, START_Y]
                    prev_char = Draw.get_original_character(prev_xy[0], round(prev_xy[1]))
                    Draw.draw_char(x, START_Y, ICON, COLOUR=COL)
                    START_Y += slope
                    time.sleep(REFRESH_RATE)
                    Draw.draw_char(prev_xy[0], prev_xy[1], prev_char, COLOUR='YELLOW')
            elif STRIKE_X < START_X:
                prev_xy = []
                for x in range(START_X-STRIKE_X):
                    prev_xy = [START_X-x, START_Y]
                    prev_char = Draw.get_original_character(prev_xy[0], round(prev_xy[1]))
                    Draw.draw_char(START_X-x, START_Y, ICON, COLOUR=COL)
                    START_Y -= slope
                    time.sleep(REFRESH_RATE)
                    Draw.draw_char(prev_xy[0], prev_xy[1], prev_char, COLOUR='YELLOW')
            
        Draw.draw_char(STRIKE_X, STRIKE_Y-1, '🌞')

    def ICBM_bresenham(start: tuple, strike: tuple, chemtrail=True, speed=0.03):
        """
        Launch a missile from start to strike using the Bresenham algorithm.

        Args:
            start (tuple): The starting coordinates.
            strike (tuple): The coordinates of the strike.
            chemtrail (bool): Whether to draw a chemtrail.
            speed (float): The speed of the missile.

        Returns:
            list: List of coordinates affected by the missile.
        """
        chemtrail_colour = "WHITE"
        chemtrail_icon = "*"
        line = Draw.get_line(start, strike)
        for xy in line:
            Draw.draw_char(xy[0], xy[1], chemtrail_icon, COLOUR=chemtrail_colour)
            time.sleep(speed)
            if xy == strike:
                fallout = Draw.draw_fallout(strike, 2, speed/2, "purple", "*")
                break

        return fallout
