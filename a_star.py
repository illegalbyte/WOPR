# A* Algorithm for Missile Pathfinding

import time

levelWidth = 153
levelHeight = 46


def getNextMoves(x, y):
    return {
        'left':  [x-1, y],
        'right': [x+1, y],
        'up':  [x, y-1],
        'down': [x, y+1],
        'ul': [x-1, y+1],
        'ur': [x+1, y+1],
        'dl': [x-1, y-1],
        'dr': [x+1, y-1]
    }.values()


def getShortestPath(level, startCoordinate, endCoordinate):
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
