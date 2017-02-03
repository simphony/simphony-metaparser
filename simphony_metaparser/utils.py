def with_cuba_prefix(string):
    """Adds the CUBA. prefix to the string if not there."""
    if string.startswith("CUBA."):
        return string

    return "CUBA."+string


def without_cuba_prefix(string):
    """Removes the CUBA. prefix to the string if there."""
    if string.startswith("CUBA."):
        return string[5:]

    return string


def traverse(node, _level=0):
    """Traverses the tree depth first.

    Parameters
    ----------
    node: Any
        Any entity that has the "children" property.

    Yields
    ------
    tuple with two elements:
        - the node
        - the level at which the node is found, zero based.
    """
    yield node, _level
    if hasattr(node, "children"):
        for c in node.children:
            for sub, sublevel in traverse(c, _level+1):
                yield sub, sublevel


def traverse_to_root(node):
    """Performs the reverse traversal, from a given node up through the
    hierarchy via the property "parent".
    The last node of the hierarchy has parent equal to None

    Parameters
    ----------
    node: Any
        Anything with the "parent" property.

    Yields
    ------
    nodes through the parent hierarchy until the node whose parent is None
    is found.
    """
    while node is not None:
        yield node
        node = node.parent if hasattr(node, "parent") else None


def cuba_key_to_property_name(string):
    """Converts a cuba key in the associated property name"""
    return without_cuba_prefix(string).lower()
