import os
import unittest

from simphony_metaparser.utils import traverse, traverse_to_root
from simphony_metaparser.yamldirparser import YamlDirParser


class TestUtils(unittest.TestCase):
    def setUp(self):
        self.yamldir = os.path.join(
            os.path.dirname(__file__),
            'fixtures',
            'yaml_files')
        parser = YamlDirParser()
        self.ontology = parser.parse(self.yamldir)

    def test_traverse(self):
        ontology = self.ontology
        traversal = list(traverse(ontology.root_cuds_item))
        self.assertEqual(len(traversal), 100)

        self.assertEqual(traversal[0][0], ontology.root_cuds_item)
        self.assertEqual(traversal[0][1], 0)

    def test_traverse_to_root(self):
        ontology = self.ontology
        traversal = list(traverse(ontology.root_cuds_item))

        for node, level in traversal:
            to_root = list(traverse_to_root(node))
            self.assertEqual(len(to_root), level+1)
            self.assertEqual(to_root[0], node)

            for rev_level, entry in enumerate(to_root):
                if rev_level+1 < len(to_root):
                    self.assertEqual(entry.parent, to_root[rev_level+1])
                else:
                    self.assertIsNone(entry.parent)
