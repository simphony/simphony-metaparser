from traits.api import HasStrictTraits


class _NoDefault(HasStrictTraits):
    """A flag value to indicate a lack of specified default.
    Node that this is needed because None could be the default"""


NoDefault = _NoDefault()
