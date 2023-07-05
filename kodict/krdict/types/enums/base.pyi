from collections.abc import ItemsView
from enum import Enum
from typing import Any, Dict, Generic, Optional, Type, TypeVar, Union, overload

T = TypeVar('T')
EnumType = TypeVar('EnumType', bound='EnumBase')
UnderlyingType = TypeVar('UnderlyingType')

class EnumBase(Generic[UnderlyingType]):
    __aliases__: Dict[str, UnderlyingType]

    @classmethod
    @property
    def aliases(cls) -> ItemsView[str, UnderlyingType]: ...

    @overload
    @classmethod
    def get(cls: Type[EnumType], key: Any) -> Optional[EnumType]: ...

    @overload
    @classmethod
    def get(cls: Type[EnumType], key: Any, default: T) -> Union[EnumType, T]: ...

    @overload
    @classmethod
    def get_value(cls: Type[EnumType], key: Any) -> Optional[UnderlyingType]: ...

    @overload
    @classmethod
    def get_value(cls: Type[EnumType], key: Any, default: T) -> Union[UnderlyingType, T]: ...

class IntEnum(int, EnumBase[int], Enum):
    pass

class StrEnum(str, EnumBase[str], Enum):
    pass
