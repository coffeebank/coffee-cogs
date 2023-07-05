"""
Contains base class for KRDict enumeration helpers.
"""

from enum import Enum

class EnumBase(Enum):
    """Base class for enumerations."""

    __aliases__ = {}

    @classmethod
    @property
    def aliases(cls):
        """The aliases of the enumeration."""
        return cls.__aliases__.items() # pylint: disable=no-member

    @classmethod
    def get(cls, key, default=None):
        """
        Returns the enumeration instance associated with a value,
        or the provided default value if the value is not associated with any enumeration.
        """

        if isinstance(key, cls):
            return cls(key.value)

        if isinstance(key, str):
            literal_value = cls.__aliases__.get(key)

            if literal_value is not None:
                key = literal_value
            else:
                try:
                    return cls[key]
                except KeyError:
                    pass

        try:
            return cls(key)
        except ValueError:
            return default

    @classmethod
    def get_value(cls, key, default=None):
        """
        Returns the enumeration value associated with a value,
        or the provided default value if the value is not associated with any enumeration.
        """

        enum_instance = cls.get(key)
        return enum_instance.value if enum_instance is not None else default

class IntEnum(int, EnumBase): # pylint: disable=invalid-enum-extension
    """Base class for integer-based enumerations."""

class StrEnum(str, EnumBase): # pylint: disable=invalid-enum-extension
    """Base class for string-based enumerations."""

    def __str__(self):
        return Enum.__str__(self)
