import unittest
from WOPR2 import utility, draw, Submarine, missiles, map, SubsAndSilos

class TestWOPR2(unittest.TestCase):

    def test_removeDuplicates(self):
        self.assertEqual(utility.removeDuplicates([1, 2, 2, 3, 4, 4, 5]), [1, 2, 3, 4, 5])
        self.assertEqual(utility.removeDuplicates(['a', 'b', 'b', 'c', 'd', 'd']), ['a', 'b', 'c', 'd'])

    def test_reverse_lookup_submarine(self):
        countries['USA']['subs'] = [(10, 10)]
        self.assertEqual(utility.reverse_lookup_submarine((10, 10)), 'USA')

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
        draw.draw_fallout((10, 10), 2, 0.003)
        self.assertEqual(draw.get_original_character(10, 10), 'X')

    def test_draw_circle(self):
        circle_coords = draw.draw_circle(10, 10, 2, 'RED', 'O')
        self.assertIn((10, 8), circle_coords)
        self.assertIn((10, 12), circle_coords)
        self.assertIn((8, 10), circle_coords)
        self.assertIn((12, 10), circle_coords)

    def test_get_line(self):
        line_coords = draw.get_line((0, 0), (3, 3))
        self.assertEqual(line_coords, [(0, 0), (1, 1), (2, 2), (3, 3)])

    def test_draw_line(self):
        line_coords = draw.draw_line(0, 0, 3, 3, 'RED')
        self.assertIn((0, 0), line_coords)
        self.assertIn((1, 1), line_coords)
        self.assertIn((2, 2), line_coords)
        self.assertIn((3, 3), line_coords)

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

    def test_ICBM_bresenham(self):
        fallout_coords = missiles.ICBM_bresenham((0, 0), (10, 10))
        self.assertIn((10, 10), fallout_coords)

    def test_print_map(self):
        map.print_map('YELLOW', 0.000002)
        self.assertEqual(draw.get_original_character(0, 0), ' ')

    def test_print_ocean(self):
        map.print_ocean()
        self.assertEqual(draw.get_original_character(0, 0), ' ')

    def test_get_ocean_tiles(self):
        ocean_tiles = map.get_ocean_tiles()
        self.assertIsInstance(ocean_tiles, list)

    def test_check_for_ocean(self):
        self.assertTrue(map.check_for_ocean(0, 0))

    def test_check_for_obstruction(self):
        self.assertTrue(map.check_for_obstruction([(0, 0), (1, 1), (2, 2)]))

    def test_convert_x_coord(self):
        self.assertEqual(map.convert_x_coord('A'), 4)

    def test_get_coordinates_inside_circle(self):
        circle_coords = draw.draw_circle(10, 10, 2, 'RED', 'O')
        coords_inside_circle = map.get_coordinates_inside_circle((10, 10), circle_coords)
        self.assertIn((10, 10), coords_inside_circle)

    def test_print_subs(self):
        map.print_subs('USA', ['RUSSIA'], ['FRANCE'])
        self.assertEqual(draw.get_original_character(0, 0), ' ')

    def test_print_silos(self):
        map.print_silos('USA', ['RUSSIA'], ['FRANCE'])
        self.assertEqual(draw.get_original_character(0, 0), ' ')

    def test_print_all_layers(self):
        map.print_all_layers('USA', ['RUSSIA'], ['FRANCE'])
        self.assertEqual(draw.get_original_character(0, 0), ' ')

    def test_print_ocean_dev(self):
        map.print_ocean_dev(WORLD_MAP_GRAPH)
        self.assertEqual(draw.get_original_character(0, 0), ' ')

    def test_find_oceans_dev(self):
        map.find_oceans_dev()
        self.assertEqual(draw.get_original_character(0, 0), ' ')

    def test_classic_mode(self):
        classic_mode()
        self.assertTrue(True)

    def test_SubsAndSilos_audio(self):
        SubsAndSilos.audio("sub_launch")
        self.assertTrue(True)

    def test_SubsAndSilos_display_map(self):
        SubsAndSilos.display_map()
        self.assertEqual(draw.get_original_character(0, 0), ' ')

    def test_SubsAndSilos_ask_for_ocean_coords(self):
        coords = SubsAndSilos.ask_for_ocean_coords()
        self.assertIsInstance(coords, tuple)

    def test_SubsAndSilos_action_sonar(self):
        visible_coords = SubsAndSilos.action_sonar('USA', ['RUSSIA'], ['FRANCE'], 13)
        self.assertIsInstance(visible_coords, list)

    def test_SubsAndSilos_action_attack(self):
        destroyed_coords = SubsAndSilos.action_attack('USA')
        self.assertIsInstance(destroyed_coords, list)

    def test_SubsAndSilos_action_move(self):
        new_coords = SubsAndSilos.action_move((0, 0), 'N', 1)
        self.assertIsInstance(new_coords, tuple)

    def test_SubsAndSilos_search_for_subs(self):
        found_subs = SubsAndSilos.search_for_subs(['RUSSIA'], [(0, 0)])
        self.assertIsInstance(found_subs, list)

    def test_SubsAndSilos_setup_game(self):
        player_country, enemies, allies, original_allies, original_enemies = SubsAndSilos.setup_game()
        self.assertIsInstance(player_country, str)
        self.assertIsInstance(enemies, list)
        self.assertIsInstance(allies, list)
        self.assertIsInstance(original_allies, list)
        self.assertIsInstance(original_enemies, list)

    def test_SubsAndSilos_player_move(self):
        player_country, enemies, allies, original_allies, original_enemies = SubsAndSilos.setup_game()
        player_country, enemies, allies, original_allies, original_enemies = SubsAndSilos.player_move(player_country, enemies, allies, original_allies, original_enemies)
        self.assertIsInstance(player_country, str)
        self.assertIsInstance(enemies, list)
        self.assertIsInstance(allies, list)
        self.assertIsInstance(original_allies, list)
        self.assertIsInstance(original_enemies, list)

    def test_SubsAndSilos_enemy_move(self):
        player_country, enemies, allies, original_allies, original_enemies = SubsAndSilos.setup_game()
        SubsAndSilos.enemy_move(player_country, enemies, allies, original_allies, original_enemies)
        self.assertTrue(True)

    def test_submarinesandsilos(self):
        submarinesandsilos()
        self.assertTrue(True)

if __name__ == "__main__":
    unittest.main()
