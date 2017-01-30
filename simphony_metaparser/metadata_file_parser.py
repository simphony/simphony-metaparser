from simphony_metaparser.base_file_parser import BaseFileParser

from .parsing_routines import parse_cuds_entry


class MetadataFileParser(BaseFileParser):
    def entry_key(self):
        """Returns the key to identify in the file, containing the entries
        to parse"""
        return "CUDS_KEYS"

    def expected_type(self):
        """Returns the expected type of the file"""
        return "CUDS"

    def parse_entry(self, name, data):
        """Performs parsing of an individual entry"""
        return parse_cuds_entry(name, data)
