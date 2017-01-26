import os
import unittest
from simphony_metaedit.parsers.metadata_file_parser import (
    MetadataFileParser)


class TestYamlDirParser(unittest.TestCase):
    def setUp(self):
        self.yamldir = os.path.join(
            os.path.dirname(__file__),
            'fixtures',
            'yaml_files')

    def test_parse_metadata_file(self):
        parser = MetadataFileParser()
        with open(os.path.join(self.yamldir, "simphony_metadata.yml")) as f:
            file = parser.parse(f)
        self.assertEqual(len(file.entries), 99)
