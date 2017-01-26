import os
import unittest

import simphony_metaedit.parsers.nodes
from simphony_metaedit import nodes
from simphony_metaedit.parsers.cuba_file_parser import (
    CUBAFileParser)


class TestCUBAFileParser(unittest.TestCase):
    def setUp(self):
        self.yamldir = os.path.join(
            os.path.dirname(__file__),
            'fixtures',
            'yaml_files')

    def test_parse_cuba_file(self):
        parser = CUBAFileParser()
        with open(os.path.join(self.yamldir, "cuba.yml")) as f:
            file = parser.parse(f)
        self.assertEqual(len(file.entries), 6)

        header = file.header
        self.assertIsInstance(header,
                              simphony_metaedit.parsers.nodes.FileHeaderInfo)
        self.assertEqual(header.version, "1.0")
        self.assertEqual(header.type, "CUBA")

        self.assertNotEqual(len(header.purpose), 0)
        self.assertEqual(len(header.resources), 0)
