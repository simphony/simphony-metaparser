import yaml

from .nodes import File
from .parsing_routines import parse_header_info, \
    parse_cuds_entry
from .exceptions import ParsingError


class MetadataFileParser:
    def parse(self, file_handle):
        """Parses the content of the specified filename.
        Returns a list of raw nodes for further processing.

        Parameters
        ----------
        file_handle: str
            Path of the file to parse

        Returns
        -------
        list of raw metadata nodes.
        """
        cuds_data = yaml.safe_load(file_handle)

        file = File()
        header = parse_header_info(cuds_data)

        if header.type != "CUDS":
            raise ParsingError("Unable to find file type marker for CUDS file")

        if header.version != "1.0":
            raise ParsingError("Unable to parse file version {}".format(
                header.version))

        try:
            keys = cuds_data["CUDS_KEYS"]
        except KeyError:
            raise ParsingError("Missing entry CUDS_KEYS")

        file.header = header
        entries = {}
        # We need to collect all cuds entities first, because in the file
        # they are a dictionary, and they can be recovered in arbitrary order.
        for name, data in keys.items():
            try:
                entry = parse_cuds_entry(name, data)
            except Exception as e:
                raise ParsingError("Unable to parse entry {} "
                                   "in {}: {}".format(name,
                                                      file_handle,
                                                      str(e)))

            entries[name] = entry

        file.entries = entries
        return file
