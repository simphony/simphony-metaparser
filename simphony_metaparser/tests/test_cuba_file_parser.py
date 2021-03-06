import os
import unittest

import six
from simphony_metaparser.cuba_file_parser import CUBAFileParser
from simphony_metaparser.exceptions import ParsingError

# Basic, working document that complies with the spec
from simphony_metaparser.tests.utils import change_lines_starting_with, \
    extract_lines

TEMPLATE = """---
VERSION: 1.0

CUBA: Common Unified Base Attributes

Purpose: CUBA provides

CUBA_KEYS:
    UID:
        definition: unique id
        length: 32
        type: string

    POSITION:
        definition: Position of a point or node or atom
        shape: [3]
        type: double

    MATRIX:
        definition: A Matrix
        shape: [3, 3]
        type: double

    SIMPLE_DOUBLE:
        type: double
"""


class TestCUBAFileParser(unittest.TestCase):
    def setUp(self):
        self.yamldir = os.path.join(
            os.path.dirname(__file__),
            'fixtures',
            'yaml_files')
        self.parser = CUBAFileParser()

    def test_parse_cuba_real_file(self):
        with open(os.path.join(self.yamldir, "cuba.yml")) as f:
            root = self.parser.parse(f)
        self.assertEqual(len(root.entries), 117)

    def test_trivial_content(self):
        content = six.StringIO(TEMPLATE)
        root = self.parser.parse(content)

        self.assertEqual(root.header.version, "1.0")
        self.assertEqual(root.header.purpose, "CUBA provides")
        self.assertEqual(root.header.type, "CUBA")
        self.assertEqual(len(root.entries), 4)
        self.assertEqual(root.entries["UID"].length, 32)
        self.assertEqual(root.entries["UID"].type, "string")
        self.assertEqual(root.entries["UID"].definition, "unique id")
        self.assertEqual(root.entries["UID"].shape, [1])

        self.assertEqual(root.entries["POSITION"].shape, [3])
        self.assertEqual(root.entries["MATRIX"].shape, [3, 3])

    def test_parse_incorrect_version(self):
        content = six.StringIO(
            change_lines_starting_with(TEMPLATE, "VERSION", ""))
        with six.assertRaisesRegex(self,
                                   ParsingError,
                                   "find file format version specifier"):
            self.parser.parse(content)

        for version in ["hello", "[]"]:
            content = six.StringIO(
                change_lines_starting_with(
                    TEMPLATE,
                    "VERSION",
                    "VERSION: {}".format(version)))
            with six.assertRaisesRegex(
                    self,
                    ParsingError,
                    "The 'version' trait"):
                self.parser.parse(content)

        for version in ["2.0", "0.9"]:
            content = six.StringIO(
                change_lines_starting_with(
                    TEMPLATE,
                    "VERSION",
                    "VERSION: {}".format(version)))
            with six.assertRaisesRegex(self,
                                       ParsingError,
                                       "Unable to parse file version"):
                self.parser.parse(content)

    def test_parse_incorrect_cuba_marker(self):
        content = six.StringIO(
            change_lines_starting_with(TEMPLATE, "CUBA:", "")
        )

        with six.assertRaisesRegex(self,
                                   ParsingError,
                                   "Unable to find file type "
                                   "specification"):
            self.parser.parse(content)

    def test_no_cuba_keys(self):
        content = six.StringIO(extract_lines(TEMPLATE, 0, 7))
        with six.assertRaisesRegex(self, ParsingError,
                                   "Missing key CUBA_KEYS"):
            self.parser.parse(content)

    def test_unrecognized_root_key(self):
        content = six.StringIO(TEMPLATE+"\nunrecognized: 1\n")
        with six.assertRaisesRegex(self, ParsingError, "Unrecognized key"):
            self.parser.parse(content)

    def test_invalid_cuba_name(self):
        content = six.StringIO(
            TEMPLATE+"""
    whatever:
        definition: Position of a point or node or atom
        shape: [3]
        type: double
""")
        with six.assertRaisesRegex(self, ParsingError, "matching the pattern"):
            self.parser.parse(content)

    def test_no_type(self):
        content = six.StringIO(
            TEMPLATE+"""
    WHATEVER:
        definition: Position of a point or node or atom
        shape: [3]
""")
        with six.assertRaisesRegex(self, ParsingError, "Missing type"):
            self.parser.parse(content)

    def test_unrecognized_type(self):
        content = six.StringIO(
            TEMPLATE+"""
    WHATEVER:
        definition: Position of a point or node or atom
        shape: [3]
        type: floatingpoint
""")
        with six.assertRaisesRegex(self,
                                   ParsingError,
                                   "but a value of 'floatingpoint'"):
            self.parser.parse(content)

    def test_length_in_non_string(self):
        content = six.StringIO(
            TEMPLATE+"""
    WHATEVER:
        definition: Position of a point or node or atom
        type: integer
        length: 5
""")
        with six.assertRaisesRegex(self,
                                   ParsingError,
                                   "not a string, and length must be None"):
            self.parser.parse(content)

    def test_unrecognized_key_in_entry(self):
        content = six.StringIO(
            TEMPLATE+"""
    WHATEVER:
        definition: Position of a point or node or atom
        unrecognized: XXX
        type: integer
""")
        with six.assertRaisesRegex(self, ParsingError, "Unrecognized key"):
            self.parser.parse(content)
