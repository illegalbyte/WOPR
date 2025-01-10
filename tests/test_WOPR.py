import unittest
from WOPR import draw, missiles, weapons, defcon, game

class TestWOPR(unittest.TestCase):

    def test_draw_char(self):
        draw.draw_char(0, 0, 'X', 'RED')
        self.assertEqual(draw.get_original_character(0, 0), 'X')

    def test_draw_targets(self):
        regions = {
            'EUROPE': {
                'GERMANY': (91, 10),
                'FRANCE': (81, 12),
                'RUSSIA': (99, 9)
            }
        }
        draw.draw_targets(regions)
        self.assertEqual(draw.get_original_character(91, 10), '{X}')
        self.assertEqual(draw.get_original_character(81, 12), '{X}')
        self.assertEqual(draw.get_original_character(99, 9), '{X}')

    def test_draw_fallout(self):
        draw.draw_fallout(10, 10, 2, 0.003)
        self.assertEqual(draw.get_original_character(10, 10), 'X')

    def test_ask_for_coordinates(self):
        coordinates = draw.ask_for_coordinates()
        self.assertIsInstance(coordinates, tuple)
        self.assertEqual(len(coordinates), 2)

    def test_console(self):
        draw.console("Test message")
        self.assertIn("Test message", console_prompts)

    def test_player_list(self):
        allies = ['FRANCE', 'GERMANY']
        enemies = ['RUSSIA']
        player = 'USA'
        draw.player_list(allies, enemies, player)
        self.assertIn('FRANCE', allies)
        self.assertIn('RUSSIA', enemies)
        self.assertEqual(player, 'USA')

    def test_clear_lines(self):
        draw.clear_lines(0, 10)
        for y in range(0, 10):
            for x in range(WIDTH):
                self.assertEqual(draw.get_original_character(x, y), ' ')

    def test_clear_to_edge(self):
        draw.clear_to_edge(0, 10, 0)
        for y in range(0, 10):
            for x in range(WIDTH):
                self.assertEqual(draw.get_original_character(x, y), ' ')

    def test_get_original_character(self):
        character = draw.get_original_character(0, 0)
        self.assertIsInstance(character, str)

    def test_get_distance(self):
        distance = missiles.get_distance(0, 0, 3, 4)
        self.assertEqual(distance, 5)

    def test_ICBM_gentle(self):
        missiles.ICBM_gentle(10, 10, 0, 0, 'X', 'RED')
        self.assertEqual(draw.get_original_character(10, 10), 'X')

    def test_ICBM_diag(self):
        missiles.ICBM_diag(0, 0, 10, 10, 'RED', 'X', 0.002)
        self.assertEqual(draw.get_original_character(10, 10), 'X')

    def test_ICBM_shortestPath(self):
        missiles.ICBM_shortestPath(0, 0, 10, 10)
        self.assertEqual(draw.get_original_character(10, 10), 'X')

    def test_simultanious_launch(self):
        launch_coords = missiles.simultanious_launch(2)
        self.assertIsInstance(launch_coords, list)
        self.assertEqual(len(launch_coords), 2)

    def test_launch_ICBM_diag2(self):
        missiles.launch_ICBM_diag2(0, 0, 10, 10, 'RED', 'X')
        self.assertEqual(draw.get_original_character(10, 10), 'X')

    def test_draw_base(self):
        base = weapons((10, 10), 10, True, 'USA')
        base.draw_base()
        self.assertEqual(draw.get_original_character(10, 10), '@')

    def test_move(self):
        sub = submarine((10, 10), 10, True, 'USA', '🛥')
        new_coords = sub.move(20, 20)
        self.assertEqual(new_coords, (20, 20))

    def test_display(self):
        defcon.display(5)
        self.assertEqual(defcon.defcon_status, 5)

    def test_game(self):
        game('autofire')
        self.assertTrue(True)

if __name__ == "__main__":
    unittest.main()
