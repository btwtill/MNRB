from enum import Enum

class AttributeType(Enum):
    """The attribute types a component can expose.

    Restricted to what Maya's `addAttr -proxy` actually supports, because the
    Attribute Editor's whole point is proxying these onto a control. String,
    matrix and message attributes are deliberately absent - they can't be
    proxied, and would need an add-and-connect fallback instead.

    Values are the strings used in serialization, so they must stay stable.
    """

    BOOL = "bool"
    INT = "int"
    FLOAT = "float"
    ENUM = "enum"

def mapNameToAttributeType(type_name):
    for attribute_type in AttributeType:
        if attribute_type.value == type_name:
            return attribute_type
    return AttributeType.FLOAT
