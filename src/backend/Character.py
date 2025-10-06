from dataclasses import dataclass
from __future__ import annotations

@dataclass
class Character:
    id: int
    name: str
    images: list[str]

    def __str__(self):
        return self.name
    
    def __repr__(self):
        return self.name
    
    def __eq__(self, char: Character):
        if not isinstance(char, Character):
            raise TypeError("Unable to compare to non-Character")

        return (self.id, self.name) == (char.id, char.name)
