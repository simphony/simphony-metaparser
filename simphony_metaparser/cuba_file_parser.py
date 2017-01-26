import yaml

from .nodes import File
from .parsing_routines import (
    parse_header_info,
    parse_cuba_entry)
from .exceptions import ParsingError


class CUBAFileParser:
    def parse(self, file_handle):
        """Parses the content of the specified file.
        Returns a list of nodes for further processing.

        Parameters
        ----------
        file_handle: file object
            file to parse

        Returns
        -------
        list of raw CUBA nodes.
        """
        cuba_data = yaml.safe_load(file_handle)

        file = File()
        header = parse_header_info(cuba_data)

        if header.type != "CUBA":
            raise ParsingError("Unable to find file type marker for CUBA file")

        if header.version != "1.0":
            raise ParsingError("Unable to parse file version {}".format(
                header.version))

        file.header = header

        entries = {}

        try:
            cuba_keys = cuba_data["CUBA_KEYS"]
        except KeyError:
            raise ParsingError("Missing entry CUBA_KEYS")

        for name, data in cuba_keys.items():
            try:
                entry = parse_cuba_entry(name, data)
            except Exception as e:
                raise ParsingError("Unable to parse entry {} "
                                   "in {}: {}".format(name,
                                                      file_handle,
                                                      str(e.message)))
            entries[name] = entry

        file.entries = entries
        return file
