import unittest
from compare_centers import count_matches


def box(x=0, z=0, label="Car"):
    return dict(x=x, y=0, z=z, label=label)


class CenterMatchTests(unittest.TestCase):
    def test_each_offline_box_used_once(self):
        self.assertEqual(count_matches([box(), box()], [box()]), 1)

    def test_different_classes_do_not_match(self):
        self.assertEqual(count_matches([box(label="Truck")], [box()]), 0)

    def test_vertical_distance_counts(self):
        self.assertEqual(count_matches([box(z=.51)], [box()]), 0)

    def test_augmenting_path_avoids_greedy_undercount(self):
        self.assertEqual(count_matches([box(.2), box(-.3)], [box(0), box(.6)]), 2)

    def test_boundary_included(self):
        self.assertEqual(count_matches([box(.5)], [box()]), 1)


if __name__ == "__main__":
    unittest.main()
