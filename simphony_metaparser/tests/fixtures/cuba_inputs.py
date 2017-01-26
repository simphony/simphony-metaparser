def header():
    return """
---
VERSION: "1.0"

CUBA: Common Unified Base Attributes

Purpose: CUBA provides the most primitive definitions used in the SimPhoNy metadata schema
"""


def cuba_keys():
    return """
CUBA_KEYS:

  UID:
    definition: Universal unique id represented as a hex string size 32
    length: 32
    type: string

  POSITION:
    definition: Position of a point or node or atom
    shape: [3]
    type: double

  STATUS:
    definition: Status of a point or node
    shape: [1]
    type: integer

  EXTERNAL_FORCING:
    definition: Toggle for an external force
    shape: [1]
    type: boolean

  VECTOR:
    definition: A vector in 3D geometric space
    shape: [3]
    type: double

  THERMODYNAMIC_ENSEMBLE:
    definition: Thermodynamic ensemble
    type: string
    length: 128
"""


def sane_file():
    return header()+cuba_keys()


def rogue_root_entry():
    return header() + """
whatever: boom
    """+cuba_keys()


def unrecognized_version():
    return """
---
VERSION: "1.1"

CUBA: Common Unified Base Attributes

""" + cuba_keys()


def missing_version():
    return """
---
CUBA: Common Unified Base Attributes

""" + cuba_keys()


