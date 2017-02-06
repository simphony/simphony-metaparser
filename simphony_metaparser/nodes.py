from traits.api import (
    HasStrictTraits, TraitError, String, Enum, Str, Dict, List, Int,
    Either, Any, Instance, Property)

from .utils import with_cuba_prefix
from .flags import NoDefault


CUBAKey = String(regex="^[A-Z][A-Z0-9_]+$")
QualifiedCUBAKey = String(regex="^CUBA\.[A-Z][A-Z0-9_]+$")
FixedPropertyKey = String(regex="^[a-z][a-z0-9_]+$")
Version = String(regex="^\d+\.\d+$")
Scope = Enum("CUBA.USER", "CUBA.SYSTEM")

# --------------------------------------------------------
# Low level nodes. they come out of the first parsing pass
# --------------------------------------------------------


class FileHeaderInfo(HasStrictTraits):
    """Represents the file header information"""
    type = Enum("CUBA", "CUDS")
    version = Version()
    purpose = Str()
    resources = Dict()


class CUBAEntry(HasStrictTraits):
    """Represents a CUBA entry"""
    name = CUBAKey()
    type = Enum('string', 'double', 'integer', 'boolean')

    definition = Str()
    shape = List(Int)
    length = Property()
    _length = Either(None, Int)

    def __init__(self, name, type, *args, **kwargs):
        self.name = name
        self.type = type
        super(CUBAEntry, self).__init__(*args, **kwargs)

    def _get_length(self):
        return self._length

    def _set_length(self, length):
        self._length = length

    def _validate_length(self, length):
        if self.type == "string" and length is None:
            raise TraitError("The CUBA entry is a string, "
                             "and requires a length")
        elif self.type != "string" and length is not None:
            raise TraitError("The CUBA entry is not a string, "
                             "and length must be None")
        return length


class FixedPropertyEntry(HasStrictTraits):
    """Represents the raw data of a property before the linkage step"""
    name = FixedPropertyKey()
    scope = Scope()
    default = Property()
    _default = Any(NoDefault)

    def __init__(self, name, scope, default):
        super(FixedPropertyEntry, self).__init__()
        self.name = name
        self.scope = scope
        self.default = default

    def _get_default(self):
        return self._default

    def _set_default(self, default):
        self._default = default

    def _validate_default(self, default):
        if self.scope == "CUBA.SYSTEM" and default != NoDefault:
            raise TraitError("Cannot specify default for CUBA.SYSTEM "
                             "fixed property")
        elif self.scope == "CUBA.USER" and default == NoDefault:
            raise TraitError("Missing default for CUBA.USER "
                             "fixed property")
        return default


class VariablePropertyEntry(HasStrictTraits):
    """Represents the raw data of a property before the linkage step"""
    name = QualifiedCUBAKey()
    scope = Scope()
    default = Property()
    shape = List(Either(Int, None))

    _default = Any(NoDefault)

    def __init__(self, name, scope, shape, default):
        super(VariablePropertyEntry, self).__init__()
        self.name = name
        self.scope = scope
        self.shape = shape
        self.default = default

    def _get_default(self):
        return self._default

    def _set_default(self, default):
        self._default = default

    def _validate_default(self, default):
        if self.scope == "CUBA.SYSTEM" and default != NoDefault:
            raise TraitError("Cannot specify default for CUBA.SYSTEM "
                             "variable property")
        return default


class CUDSEntry(HasStrictTraits):
    """Represents the raw data of a concept before the linkage step"""
    name = CUBAKey()
    parent = Either(QualifiedCUBAKey(), None)
    # Must be a dict. No order in what we get from the file.
    property_entries = Dict(Either(FixedPropertyKey, QualifiedCUBAKey),
                            Either(FixedPropertyEntry, VariablePropertyEntry))

    def __init__(self, name, parent, *args, **kwargs):
        super(CUDSEntry, self).__init__(*args, **kwargs)
        self.name = name
        self.parent = parent


class File(HasStrictTraits):
    """Represents the root node"""
    name = Str("/")
    path = Str("/")
    header = Instance(FileHeaderInfo)

    # Must be a dict because we don't have any order in what we get from
    # the file
    entries = Either(Dict(Str, CUBAEntry), Dict(Str, CUDSEntry))


class DirectoryRoot(HasStrictTraits):
    """Root object for the result of the parsing from the two files."""
    cuba_file = Instance(File)
    cuds_file = Instance(File)


# --------------------------------------------------
# High level nodes, they come out of the second pass
# Note that the second pass tree contains a mixture
# of second pass nodes and first pass nodes, when
# appropriate
# --------------------------------------------------

class CUDSItem(HasStrictTraits):
    """A high level node representing a concept that has
    dependencies, an identity and properties.
    """
    name = QualifiedCUBAKey()
    parent = Instance("CUDSItem")
    children = List(Instance("CUDSItem"))
    property_entries = Dict(Str,
                            Either(FixedPropertyEntry, VariablePropertyEntry))

    @classmethod
    def from_cuds_entry(cls, cuds_entry):
        if not isinstance(cuds_entry, CUDSEntry):
            raise TypeError("cuba_entry must be a CUBAEntry")

        d = {}

        for name in cuds_entry.editable_traits():
            value = getattr(cuds_entry, name)
            if name == "name":
                value = with_cuba_prefix(value)
            elif name == "parent":
                continue

            d[name] = value

        return cls(**d)


class CUBADataType(CUBAEntry):
    """A high level node representing a value with no dependencies."""
    name = QualifiedCUBAKey()

    @classmethod
    def from_cuba_entry(cls, cuba_entry):
        if not isinstance(cuba_entry, CUBAEntry):
            raise TypeError("cuba_entry must be a CUBAEntry")

        d = {}

        for name in cuba_entry.editable_traits():
            value = getattr(cuba_entry, name)
            if name == "name":
                value = with_cuba_prefix(value)
            d[name] = value

        return cls(**d)


class Ontology(HasStrictTraits):
    """Our overall model, containing the entities that represent our
    world description"""
    purpose = Str()
    resources = Dict()
    data_types = List(CUBADataType)
    root_cuds_item = Instance(CUDSItem)
