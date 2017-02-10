import unittest

from simphony_metaparser.nodes import CUDSItem, FixedProperty, VariableProperty
from traits.api import TraitError


class TestNodes(unittest.TestCase):
    def test_fixed_property_init(self):
        item = CUDSItem(name="CUBA.ITEM")
        # Check if it just instantiates appropriately
        FixedProperty(
            name="foo",
            scope="CUBA.USER",
            default=[1],
            item=item,
        )

        # no default for a system property
        with self.assertRaises(TraitError):
            FixedProperty(
                name="foo",
                scope="CUBA.SYSTEM",
                default=[1],
                item=item,
            )

    def test_variable_property_init(self):
        item = CUDSItem(name="CUBA.ITEM")
        # Check if it just instantiates appropriately
        VariableProperty(
            name="CUBA.FOO",
            scope="CUBA.USER",
            shape=[1],
            default=[1],
            item=item,
        )

        # Invalid name
        with self.assertRaises(TraitError):
            VariableProperty(
                name="xxx",
                scope="CUBA.USER",
                shape=[1],
                default=[1],
                item=item,
            )
