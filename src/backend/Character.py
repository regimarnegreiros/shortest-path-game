from __future__ import annotations
from dataclasses import dataclass
from types import NoneType

@dataclass
class Character:
    id: int
    name: str
    images: list[str]

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return self.name

    def __eq__(self, char: Character | str | int) -> bool:
        if not isinstance(char, (Character, str, int, NoneType)):
            raise TypeError(f"Unable to compare to {type(char)}")

        if isinstance(char, str):
            return char == self.name
        elif isinstance(char, int):
            return char == self.id
        elif isinstance(char, NoneType):
            return False
        else:
            return (self.id, self.name) == (char.id, char.name)

    def __hash__(self) -> int:
        return hash((self.id, self.name))

if __name__ == "__main__":
    a = Character(1, "a", ["a"])
    print(a == None)