import bext
import sys

# Define WIDTH constant
WIDTH, HEIGHT = bext.size()
WIDTH -= 1

# Define REFRESH_RATE constant
REFRESH_RATE = 0.00002

# Define SMALL_PAUSE constant
SMALL_PAUSE = 0.0008

# Define COLOURS constant
COLOURS = ['red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white']

# Define countries constant
countries = {
    'GERMANY': {
        'location': (91, 10),
        'status': True,
        'region': 'EUROPE',
        'subs': [],
    },
    'FRANCE': {
        'location': (81, 12),
        'status': True,
        'region': 'EUROPE',
        'subs': [],
    },
    'RUSSIA': {
        'location': (99, 9),
        'status': True,
        'region': 'EUROPE',
        'subs': [],
    },
    'COLOMBIA': {
        'location': (49, 23),
        'status': True,
        'region': 'AMERICAS',
        'subs': [],
    },
    'USA': {
        'location': (34, 14),
        'status': True,
        'region': 'AMERICAS',
        'subs': [],
    },
    'CHINA': {
        'location': (121, 15),
        'status': True,
        'region': 'ASIA',
        'subs': [],
    },
    'INDIA': {
        'location': (110, 20),
        'status': True,
        'region': 'ASIA',
        'subs': [],
    },
    'PAKISTAN': {
        'location': (107, 17),
        'status': True,
        'region': 'ASIA',
        'subs': [],
    },
    'AUSTRALIA': {
        'location': (132, 30),
        'status': True,
        'region': 'PACIFIC',
        'subs': [],
    }
}

# Define console_prompts constant
console_prompts = []

# Define WORLD_MAP constant
with open('WORLD_MAP.txt', 'r') as map_file:
    WORLD_MAP = map_file.read()

# Define WORLD_MAP_GRAPH constant
WORLD_MAP_GRAPH = WORLD_MAP.splitlines()
WORLD_MAP_GRAPH = [list(line) for line in WORLD_MAP_GRAPH]
sys.setrecursionlimit(len(WORLD_MAP_GRAPH) * len(WORLD_MAP_GRAPH[0]) * 2)
