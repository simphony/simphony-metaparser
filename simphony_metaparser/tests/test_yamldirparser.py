import os
import unittest

from simphony_metaedit.parsers.exceptions import ParsingError
from simphony_metaedit.parsers.yamldirparser import YamlDirParser, \
    check_name_clash


class TestYamlDirParser(unittest.TestCase):
    def setUp(self):
        self.yamldir = os.path.join(
            os.path.dirname(__file__),
            'fixtures',
            'yaml_files')

    def notest_initialization(self):
        parser = YamlDirParser()

        root = parser.parse(self.yamldir)
        self.assertEqual(type(root), nodes.Root)
        self.assertEqual(len(list(nodes.traverse(root))), 398)

    def test_check_name_clash(self):
        with self.assertRaises(ParsingError):
            check_name_clash("hello", set(['what']), set(["CUBA.WHAT"]))

        check_name_clash("hello", set(["one"]), set(["CUBA.TWO"]))
