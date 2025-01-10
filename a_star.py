# A* Algorithm for Missile Pathfinding

import time

levelWidth = 153
levelHeight = 46

def getNextMoves(x, y):
    """
    Get the possible next moves from the current position.

    Args:
        x (int): The current x-coordinate.
        y (int): The current y-coordinate.

    Returns:
        list: A list of possible next moves as (x, y) coordinates.
    """
    return {
        'left':  [x-1, y],
        'right': [x+1, y],
        'up':  [x, y-1],
        'down':  [x, y+1],
        'ul': [x-1, y+1],
        'ur': [x+1, y+1],
        'dl': [x-1, y-1],
        'dr': [x+1, y-1]
    }.values()

def getShortestPath(level, startCoordinate, endCoordinate):
    """
    Find the shortest path from the start coordinate to the end coordinate using the A* algorithm.

    Args:
        level (list): The game level represented as a 2D list.
        startCoordinate (list): The starting coordinate as [x, y].
        endCoordinate (list): The ending coordinate as [x, y].

    Returns:
        list: The shortest path as a list of coordinates.
    """
    searchPaths = [[startCoordinate]]
    visitedCoordinates = [startCoordinate]

    while searchPaths != []:
        currentPath = searchPaths.pop(0)
        currentCoordinate = currentPath[-1]

        currentX, currentY = currentCoordinate

        if currentCoordinate == endCoordinate:
            return currentPath

        for nextCoordinate in getNextMoves(currentX, currentY):
            nextX, nextY = nextCoordinate

            if nextX < 0 or nextX >= levelWidth:
                continue

            if nextY < 0 or nextY >= levelHeight:
                continue

            if nextCoordinate in visitedCoordinates:
                continue

            searchPaths.append(currentPath + [nextCoordinate])
            visitedCoordinates += [nextCoordinate]

# Unit tests for the functions in a_star.py
def test_getNextMoves():
    """
    Test the getNextMoves function.
    """
    assert getNextMoves(0, 0) == [[-1, 0], [1, 0], [0, -1], [0, 1], [-1, 1], [1, 1], [-1, -1], [1, -1]]
    assert getNextMoves(1, 1) == [[0, 1], [2, 1], [1, 0], [1, 2], [0, 2], [2, 2], [0, 0], [2, 0]]

def test_getShortestPath():
    """
    Test the getShortestPath function.
    """
    level = [[' ' for _ in range(levelWidth)] for _ in range(levelHeight)]
    assert getShortestPath(level, [0, 0], [1, 1]) == [[0, 0], [1, 1]]
    assert getShortestPath(level, [0, 0], [2, 2]) == [[0, 0], [1, 1], [2, 2]]

if __name__ == "__main__":
    test_getNextMoves()
    test_getShortestPath()
    print("All tests passed.")

