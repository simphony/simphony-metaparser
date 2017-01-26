import yaml
import six
import abc

from .nodes import File
from .parsing_routines import parse_header_info
from .exceptions import ParsingError


@six.add_metaclass(abc.ABCMeta)
class BaseFileParser(object):
    """Common parser class that handles both files for the header,
    and delegates to subclasses the handling of the keys.
    """
    def supported_versions(self):
        """Returns a list of the supported file versions"""
        return ["1.0"]

    def recognized_root_keys(self, version):
        """Returns the recognized keys for a given version, as a set"""
        return {
            "VERSION",
            self.expected_type(),
            "Resources",
            "Purpose",
            self.entry_key()
        }

    @abc.abstractmethod
    def expected_type(self):
        """The expected type in the header.
        Must return "CUBA" or "CUDS"
        """

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
            data = yaml.safe_load(file_handle)
        except Exception as e:
            raise ParsingError("Unable to parse basic YAML "
                               "structure. {}".format(e))

        header = parse_header_info(data)

        if header.version not in self.supported_versions():
            raise ParsingError("Unable to parse file version {}".format(
                header.version))

        unrecognized_keys = set(data.keys()).difference(
            self.recognized_root_keys(header.version))

        if len(unrecognized_keys) != 0:
            raise ParsingError("Unrecognized key(s) "
                               "in file: {}".format(unrecognized_keys))

        if header.type != self.expected_type():
            raise ParsingError("Unable to find correct file type marker")

        file_node = File()
        file_node.header = header

        try:
            entry_keys = data[self.entry_key()]
        except KeyError:
            raise ParsingError("Missing key {}".format(self.entry_key()))

        if not isinstance(entry_keys, dict):
            raise ParsingError("{} does not contain a mapping".format(
                self.entry_key()))

        entries = {}

        for name, data in entry_keys.items():
            try:
                entry = self.parse_entry(name, data)
            except Exception as e:
                raise ParsingError("Unable to parse entry {} : "
                                   "{}".format(name, str(e)))
            entries[name] = entry

        file_node.entries = entries

        return file_node

    @abc.abstractmethod
    def parse_entry(self, name, data):
        """Reimplemented in subclasses to extract data from the
        CUBA/CUDS_KEYS"""

    @abc.abstractmethod
    def entry_key(self):
        """Returns the container in the file that has the entries.
        it's CUBA_KEYS or CUDS_KEYS depending on the file"""
