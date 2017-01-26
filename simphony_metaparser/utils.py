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


def traverse(node, level=0):
    """Traverses the tree depth first.
    yields the node and the level at which the node is found.
    """
    yield node, level
    if hasattr(node, "children"):
        for c in node.children:
            for sub, sublevel in traverse(c, level+1):
                yield sub, sublevel


def cuba_key_to_property_name(string):
    """Converts a cuba key in the associated property name"""
    return without_cuba_prefix(string).lower()
