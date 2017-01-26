from traits.trait_errors import TraitError

from .nodes import FixedPropertyEntry, \
    VariablePropertyEntry, FileHeaderInfo, CUBAEntry, CUDSEntry
from .flags import NoDefault
from .exceptions import ParsingError


def parse_header_info(data):
    """Parse and returns the FileHeaderInfo node.

    Parameters
    ----------
    data: dict or None
        The data extracted from the yaml format

    Returns
    -------
    FileHeaderInfo
    """

    if data is None:
        data = {}

    try:
        version = data["VERSION"]
    except KeyError:
        raise ParsingError("Unable to find file format version specifier")

    type_ = None

    if "CUBA" in data:
        type_ = "CUBA"
    elif "CUDS" in data:
        type_ = "CUDS"

    if type_ is None:
       raise ParsingError("Unable to find file type specification in header. "
                          "Key CUBA or CUDS missing")

    try:
        header = FileHeaderInfo(
            type=type_,
            version=version,
            purpose=data.get("Purpose", ""),
            resources=data.get("Resources", {}))
    except TraitError as e:
        raise ParsingError("Unable to parse file header: {}".format(str(e)))

    return header


def parse_cuba_entry(name, data):
    """Parses the content of the node from the direct yaml parsed content

    Parameters
    ----------
    name: str
        The name of the node

    data: dict or None
        The data _under_ the yaml node with the specified name

    Returns
    -------
    CUBAEntry
    """
    if data is None:
        data = {}

    try:
        type_ = data["type"]
    except KeyError:
        raise ParsingError("Missing type specification "
                           "for CUBA data type {}".format(name))

    try:
        return CUBAEntry(
            name=name,
            type=type_,
            definition=data.get("definition", ""),
            shape=data.get("shape", [1]),
            length=data.get("length")
        )
    except TraitError as e:
        raise ParsingError("Unable to create CUBA entry {}: {}".format(
            name, str(e)
        ))


def parse_cuds_entry(name, data):
    """Parses the content of the node from the direct yaml parsed content

    Parameters
    ----------
    name: str
        The name of the node

    data: dict or None
        The data _under_ the yaml node with the specified name

    Returns
    -------
    simphony_metaedit.parsers.nodes.CUDSEntry
    """

    if data is None:
        data = {}

    # Copy so that we don't alter the initial content.
    data = dict(data)

    try:
        parent = data.pop("parent")
    except KeyError:
        raise ParsingError("CUDS entry {} has no parent information.".format(
            name))

    if parent.strip() == "":
        parent = None

    try:
        entry = CUDSEntry(
            name=name,
            parent=parent,
            definition=data.get("definition", ""),
        )
    except TraitError as e:
        raise ParsingError("Unable to parse CUDS entry {}: {}".format(
            name, str(e)
        ))

    property_entries = {}

    try:
        for prop_name, prop_data in data.items():
            if prop_name.startswith("CUBA."):
                prop = parse_variable_property_entry(prop_name, prop_data)
            else:
                prop = parse_fixed_property_entry(prop_name, prop_data)
            property_entries[prop_name] = prop
    except ParsingError as e:
        raise ParsingError("Could not parse CUDS entry {}. {}".format(
            name, str(e)
        ))

    entry.property_entries = property_entries

    return entry


def parse_fixed_property_entry(name, data):
    """Extract the property entries from the yaml data

    Parameters
    ----------
    name: str
        The name of the property

    data: Dict or None
        The value data under the entry

    Returns
    -------
    FixedPropertyEntry
    """

    if not isinstance(data, dict):
        data = {
            "scope": "CUBA.USER",
            "default": data
        }

    try:
        return FixedPropertyEntry(
            name=name,
            scope=data.get("scope", "CUBA.USER"),
            default=data.get("default", NoDefault)
        )
    except TraitError as e:
        raise ParsingError("Unable to create Fixed Property {}: {}".format(
            name, str(e)
        ))


def parse_variable_property_entry(name, data):
    """Extract the property entries from the yaml data.

    Parameters
    ----------
    name: str
        The name of the property

    data: Dict or None
        The value data under the entry

    Returns
    -------
    VariablePropertyEntry

    """

    if data is None:
        data = {}

    try:
        shape = parse_shape(data.get("shape", None))
    except (TypeError, ValueError) as e:
        raise ParsingError(
            "Unable to parse shape for property {}. {}".format(name, str(e)))

    try:
        return VariablePropertyEntry(
            name=name,
            scope=data.get("scope", "CUBA.USER"),
            default=data.get("default", NoDefault),
            shape=shape
        )
    except TraitError as e:
        raise ParsingError("Unable to create Variable Property {}: {}".format(
            name, str(e)
        ))


def parse_shape(shape_spec):
    """Parses the shape as specified in the yaml file.

    Note that the colon notation e.g. (3, :) maps to a None e.g. (3, None).

    If shape is None, it will return the default [1].
    """
    if shape_spec is None:
        return [1]

    elif isinstance(shape_spec, (str, unicode)):
        shape_spec = shape_spec.strip()
        if shape_spec[0] not in "[(" or shape_spec[-1] not in "])":
            raise ValueError("Shape specification {} not "
                             "compliant to required format".format(shape_spec))

        elems = shape_spec[1:-1].split(",")

        def transform(el):
            el = el.strip()
            if el == ':':
                return None
            else:
                return int(el)

        shape = map(transform, elems)
    else:
        shape = shape_spec

    if not isinstance(shape, list):
        raise TypeError(
            "Shape not compliant with required type. Got {}".format(
                shape_spec
            ))

    if not all([x is None or x > 0 for x in shape]):
        raise ValueError("shape must be a list of positive or None values. "
                         "Got {}".format(shape))

    return shape
