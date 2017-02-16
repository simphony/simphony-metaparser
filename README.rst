Simphony-metaparser
===================

A parser library for SimPhoNy metadata files, available at https://github.com/simphony/simphony-metadata
This library is used by both the simphony-common meta generator and by the simphony-metaedit.

Basic usage
-----------

The parser for the file format accepts the path of the directory where the
yaml files reside, and returns a high level data model::

    parser = YamlDirParser()
    data = parser.parse(directory)

The data will now refer to a high level structure ``Ontology``, containing a list of CUBA
data types, and a tree of CUDS items.


Directory structure
-------------------

- simphony_metaparser -- main package content
