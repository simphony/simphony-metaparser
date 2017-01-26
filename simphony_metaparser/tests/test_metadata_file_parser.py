import os
import six
import unittest
from simphony_metaparser.metadata_file_parser import (
    MetadataFileParser)

TEMPLATE = """
---
VERSION: "1.0"

CUDS: Common Universal Data Structure

Purpose: CUDS provides

Resources:
  CUDS 1.0 (1st Edition): http://simphony.eu/cuds/1.0/  # does not exist
  CUDS Issues Page: https://github.com/simphony/simphony-metadata/issues
  CUDS Mailing List: simphony-ssb@fraunhofer.de
  CUDS Reference Parser: https://github.com/simphony/simphony-metadata/cparser

CUDS_KEYS:
  CUDS_ITEM:
    definition: Root of all CUDS types
    parent:
    CUBA.t UUID:
      scope: CUBA.SYSTEM
    data:
      scope: CUBA.SYSTEM

  CUDS_COMPONENT:
    definition: Base data type for the CUDS components
    parent: CUBA.CUDS_ITEM
    CUBA.DESCRIPTION:
      default: ""
      scope: CUBA.USER
    CUBA.NAME:
      default: ""
      scope: CUBA.USER

  COMPUTATIONAL_MODEL:
    definition: Model category according to the RoMM
    parent: CUBA.CUDS_COMPONENT

  ELECTRONIC:
    definition: Electronic model category according to the RoMM
    parent: CUBA.COMPUTATIONAL_MODEL

  ATOMISTIC:
    definition: Atomistic model category according to the RoMM
    parent: CUBA.COMPUTATIONAL_MODEL

  MESOSCOPIC:
    definition: Mesoscopic model category according to the RoMM
    parent: CUBA.COMPUTATIONAL_MODEL

  CONTINUUM:
    definition: Continuum model category according to the RoMM
    parent: CUBA.COMPUTATIONAL_MODEL

  MODEL_EQUATION:
    definition: The model equations are represented by all physics equations
    models: []
    parent: CUBA.CUDS_COMPONENT
    variables: []

  PHYSICS_EQUATION:
    definition: Physics equation
    parent: CUBA.MODEL_EQUATION
"""


class TestMetadataFileParser(unittest.TestCase):
    def setUp(self):
        self.yamldir = os.path.join(
            os.path.dirname(__file__),
            'fixtures',
            'yaml_files')
        self.parser = MetadataFileParser()

    def test_parse_metadata_file(self):
        with open(os.path.join(self.yamldir, "simphony_metadata.yml")) as f:
            file = self.parser.parse(f)
        self.assertEqual(len(file.entries), 99)

    def test_parsing_template(self):
        content = six.StringIO(TEMPLATE)
        root = self.parser.parse(content)

        self.assertEqual(root.header.version, "1.0")
        self.assertEqual(root.header.purpose, "CUDS provides")
        self.assertEqual(root.header.type, "CUDS")
        self.assertEqual(len(root.entries), 9)
        self.assertEqual(len(root.entries["CUDS_ITEM"].property_entries), 3)
        self.assertEqual(root.entries["CUDS_ITEM"].parent, None)
        self.assertEqual(root.entries["CUDS_COMPONENT"].parent,
                         "CUBA.CUDS_ITEM")
