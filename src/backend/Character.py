from dataclasses import dataclass

@dataclass
class Character:
    id: int
    name: str
    images: list[str]

    def __str__(self):
        return self.name
    
    def __repr__(self):
        return self.name
