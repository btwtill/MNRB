"""Node categories for the attribute canvas.

Deliberately a leaf module with no imports of its own. These used to live in
attribute_Editor_conf, but conf ends by importing every node module (that is how
they register), so anything conf reaches cannot import conf back - the graphics
node did, and the cycle broke the whole tab on load.
"""

#something a value comes from
CATEGORY_SOURCE = "source"
#something a value lands on
CATEGORY_TARGET = "target"
#something that transforms a value on the way through
CATEGORY_OPERATOR = "operator"
