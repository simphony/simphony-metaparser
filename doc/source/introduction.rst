Introduction
============

The simphony-metaparser library provides parsers for the simphony-metadata format.
This format, as of version 1.0, is composed of two files, ``cuba.yml`` and ``simphony_metadata.yml``.
The parser class ``YamlDirParser`` specifically looks for these two files in the specified directory.

The ``YamlDirParser`` class is the main entry point for parsing the contents. It accepts the above mentioned
directory and returns an ``Ontology`` node, containing:

    - A few metadata (purpose of the file, resources)_
    - A list of ``CUBADataType`` nodes, which specify the CUBA types.
    - A tree of ``CUDSItem`` starting from the root node of the hierarchy of CUDSItems. 
      Each node of the tree then contains additional nodes for the associated properties.

This library is currently used by:
   
    - simphony-metaedit: GUI visualizer and editor for the simphony-metadata files.
    - simphony-common generator: used to generate the python classes from the meta files.


