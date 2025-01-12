import unittest
from archived_files.a_star import getNextMoves, getShortestPath

class TestAStar(unittest.TestCase):

    def test_getNextMoves(self):
        self.assertEqual(getNextMoves(0, 0), [[-1, 0], [1, 0], [0, -1], [0, 1], [-1, 1], [1, 1], [-1, -1], [1, -1]])
        self.assertEqual(getNextMoves(1, 1), [[0, 1], [2, 1], [1, 0], [1, 2], [0, 2], [2, 2], [0, 0], [2, 0]])

    def test_getShortestPath(self):
        level = [[' ' for _ in range(153)] for _ in range(46)]
        self.assertEqual(getShortestPath(level, [0, 0], [1, 1]), [[0, 0], [1, 1]])
        self.assertEqual(getShortestPath(level, [0, 0], [2, 2]), [[0, 0], [1, 1], [2, 2]])

if __name__ == "__main__":
    unittest.main()
