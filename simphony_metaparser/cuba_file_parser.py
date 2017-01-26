from simphony_metaparser.base_file_parser import BaseFileParser
from simphony_metaparser.parsing_routines import parse_cuba_entry


class CUBAFileParser(BaseFileParser):
    def entry_key(self):
        return "CUBA_KEYS"

    def expected_type(self):
        return "CUBA"

    def parse_entry(self, name, data):
        return parse_cuba_entry(name, data)
