import enum
from typing import Callable, Generic, NoReturn, Optional, Tuple, TypeVar, Any

T = TypeVar("T")
E = TypeVar("E", bound=Exception)

Result = Tuple[T, Optional[E]]

ResultWithErr = Tuple[T, Optional[Exception]]


class Ok(Generic[T, E]):
    _value: T
    __match_args__ = ("_value",)

    def __init__(self, value: T):
        self._value = value

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Ok):
            return self._value == other._value  # type: ignore
        return False

    def unwrap(self) -> T:
        return self._value

    def unwrap_or(self, default: T) -> T:
        return self.unwrap()

    def unwrap_or_else(self, op: Callable[[E], T]) -> T:
        return self.unwrap()

    def __repr__(self) -> str:
        return f"Ok({repr(self._value)})"


class Err(Generic[T, E]):
    _err: E
    __match_args__ = ("_err",)

    def __init__(self, err: E):
        self._err = err

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Err):
            return self._err == other._err  # type: ignore
        return False

    def unwrap(self) -> NoReturn:
        raise self._err

    def unwrap_or(self, default: T) -> T:
        return default

    def unwrap_or_else(self, op: Callable[[E], T]) -> T:
        return op(self._err)

    def __repr__(self) -> str:
        return f"Err({repr(self._err)})"
