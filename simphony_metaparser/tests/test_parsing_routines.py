import os
import unittest

from simphony_metaedit.parsers.parsing_routines import parse_cuba_entry, \
    parse_cuds_entry, parse_shape, \
    parse_fixed_property_entry, parse_variable_property_entry

from simphony_metaedit.nodes import VariablePropertyEntry, \
    FixedPropertyEntry
from simphony_metaedit.parsers.nodes import NoDefault, FixedPropertyEntry, \
    VariablePropertyEntry
from simphony_metaedit.parsers.exceptions import ParsingError


class TestParsingRoutines(unittest.TestCase):
    def setUp(self):
        self.yamldir = os.path.join(
            os.path.dirname(__file__),
            'fixtures',
            'yaml_files')

    def test_parse_cuba_entry(self):
        res = parse_cuba_entry("POSITION", {
            "definition": "position",
            "shape": [3],
            "type": "double",
        })

        self.assertEqual(res.name, "POSITION")
        self.assertEqual(res.definition, "position")
        self.assertEqual(res.shape, [3])
        self.assertEqual(res.type, "double")

    def test_default_shape(self):
        res = parse_cuba_entry("POSITION", {
            "type": "double",
        })

        self.assertEqual(res.shape, [1])

    def test_missing_length_if_string(self):
        res = parse_cuba_entry("POSITION", {
            "type": "string",
            "length": 12
        })

        self.assertEqual(res.length, 12)

        with self.assertRaises(ParsingError):
            parse_cuba_entry("POSITION", {
                "type": "string",
            })

    def test_parse_cuds_entry(self):
        node = parse_cuds_entry("MIXTURE_MODEL", {
            "definition": "mixture (drift flux) model",
            "parent": "CUBA.PHYSICS_EQUATION",
            "models": ["CUBA.CONTINUUM"],
            "CUBA.WHATEVER": {
            }
        })

        self.assertEqual(node.name, "MIXTURE_MODEL")
        props = node.property_entries
        self.assertEqual(len(props), 3)
        self.assertEqual(
            len([p for p in props.values()
                 if isinstance(p, FixedPropertyEntry)]),
            2)
        self.assertEqual(
            len([p for p in props.values()
                 if isinstance(p, VariablePropertyEntry)]),
            1)

    def test_check_parent_parsing(self):
        res = parse_cuds_entry("MIXTURE_MODEL", {
            "parent": "",
        })

        self.assertEqual(res.parent, None)

        res = parse_cuds_entry("MIXTURE_MODEL", {
            "parent": "CUBA.WHATEVER",
        })

        self.assertEqual(res.parent, "CUBA.WHATEVER")

        with self.assertRaises(ParsingError):
            parse_cuds_entry("MIXTURE_MODEL", {
                "parent": "notcubakey",
            })

    def test_parse_missing_parent_cuds_entry(self):
        with self.assertRaises(ParsingError):
            parse_cuds_entry("MIXTURE_MODEL", {
                "definition": "mixture (drift flux) model",
                "models": ["CUBA.CONTINUUM"],
            })

    def test_parse_property_entry(self):
        res = parse_variable_property_entry("CUBA.FOO", {})

        self.assertIsInstance(res, VariablePropertyEntry)
        self.assertEqual(res.shape, [1])
        self.assertEqual(res.default, NoDefault)
        self.assertEqual(res.scope, "CUBA.USER")

        res = parse_fixed_property_entry("whatever", "hello")

        self.assertIsInstance(res, FixedPropertyEntry)
        self.assertEqual(res.default, "hello")
        self.assertEqual(res.scope, "CUBA.USER")

        with self.assertRaises(ParsingError):
            parse_fixed_property_entry("hello", {
                "scope": "CUBA.SYSTEM",
                "default": "[1]"
            })

        with self.assertRaises(ParsingError):
            parse_fixed_property_entry("hello", {
                "scope": "CUBA.USER",
            })

        with self.assertRaises(ParsingError):
            res = parse_variable_property_entry("hello", {
                "scope": "CUBA.SYSTEM",
                "default": [1]
            })

    def test_parse_shape(self):
        self.assertEqual(parse_shape(None), [1])
        self.assertEqual(parse_shape([1, 2]), [1, 2])
        self.assertEqual(parse_shape("(1, 2)"), [1, 2])
        self.assertEqual(parse_shape("(1, :, 3)"), [1, None, 3])
        self.assertEqual(parse_shape("(:)"), [None])
