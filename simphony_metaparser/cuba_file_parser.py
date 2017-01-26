import yaml

from .nodes import File
from .parsing_routines import (
    parse_header_info,
    parse_cuba_entry)
from .exceptions import ParsingError


class CUBAFileParser:
    # Trivial check: verify the file version before acting. We support only

    # these versions
    SUPPORTED_VERSIONS = ["1.0"]

    # The recognized keys for version 1.0 for the root of the yaml file
    _RECOGNIZED_KEYS_ROOT_1_0 = {
        "VERSION",
        "CUBA",
        "Resources",
        "Purpose",
        "CUBA_KEYS"}

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
        try:
            cuba_data = yaml.safe_load(file_handle)
        except Exception as e:
            raise ParsingError("Unable to parse basic YAML "
                               "structure. {}".format(e))

        file = File()

        unrecognized_keys = set(cuba_data.keys()).difference(
            self._RECOGNIZED_KEYS_ROOT_1_0)

        if len(unrecognized_keys) != 0:
            raise ParsingError("Unrecognized key(s) "
                               "in file: {}".format(unrecognized_keys))

        header = parse_header_info(cuba_data)

        if header.type != "CUBA":
            raise ParsingError("Unable to find file type marker for CUBA file")

        if header.version not in self.SUPPORTED_VERSIONS:
            raise ParsingError("Unable to parse file version {}".format(
                header.version))

        file.header = header

        try:
            cuba_keys = cuba_data["CUBA_KEYS"]
        except KeyError:
            raise ParsingError("Missing key CUBA_KEYS")

        if not isinstance(cuba_keys, dict):
            raise ParsingError(
                "CUBA_KEYS must contain a mapping in {}".format(
                    file_handle))

        entries = {}

        for name, data in cuba_keys.items():
            try:
                entry = parse_cuba_entry(name, data)
            except Exception as e:
                raise ParsingError("Unable to parse entry {} "
                                   "in {}: {}".format(name,
                                                      file_handle,
                                                      str(e)))
            entries[name] = entry

        file.entries = entries
        return file
