import os
import json
import networkx as nx
from typing import Any
from Character import Character
from networkx.readwrite.gml import read_gml
from random import choice

def to_list(value) -> list:
    """Função auxiliar para garantir que o valor seja sempre uma lista."""
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]

class CharacterGraph:
    def __init__(self, json_file: str):
        self.json_file: str = json_file
        self.weights: dict[str, int] = {
            'family': 3,
            'clan': 1,
            'same_primary_team': 5,
            'share_primary_team': 3,
            'share_team': 0.5,
            'anime_debut': 3,
            'partner': 5,
            'affiliation': 1,
        }
        self.graph: nx.Graph = nx.Graph()
        self.characters_data: list[dict[str, Any]] = self.__load_characters()
        self.__build_graph()

    def __load_characters(self) -> list[dict[str, Any]]:
        """Carrega os dados do arquivo JSON."""
        try:
            with open(self.json_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Erro: O arquivo '{self.json_file}' não foi encontrado.")
            exit()

    def __build_graph(self):
        """Constrói o grafo de personagens e suas relações ponderadas."""
        # Adiciona nós
        for character in self.characters_data:
            # Checa se personagem estreou no Boruto
            anime_debut: str = character.get('debut', {}).get('anime', '')

            if not anime_debut.startswith('Boruto') and "name" in character:
                self.graph.add_node(
                    character['name'], id=character["id"],
                    images=character["images"]
                )

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
                    self.graph.add_edge(name1, name2, relation=relation_label,
                                        weight=total_weight)

    def save_graph(self, filename: str) -> None:
        """Salva o grafo ponderado em um arquivo GML."""
        nx.write_gml(self.graph, filename)
        print(f"Grafo ponderado criado e salvo como '{filename}'")
        print(f"O grafo tem {self.graph.number_of_nodes()} nós (personagens) "
              f"e {self.graph.number_of_edges()} arestas (relações).")

    def get_top_connections(self, target_character, top_n=10) -> list | None:
        """Encontra e lista as principais conexões de um personagem."""
        if not self.graph.has_node(target_character):
            print(f"\nPersonagem '{target_character}' não encontrado no grafo.")
            return None

        character_connections: list = []
        for neighbor in self.graph.neighbors(target_character):
            edge_data = self.graph.get_edge_data(target_character, neighbor)
            weight = edge_data.get('weight', 0)
            character_connections.append((neighbor, weight))

        # Ordena a lista pelo peso em ordem decrescente
        sorted_connections = sorted(character_connections, 
                                    key=lambda item: item[1], reverse=True)

        # Pega os top_n primeiros
        top_connections = sorted_connections[:top_n]

        print(f"\n--- As {top_n} principais conexões de {target_character} ---")
        for i, (character, weight) in enumerate(top_connections, 1):
            print(f"{i}. {character} (Peso Total da Relação: {weight})")

        return top_connections


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
    character_graph.get_top_connections('Gaara')