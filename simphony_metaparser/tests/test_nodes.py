import unittest
from simphony_metaedit import nodes


class TestNodes(unittest.TestCase):
    def test_traversal(self):
        root = nodes.Root()
        concepts = nodes.Concepts()
        root.children.append(concepts)

        animal = nodes.Concept(name="animal")
        concepts.children.append(animal)

        dog = nodes.Concept(name="dog")
        cat = nodes.Concept(name="cat")
        horse = nodes.Concept(name="horse")

        animal.children.extend([dog, cat, horse])

        vehicle = nodes.Concept(name="vehicle")
        concepts.children.append(vehicle)
        truck = nodes.Concept(name="truck")
        car = nodes.Concept(name="car")
        plane = nodes.Concept(name="plane")
        glider = nodes.Concept(name="sailplane")

        plane.children.append(glider)
        vehicle.children.extend([truck, car, plane])

        self.assertEqual(
            [(x.name, level) for x, level in nodes.traverse(root)],
            [('/', 0),
             ('Concepts', 1),
             ('animal', 2),
             ('dog', 3),
             ('cat', 3),
             ('horse', 3),
             ('vehicle', 2),
             ('truck', 3),
             ('car', 3),
             ('plane', 3),
             ('sailplane', 4)]
        )
