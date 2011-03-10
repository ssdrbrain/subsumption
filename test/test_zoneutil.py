import unittest
import zoneutil
import zone

class Test(unittest.TestCase):
    def test_player_manager(self):
        # create stuff
        manager = zoneutil.PlayerManager()
        p1 = manager.new_player()
        p2 = manager.new_player()
        
        # check that things got added as expected
        self.assertNotEqual(p1.gid, p2.gid)
        self.assertEqual(len(manager), 2)
        
        # remove a player
        manager.remove_player(p1)
        self.assertEqual(len(manager), 1)
        
        # add another player, and check that the gid was reused
        p3 = manager.new_player()
        self.assertEqual(p3.gid, 0)
        self.assertEqual(len(manager), 2)

    def test_arena_mapping(self):
        # create some objects
        map = zoneutil.ZoneMapping()
        r = zone.Realm()
        a = zone.Arena(r)

        # assign some values into the map
        map[None]['cmd_x'] = 1
        map[None]['cmd_y'] = 2
        map[a]['cmd_x'] = 3
        map[a]['cmd_z'] = 4
        
        # make sure they're as expected
        self.assertEqual(map[None]['cmd_x'], 1)
        self.assertEqual(map[None]['cmd_y'], 2)
        self.assertNotIn('cmd_z', map[None])
        self.assertEqual(len(map[None]), 2)
        self.assertEqual(map[a]['cmd_x'], 3)
        self.assertEqual(map[a]['cmd_y'], 2)
        self.assertEqual(map[a]['cmd_z'], 4)
        self.assertEqual(len(map[a]), 3)
        
        # remove some values and do checking
        del map[a]['cmd_x']
        self.assertEqual(map[a]['cmd_x'], 1)
        del map[None]['cmd_y']
        self.assertNotIn('cmd_y', map[a])
        self.assertNotIn('cmd_y', map[None])
        
        # remove the remaining values
        del map[a]['cmd_z']
        del map[None]['cmd_x']
        self.assertEquals(len(map[a]), 0)
        self.assertEquals(len(map[None]), 0)

if __name__ == "__main__":
    unittest.main()