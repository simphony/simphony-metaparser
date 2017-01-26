from simphony_metaparser.base_file_parser import BaseFileParser

from .parsing_routines import parse_cuds_entry


class MetadataFileParser(BaseFileParser):

    def entry_key(self):
        return "CUDS_KEYS"

    def expected_type(self):
        return "CUDS"

    def parse_entry(self, name, data):
        return parse_cuds_entry(name, data)
