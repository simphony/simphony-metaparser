import os
import unittest

from simphony_metaparser.exceptions import ParsingError
from simphony_metaparser.nodes import Ontology, CUDSItem
from simphony_metaparser.yamldirparser import (
    check_name_clash, YamlDirParser, cuba_data_type_from_cuba_entry,
    property_entry_to_property, cuds_item_from_cuds_entry)


class TestYamlDirParser(unittest.TestCase):
    def setUp(self):
        self.yamldir = os.path.join(
            os.path.dirname(__file__),
            'fixtures',
            'yaml_files')

    def test_full_parsing(self):
        parser = YamlDirParser()
        ontology = parser.parse(self.yamldir)
        self.assertIsInstance(ontology, Ontology)

        self.assertEqual(len(ontology.data_types), 117)

        root_cuds = ontology.root_cuds_item

        self.assertEqual(root_cuds.name, "CUBA.CUDS_ITEM")
        self.assertIsNone(root_cuds.parent)
        self.assertEqual(len(root_cuds.children), 7)
        self.assertEqual(len(root_cuds.properties), 3)

        for child in root_cuds.children:
            self.assertIs(child.parent, root_cuds)

    def test_check_name_clash(self):
        with self.assertRaises(ParsingError):
            check_name_clash("hello", set(['what']), set(["CUBA.WHAT"]))

        check_name_clash("hello", set(["one"]), set(["CUBA.TWO"]))

    def test_conversion_routines_fail_for_incorrect_data(self):
        with self.assertRaises(TypeError):
            cuba_data_type_from_cuba_entry("foo")

        with self.assertRaises(TypeError):
            property_entry_to_property("foo", CUDSItem())

        with self.assertRaises(TypeError):
            cuds_item_from_cuds_entry("foo")
