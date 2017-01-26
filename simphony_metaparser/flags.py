from traits.api import HasStrictTraits


class NoDefault(HasStrictTraits):
    """A flag value to indicate a lack of specified default.
    Node that this is needed because None could be the default"""
    pass
