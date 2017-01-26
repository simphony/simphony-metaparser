import os
import unittest

from simphony_metaparser.exceptions import ParsingError
from simphony_metaparser.yamldirparser import \
    check_name_clash, YamlDirParser


class TestYamlDirParser(unittest.TestCase):
    def setUp(self):
        self.yamldir = os.path.join(
            os.path.dirname(__file__),
            'fixtures',
            'yaml_files')

    def test_full_parsing(self):
        parser = YamlDirParser()
        nodes = parser.parse(self.yamldir)

    def test_check_name_clash(self):
        with self.assertRaises(ParsingError):
            check_name_clash("hello", set(['what']), set(["CUBA.WHAT"]))

        check_name_clash("hello", set(["one"]), set(["CUBA.TWO"]))
