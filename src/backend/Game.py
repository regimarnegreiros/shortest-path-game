import os
from Graph import CharacterGraph
from Character import Character
from random import choices

class Game:
    def __init__(self, graph: CharacterGraph, max_choices: int = None):
        self.cgraph: CharacterGraph = graph
        self.initial: Character = self.set_initial()
        self.current: Character = self.initial
        self.destination: Character = self.set_destination()
        self.choices_count: int = 0
        self.max_choices: int | None = max_choices  # None = ilimitado

    def set_initial(self) -> Character:
        """Define e retorna o personagem inicial"""
        pass

    def set_destination(self) -> Character:
        """Define e retorna o personagem de destino"""
        pass

    def choose(self, id: int) -> bool:
        """
        Atualiza o personagem atual.
        Incrementa contador de escolhas.
        Retorna True se chegou ao destino, senão False.
        """
        if self.max_choices is not None and self.choices_count >= self.max_choices:
            raise RuntimeError("Número máximo de escolhas atingido.")
        self.choices_count += 1
        pass

# Inicializa a classe com o arquivo JSON
BASE_DIR: str = os.path.dirname(os.path.abspath(__file__))
json_path: str = os.path.join(BASE_DIR, 'data', 'characters.json')
character_graph: CharacterGraph = CharacterGraph(json_path)

# Salva o grafo ponderado
output_dir: str = os.path.join(BASE_DIR, 'data', 'graph')
os.makedirs(output_dir, exist_ok=True)
graph_path: str = os.path.join(output_dir, 'naruto_relationships.gml')
character_graph.save_graph(graph_path)

game_instance: Game = Game(character_graph)