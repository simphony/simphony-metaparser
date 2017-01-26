import os
import six
import unittest

from simphony_metaparser import nodes
from simphony_metaparser.cuba_file_parser import (
    CUBAFileParser)
from simphony_metaparser.exceptions import ParsingError

from .fixtures import cuba_inputs


class TestCUBAFileParser(unittest.TestCase):
    def parse(self, string):
        parser = CUBAFileParser()
        f = six.StringIO(string)
        return parser.parse(f)

    def test_parse_cuba_file(self):
        file = self.parse(cuba_inputs.sane_file())
        self.assertEqual(len(file.entries), 6)

        header = file.header
        self.assertIsInstance(header,
                              nodes.FileHeaderInfo)
        self.assertEqual(header.version, "1.0")
        self.assertEqual(header.type, "CUBA")

        self.assertNotEqual(len(header.purpose), 0)
        self.assertEqual(len(header.resources), 0)

    def test_unrecognized_root_key(self):
        with self.assertRaisesRegex(ParsingError, "Unrecognized key"):
            self.parse(cuba_inputs.rogue_root_entry())

    def test_unrecognized_version(self):
        with self.assertRaisesRegex(ParsingError, "parse file version 1.1"):
            self.parse(cuba_inputs.unrecognized_version())

    def test_missing_version(self):
        with self.assertRaisesRegex(ParsingError, "find file format version"):
            self.parse(cuba_inputs.missing_version())

    def test_missing_cuba_keys(self):
        with self.assertRaisesRegex(ParsingError, "Missing entry CUBA_KEYS"):
            self.parse(cuba_inputs.header())

    def test_no_mapping_cuba_keys(self):
        with self.assertRaisesRegex(ParsingError, "must contain a mapping"):
            self.parse(cuba_inputs.header()+"""\nCUBA_KEYS:\n""")
