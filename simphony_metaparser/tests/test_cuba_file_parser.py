import os
import unittest

from simphony_metaparser import nodes
from simphony_metaparser.cuba_file_parser import (
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
                              nodes.FileHeaderInfo)
        self.assertEqual(header.version, "1.0")
        self.assertEqual(header.type, "CUBA")

        self.assertNotEqual(len(header.purpose), 0)
        self.assertEqual(len(header.resources), 0)
