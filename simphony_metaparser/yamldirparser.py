import os

from simphony_metaparser.utils import with_cuba_prefix
from . import utils
from .nodes import CUBADataType, CUDSItem, \
    VariablePropertyEntry, FixedPropertyEntry, CUBAEntry, CUDSEntry, \
    FixedProperty, VariableProperty
from .cuba_file_parser import CUBAFileParser
from .exceptions import ParsingError
from .metadata_file_parser import MetadataFileParser
from . import nodes


class YamlDirParser:
    """Parser for the current format of metadata as two files in a directory.
    The file format is specified in simphony-metadata documentation.
    """

    def parse(self, directory):
        """Parses a directory containing file and extracts the tree.

        Parameters
        ----------
        directory: str
            the directory containing the cuba.yml and simphony_metadata.yml.

        Returns
        -------
        The object tree.
        """
        cuba_file_path = os.path.join(directory, "cuba.yml")
        with open(cuba_file_path) as f:
            parsed_cuba = CUBAFileParser().parse(f)

        metadata_file_path = os.path.join(directory, "simphony_metadata.yml")
        with open(metadata_file_path) as f:
            parsed_metadata = MetadataFileParser().parse(f)

        root_node = self._do_second_pass(parsed_cuba, parsed_metadata)

        return root_node

    def _do_second_pass(self, parsed_cuba, parsed_metadata):
        """Creates a linkage, second pass tree from the raw nodes.
        and returns the final parse tree.

        Parameters
        ----------

        parsed_cuba: nodes.File
            the result of parsing cuba.yml file

        parsed_metadata: nodes.File
            the result of parsing simphony_metadata.yml

        Returns
        -------
        an Ontology node, properly filled in.
        """

        if parsed_cuba.header.version != parsed_metadata.header.version:
            raise ParsingError("Mismatched versions between cuba and "
                               "metadata file.")

        ontology = nodes.Ontology()
        ontology.purpose = parsed_metadata.header.purpose
        ontology.resources = parsed_cuba.header.resources
        ontology.resources.update(parsed_metadata.header.resources)

        cuba_symtable, cuds_symtable = build_symbol_tables(
            parsed_cuba,
            parsed_metadata
        )
        ontology.data_types = list(cuba_symtable.values())

        # Build the tree, and in the meantime run additional checks
        root = None

        for entry in parsed_metadata.entries.values():
            cur_name = with_cuba_prefix(entry.name)
            cur_item = cuds_symtable[cur_name]

            if entry.parent is None:
                cur_item.parent = None
                if root is not None:
                    raise ParsingError("Found two CUDS items with no parent "
                                       "specification (hierarchy roots)")
                root = cur_item
            else:
                parent_name = with_cuba_prefix(entry.parent)
                parent_item = cuds_symtable[parent_name]
                cur_item.parent = parent_item
                parent_item.children.append(cur_item)

        # We have the tree. Store it.
        ontology.root_cuds_item = root

        check_item_tree(ontology, cuba_symtable, cuds_symtable)

        return ontology


def build_symbol_tables(parsed_cuba, parsed_metadata):
    """Builds a symbol table, extracting the relevant symbols and their
    correspondence from the parsed information.
    Note that the symbol table is populated by high level nodes, but
    their linkage won't be done until later, when all nodes have been
    created."""
    cuba_symtable = {}
    # Extract the data types
    for entry in parsed_cuba.entries.values():
        data_type = cuba_data_type_from_cuba_entry(entry)
        cuba_symtable[data_type.name] = data_type

    # Extract the CUDS Item, still not linked
    cuds_symtable = {}
    for entry in parsed_metadata.entries.values():
        # check if no duplication exists between the CUBA and the CUDS.
        if entry.name in cuba_symtable:
            raise ParsingError("Common key found between CUBA and "
                               "CUDS items: {}".format(entry.name))
        item = cuds_item_from_cuds_entry(entry)
        cuds_symtable[item.name] = item

    return cuba_symtable, cuds_symtable


def check_item_tree(ontology, cuba_symtable, cuds_symtable):
    """Performs a check of the whole item tree."""
    # we need a stack for frames to check the consistency across the
    # hierarchy of names. Each stack frame is a tuple of two sets,
    # containing the found property names. The first set contains fixed
    # property names (lowercase). The second the variable property names
    # (cuba keys). The sets are cumulative (meaning, they contain what
    # is found and the current level, _and_ what was found at the lower one
    stack = []
    FIXED_IDX = 0
    VARIABLE_IDX = 1
    for item, level in utils.traverse(ontology.root_cuds_item):
        stack = stack[:level]

        if len(stack) == 0:
            cur_frame = (set(), set())
        else:
            cur_frame = (set(stack[-1][FIXED_IDX]),
                         set(stack[-1][VARIABLE_IDX]))

        stack.append(cur_frame)

        # collect the new names
        for prop_name, prop in item.properties.items():
            if isinstance(prop, VariablePropertyEntry):
                # Check if the current variable properties are referring to
                # something that is undefined
                if not (prop_name in cuds_symtable or
                        prop_name in cuba_symtable):
                    raise ParsingError(
                        "Property key {} of item {} is not"
                        " defined anywhere".format(prop_name, item.name))

                # Presence of the same name is ok. We allow overriding
                cur_frame[VARIABLE_IDX].add(prop_name)

            elif isinstance(prop, FixedPropertyEntry):
                cur_frame[FIXED_IDX].add(prop_name)

            else:
                # This should never occur.
                raise RuntimeError("Found unrecognized object "
                                   "{}".format(prop))

        # Now that we collected all names, we cross check
        # for a name clash between a lowercase property
        # and an cuba key property after "lowercase-ization"

        check_name_clash(item.name,
                         cur_frame[FIXED_IDX],
                         cur_frame[VARIABLE_IDX])


def check_name_clash(item_name, fixed_names, variable_names):
    """Checks name clashes between properties"""
    # not using intersection. We want to return a meaningful message.
    for name in variable_names:
        transformed_name = utils.cuba_key_to_property_name(name)

        if transformed_name in fixed_names:
            raise ParsingError(
                "Variable property {} on item {} "
                "clashes with fixed property {} in "
                "its hierarchy".format(
                    name, item_name, transformed_name))


def cuds_item_from_cuds_entry(cuds_entry):
    """Converts a CUDSEntry into a CUDSItem node,
    adjusting for the differences in data representation.
    Note that the resulting CUDSItem is not linked yet,
    hence its parent is None"""
    if not isinstance(cuds_entry, CUDSEntry):
        raise TypeError("cuds_entry must be a CUDSEntry")

    item = CUDSItem(
        name=with_cuba_prefix(cuds_entry.name),
    )

    properties = {}
    for prop_entry in cuds_entry.property_entries.values():
        prop = property_entry_to_property(prop_entry, item)
        properties[prop.name] = prop

    item.properties = properties
    return item


def property_entry_to_property(prop_entry, item):
    """Converts a PropertyEntry to a Property, copying the
    relevant information. It also performs linkage against the
    containing item.
    """
    if isinstance(prop_entry, FixedPropertyEntry):
        prop = FixedProperty(name=prop_entry.name,
                             scope=prop_entry.scope,
                             default=prop_entry.default)
    elif isinstance(prop_entry, VariablePropertyEntry):
        prop = VariableProperty(name=prop_entry.name,
                                scope=prop_entry.scope,
                                shape=prop_entry.shape,
                                default=prop_entry.default
                                )
    else:
        raise TypeError("Unrecognised prop_entry type")

    prop.item = item
    return prop


def cuba_data_type_from_cuba_entry(cuba_entry):
    """Converts the CUBAEntry into a CUBADataType node,
    adjusting for the differences in data representation and
    enforced format."""
    if not isinstance(cuba_entry, CUBAEntry):
        raise TypeError("cuba_entry must be a CUBAEntry")

    d = traits_as_dict(cuba_entry)
    d["name"] = with_cuba_prefix(d["name"])

    return CUBADataType(**d)


def traits_as_dict(instance):
    """Converts the traits into a dictionary keyed over the trait names."""
    d = {}
    for name in instance.editable_traits():
        value = getattr(instance, name)
        d[name] = value

    return d
