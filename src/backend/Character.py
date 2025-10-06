from dataclasses import dataclass

@dataclass
class Character:
    id: int
    nome: str
    imagem: list[str]

    def __str__(self):
        return self.nome
    
    def __repr__(self):
        return self.nome
