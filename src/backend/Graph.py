import os
import json
import networkx as nx
from typing import Any
from Character import Character
from random import choices, shuffle
from itertools import groupby
from sys import stderr
from abc import ABC, abstractmethod
from math import inf

def to_list(value: Any) -> list:
    """Função auxiliar para garantir que o valor seja sempre uma lista."""
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]

def minmax_comp(x: int, xmin: int, xmax: int) -> float:
    return 1 - ((x - xmin) / (xmax - xmin))

class AbstractCharacterGraph(ABC):
    def __init__(self, json_file: str, weights: dict[str, float]):
        self.json_file: str = json_file
        self.weights: dict[str, float] = weights
        self.graph: nx.Graph = nx.Graph()
        self.characters_data: list[dict[str, Any]] = self.__load_characters()
        self._build_graph()
        self.__normalize_graph()

    def __load_characters(self) -> list[dict[str, Any]]:
        """Carrega os dados do arquivo JSON."""
        try:
            with open(self.json_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Erro: O arquivo '{self.json_file}' não foi encontrado.",
                  file=stderr)
            exit()

    @abstractmethod
    def _build_graph(self) -> None:
        """Constrói o grafo de personagens e suas relações ponderadas."""

        pass

    def __normalize_graph(self) -> None:
        """
        Normaliza os pesos do grafo usando normalização min-max.
        """

        weights: list[float] = [data[-1]["weight"] for data
                              in self.graph.edges(data=True)]
        min_weight: int = min(weights)
        max_weight: int = max(weights)

        edge: list[Character]
        data: dict[str, str|float]
        for (*edge, data) in self.graph.edges(data=True):
            self.graph.edges[*edge]["weight"] = minmax_comp(
                x=data["weight"], xmin=min_weight, xmax=max_weight
            )

    def save_graph(self, filename: str) -> None:
        """Salva o grafo ponderado em um arquivo GML."""
        nx.write_gml(self.graph, filename, stringizer=lambda char: str(char))

    def get_top_connections(
            self, target_character: Character | str | int,
            top_n: int = 10
        ) -> list[tuple[Character, float]] | None:
        """Encontra e lista as principais conexões de um personagem."""

        if not isinstance(target_character, (Character, int, str)):
            raise TypeError("invalid type for target_character")

        if isinstance(target_character, (str, int)):
            target_character = self.search(target_character)

        if target_character not in self.graph:
            print(f"\nPersonagem '{target_character}' não encontrado no grafo.",
                  file=stderr)
            return None

        character_connections: list[tuple[Character, float]] = []

        neighbor: Character
        for neighbor in self.graph.neighbors(target_character):
            edge_data: dict[str, str | float]
            edge_data = self.graph.get_edge_data(target_character, neighbor)
            weight: float = edge_data.get('weight', 0.0)
            character_connections.append((neighbor, weight))

        # Ordena a lista pelo peso em ordem decrescente
        sorted_connections: list[tuple[Character, float]] = (
            sorted(character_connections, key=lambda item: item[1])
        )

        # Aleatoriza por grupos de mesmo peso
        groups: list[tuple[Character, float]] = []
        for _, group in groupby(sorted_connections, key=lambda x: x[1]):
            g: list[tuple[Character, float]] = list(group)
            shuffle(g)
            groups += g

        sorted_connections = groups

        # Pega os top_n primeiros
        top_connections: list[tuple[Character, float]] = (
            sorted_connections[:min(top_n, len(sorted_connections))]
        )

        return top_connections

    def rand_chars(self, k: int = 1) -> list[Character]:
        """
        Retorna um ou mais personagens aleatórios
        """

        rand_chars: list[Character] = (choices(tuple(self.graph.nodes), k=k))

        return rand_chars

    def search(self, char: Character | int | str) -> Character | None:
        """
        Converte um id ou nome em `Character`

        Args:
            char (Character |int | str):
                o ID (`int`) ou nome (`str`) do personagem, ou ele em si

        Returns:
            `Character`: `Character`, caso o personagem exista no grafo,
            `None` caso contrário

        Raises:
            TypeError: Caso `char` não seja um `int`, `str`, ou `Character`
        """

        if not isinstance(char, (Character, int, str)):
            raise TypeError("invalid type for char")

        data: tuple = tuple(self.graph.nodes)

        if char not in data: return None

        return data[data.index(char)]

    def distance(self, start: Character | int | str,
                 end: Character | int | str) -> tuple[Character] | None:
        """
        Retorna a distância entre dois personagens como uma 
        tuple ordenada de personagens, caso haja um caminho entre eles
        """

        if not isinstance(start, (Character, int, str)):
            raise TypeError("invalid type for start character")

        elif not isinstance(end, (Character, int, str)):
            raise TypeError("invalid type for end character")

        if isinstance(start, (str, int)):
            start = self.search(start)

        if isinstance(end, (str, int)):
            end = self.search(end)

        if not start or not end:
            return None

        type Table = dict[Character, tuple[float, Character | None, bool]]

        if start in (None, "") or end in (None, ""):
            return None

        # Tabela: {Nó: (Custo, Antecessor, Visitado)}
        table: Table = {
            char: ((inf, None, False) if char != start else (0.0, None, False))
            for char in self.graph.nodes
        }

        # Para se chegou no destino ou restam só nós inalcançáveis
        while (start != end and any(vals[0] != inf for vals in table.values()
                                    if not vals[2])):
            min_weight: float = min(vals[0] for vals in table.values()
                                    if not vals[2] and vals[0] != inf)

            # Acha nó não visitado de menor distância
            for (char, vals) in table.items():
                if not vals[2] and vals[0] == min_weight:
                    start = char
                    break

            neighbors = self.graph.edges(start, data=True)

            # Dos vizinhos não visitados, checa menor distância
            edge: tuple[Character, Character, dict[str, str | float]]
            for edge in neighbors:
                neighbor: Character = edge[1]
                if table[neighbor][2]: continue

                dist: float = table[neighbor][0]
                proposed_dist: float = table[start][0] + edge[2]["weight"]

                if proposed_dist < dist:
                    table[neighbor] = (proposed_dist, start, table[neighbor][2])

            table[start] = (table[start][0], table[start][1], True)

        if start != end: return None

        path: list[int | str] = []

        while start:
            path.insert(0, start)
            start = table[start][1]

        return tuple(path)

class CharacterGraph(AbstractCharacterGraph):
    def __init__(self, json_file):
        NARUTO_WEIGHTS: dict[str, float] = {
            'family': 3.0,
            'clan': 1.0,
            'same_primary_team': 5.0,
            'share_primary_team': 3.0,
            'share_team': 0.5,
            'anime_debut': 3.0,
            'partner': 5.0,
            'affiliation': 1.0,
        }

        super().__init__(json_file, NARUTO_WEIGHTS)

    def _build_graph(self):
        # Checa se personagem estreou no Boruto
        self.characters_data = [
            character for character in self.characters_data
            if "Boruto" not in (character.get('debut', {}).get('anime', ''))
            and "name" in character
        ]
        # Adiciona nós
        for character in self.characters_data:
            self.graph.add_node(Character(
                id=character["id"], name=character['name'],
                images=character["images"]
            ))

        # Adiciona arestas com a nova lógica de ponderação
        for i, char1 in enumerate(self.characters_data):
            for j in range(i + 1, len(self.characters_data)):
                char2 = self.characters_data[j]

                if 'name' not in char1 or 'name' not in char2:
                    continue

                name1: str = char1['name']
                name2: str = char2['name']

                personal1: dict | Any = char1.get('personal', {})
                personal2: dict | Any = char2.get('personal', {})

                if not (isinstance(personal1, dict)
                        and isinstance(personal2, dict)):
                    continue

                total_weight: int = 0
                relations: list = []
                c1_family: dict | Any | None = char1.get('family')
                c2_family: dict | Any | None = char2.get('family')

                # 1. Relação por Família
                is_family: bool = ((isinstance(c1_family, dict)
                                     and name2 in char1['family'].values()) or
                                    (isinstance(c2_family, dict)
                                     and name1 in char2['family'].values()))
                if is_family:
                    total_weight += self.weights['family']
                    relations.append('family')

                # 2. Relação por Clã
                clans1: list = to_list(personal1.get('clan'))
                clans2: list = to_list(personal2.get('clan'))

                if set(clans1) & set(clans2):
                    total_weight += self.weights['clan']
                    relations.append('clan')

                # 3. Relação por Parceiro
                partners1: list = to_list(personal1.get('partner'))
                partners2: list = to_list(personal2.get('partner'))

                if (name2 in partners1) or (name1 in partners2):
                    total_weight += self.weights['partner']
                    relations.append('partner')

                # 4. Relação por Equipe (Lógica de Posição e Primária)
                teams1: list = to_list(personal1.get('team'))
                teams2: list = to_list(personal2.get('team'))

                common_teams: set = set(teams1) & set(teams2)

                if common_teams:
                    if 'team' not in relations:
                        relations.append('team')

                    team_weight: int = 0

                    # Identifica a equipe primária de cada um
                    primary_team1: Any | None = teams1[0] if teams1 else None
                    primary_team2: Any | None = teams2[0] if teams2 else None

                    # Regra +3: Mesma equipe primária
                    if primary_team1 and primary_team1 == primary_team2:
                        team_weight += self.weights['same_primary_team']
                        # Remove a equipe processada para não contar novamente
                        common_teams.discard(primary_team1)
                    # Regra +2: Equipe primária de um está na lista do outro
                    else:
                        if primary_team1 and primary_team1 in teams2:
                            team_weight += self.weights['share_primary_team']
                            common_teams.discard(primary_team1)
                        if primary_team2 and primary_team2 in teams1:
                            team_weight += self.weights['share_primary_team']
                            common_teams.discard(primary_team2)

                    # Regra +1: Adiciona 1 para cada outra equipe em comum restante
                    team_weight += self.weights['share_team'] * len(common_teams)

                    total_weight += team_weight

                # 5. Relação por Primeira Aparição (Anime)
                debut1: dict = char1.get('debut', {})
                debut2: dict = char2.get('debut', {})
                anime_debut1: str | None = debut1.get('anime')
                anime_debut2: str | None = debut2.get('anime')

                if anime_debut1 and anime_debut1 == anime_debut2:
                    total_weight += self.weights['anime_debut']
                    relations.append('anime_debut')

                # 6. Relação por Afiliações
                affiliations1: list = to_list(personal1.get('affiliation'))
                affiliations2: list = to_list(personal2.get('affiliation'))
                common_affiliations: set = set(affiliations1) & set(affiliations2)

                if common_affiliations:
                    relations.append('affiliation')
                    affiliation_weight: int = 0

                    for aff in common_affiliations:
                        if aff == "Akatsuki":  # Peso especial para Akatsuki
                            affiliation_weight += 5
                        else:  # Peso padrão para outras afiliações
                            affiliation_weight += 1

                    total_weight += affiliation_weight

                # Adicionar a aresta se houver qualquer relação
                if total_weight > 0:
                    # Ordena para consistência
                    relation_label = ', '.join(sorted(relations))
                    first: Character = Character(
                        id=char1["id"], name=char1["name"],
                        images=char1["images"]
                    )
                    second: Character = Character(
                        id=char2["id"], name=char2["name"],
                        images=char2["images"]
                    )
                    self.graph.add_edge(first, second, relation=relation_label,
                                        weight=total_weight)


if __name__ == "__main__":
    # Inicializa a classe com o arquivo JSON
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(BASE_DIR, 'data', 'characters.json')
    character_graph = CharacterGraph(json_path)

    # Salva o grafo ponderado
    output_dir = os.path.join(BASE_DIR, 'data', 'graph')
    os.makedirs(output_dir, exist_ok=True)
    graph_path = os.path.join(output_dir, 'naruto_relationships.gml')
    character_graph.save_graph(graph_path)

    # Exemplo: Obtém as 10 principais conexões de um personagem
    top = character_graph.get_top_connections('Kabuto Yakushi')
    print(character_graph.distance("Naruto Uzumaki", "Mitsuo"))

    for i, (name, score) in enumerate(top, start=1):
        print(f"{i:2}. {str(name):<20} {score:.3f}")
