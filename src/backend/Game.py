import os
from Graph import CharacterGraph
from Character import Character
from random import shuffle, choice

class Game:
    def __init__(self, graph: CharacterGraph, max_choices: int = None):
        self.cgraph: CharacterGraph = graph

        self.initial: Character = self.set_initial()
        self.current: Character = self.initial
        self.destination: Character = self.set_destination()
        self.path: list[Character] = [self.initial]

        self.choices_count: int = 0
        self.max_choices: int | None = max_choices  # None = ilimitado

        self.game_over: bool = False
        self.win: bool = False
        self.loss: bool = False

    def set_initial(self) -> Character:
        """Define e retorna o personagem inicial"""
        while True:
            char = self.cgraph.rand_chars(k=1)[0]
            if self.cgraph.get_top_connections(char, 5) not in (None, []):
                return char

    def set_destination(self) -> Character:
        """Define e retorna o personagem de destino"""
        while True:
            visited = []
            number_of_choises = 50
            number_of_neighbors = 5

            destination = choice(self.cgraph.get_top_connections(self.initial.name, number_of_neighbors))[0]
            print(destination)

            repeated = 0
            while number_of_choises >= 0 and repeated < 10:
                opt_num = number_of_neighbors
                while opt_num < 15:
                    options = self.cgraph.get_top_connections(destination, opt_num)
                    available = [opt[0] for opt in options if opt[0] not in visited]

                    if available:
                        destination = choice(available)
                        visited.append(destination)
                        break

                    opt_num += 3
                    print('loop', opt_num)

                if not available:
                    destination = choice(self.cgraph.get_top_connections(destination, number_of_neighbors + 5))[0]
                    number_of_choises += 2
                    print("\033[91mTEVE QUE REPETIR\033[0m")
                    repeated += 1

                
                number_of_choises -= 1
                print(destination, number_of_choises)

            if len(self.cgraph.distance(self.initial.name, destination)) > 3:
                return destination

    def check_end_game(self) -> bool:
        """
        Verifica se o jogo terminou (vitória ou derrota) e atualiza os estados.
        Retorna True se o jogo acabou, False caso contrário.
        """
        if self.current == self.destination:
            # Condição de VITÓRIA
            self.game_over = self.win = True
            self.loss = False

        elif (self.max_choices is not None and 
              self.choices_count >= self.max_choices):
            # Condição de DERROTA por limite de escolhas
            self.game_over = self.loss = True
            self.win = False

        return self.game_over

    def choose(self, id: int) -> None:
        """
        Atualiza o personagem atual.
        Verifica se o jogo terminou.
        Incrementa contador de escolhas.
        """

        self.current = self.cgraph.search(id)
        self.choices_count += 1
        self.path.append(self.current)
        self.check_end_game()

    def options(self, k: int = 5, max_c: int = 10) -> list[Character] | list:
            """Retorna até `k` de `max_c` personagens vizinhos ao atual"""
            if k > max_c:
                return list()

            top_neighbors: list | None = (self.cgraph.get_top_connections(
                                        target_character=self.current.name,
                                        top_n=max_c))
            if not top_neighbors:
                return list()

            # Evita personagens já visitados
            count: int = 0
            characters: list[Character] = [neighbor[0] for neighbor in top_neighbors]
            for done in self.path:
                if done in characters:
                    count += 1

            top_neighbors = (self.cgraph.get_top_connections(
                                target_character=self.current.name,
                                top_n=max_c + count))

            characters = [neighbor[0] for neighbor in top_neighbors]
            for done in self.path:
                if done in characters:
                    characters.remove(done)

            print("Proximos do atual:")
            for i, (name, score) in enumerate(top_neighbors, start=1):
                print(f"{i:2}. {str(name):<20} {score:.3f}")

            print("Próximos do destino:")
            for i, (name, score) in enumerate(self.cgraph.get_top_connections(self.destination.name), start=1):
                print(f"{i:2}. {str(name):<20} {score:.3f}")

            shuffle(characters)

            shortest: tuple[Character] | None = self.cgraph.distance(self.current, self.destination)

            if shortest and len(shortest) > 1:
                if shortest[1] in characters:
                    characters.remove(shortest[1])

                characters.insert(0, shortest[1])

            if self.destination in characters:
                characters.remove(self.destination)
                characters.insert(0, self.destination)

            characters = characters[:k]

            shuffle(characters)

            print(self.cgraph.distance(self.current.name, self.destination.name))

            return characters


# Inicializa a classe com o arquivo JSON
BASE_DIR: str = os.path.dirname(os.path.abspath(__file__))
json_path: str = os.path.join(BASE_DIR, 'data', 'characters.json')
character_graph: CharacterGraph = CharacterGraph(json_path)

# Salva o grafo ponderado
output_dir: str = os.path.join(BASE_DIR, 'data', 'graph')
os.makedirs(output_dir, exist_ok=True)
graph_path: str = os.path.join(output_dir, 'naruto_relationships.gml')
character_graph.save_graph(graph_path)
