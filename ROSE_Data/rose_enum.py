"""Enum handling that survives a shelf Reload.

Every Reload runs importlib.reload over the modules below, which rebuilds each
Enum class as a NEW class object under the same name. Enum members hash and
compare by identity, so a member created before a reload is a different object
from the same-named member after it: `==` returns False and a dict keyed by
members raises KeyError. Which modules are affected depends entirely on the
order of the reload list, so the failures move around as that list is edited.

The values are stable by contract (they are what gets serialized), so anything
that branches on an enum compares values instead of members.
"""

def enumValue(member):
    """The stable string behind an enum member, whichever copy of its class it
    came from. Passing a plain value through is intentional - callers shouldn't
    have to know which of the two they hold."""
    return getattr(member, "value", member)
