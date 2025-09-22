import os
import json
import networkx as nx

class CharacterGraph:
    def __init__(self, json_file):
        self.json_file = json_file
        self.weights = {
            'family': 3,
            'clan': 1,
            'same_primary_team': 5,
            'share_primary_team': 3,
            'share_team': 0.5,
        }
        self.graph = nx.Graph()
        self.characters_data = self.load_characters()
        self.build_graph()

    def load_characters(self):
        """Carrega os dados do arquivo JSON."""
        try:
            with open(self.json_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Erro: O arquivo '{self.json_file}' não foi encontrado.")
            exit()

    def to_list(self, value):
        """Função auxiliar para garantir que o valor seja sempre uma lista."""
        if value is None:
            return []
        if isinstance(value, list):
            return value
        return [value]

    def build_graph(self):
        """Constrói o grafo de personagens e suas relações ponderadas."""
        # Adiciona nós
        for character in self.characters_data:
            if 'name' in character:
                self.graph.add_node(character['name'])

        # Adiciona arestas com a nova lógica de ponderação
        for i, char1 in enumerate(self.characters_data):
            for j in range(i + 1, len(self.characters_data)):
                char2 = self.characters_data[j]

                if 'name' not in char1 or 'name' not in char2:
                    continue

                name1 = char1['name']
                name2 = char2['name']

                personal1 = char1.get('personal', {})
                personal2 = char2.get('personal', {})

                if not isinstance(personal1, dict) or not isinstance(personal2, dict):
                    continue

                total_weight = 0
                relations = []

                # 1. Relação por Família
                is_family = (char1.get('family') and isinstance(char1.get('family'), dict) and name2 in char1['family'].values()) or \
                            (char2.get('family') and isinstance(char2.get('family'), dict) and name1 in char2['family'].values())
                if is_family:
                    total_weight += self.weights['family']
                    relations.append('family')

                # 2. Relação por Clã
                clans1 = self.to_list(personal1.get('clan'))
                clans2 = self.to_list(personal2.get('clan'))
                if clans1 and clans2 and set(clans1).intersection(set(clans2)):
                    total_weight += self.weights['clan']
                    relations.append('clan')

                # 3. Relação por Equipe (Lógica de Posição e Primária)
                teams1 = self.to_list(personal1.get('team'))
                teams2 = self.to_list(personal2.get('team'))

                common_teams = set(teams1).intersection(set(teams2))

                if common_teams:
                    if 'team' not in relations:
                        relations.append('team')

                    team_weight = 0

                    # Identifica a equipe primária de cada um
                    primary_team1 = teams1[0] if teams1 else None
                    primary_team2 = teams2[0] if teams2 else None

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

                # Adicionar a aresta se houver qualquer relação
                if total_weight > 0:
                    relation_label = ', '.join(sorted(relations))  # Ordena para consistência
                    self.graph.add_edge(name1, name2, relation=relation_label, weight=total_weight)

    def save_graph(self, filename):
        """Salva o grafo ponderado em um arquivo GML."""
        nx.write_gml(self.graph, filename)
        print(f"Grafo ponderado criado e salvo como '{filename}'")
        print(f"O grafo tem {self.graph.number_of_nodes()} nós (personagens) e {self.graph.number_of_edges()} arestas (relações).")

    def get_top_connections(self, target_character, top_n=10):
        """Encontra e lista as principais conexões de um personagem."""
        if self.graph.has_node(target_character):
            character_connections = []
            for neighbor in self.graph.neighbors(target_character):
                edge_data = self.graph.get_edge_data(target_character, neighbor)
                weight = edge_data.get('weight', 0)
                character_connections.append((neighbor, weight))

            # Ordena a lista pelo peso em ordem decrescente
            sorted_connections = sorted(character_connections, key=lambda item: item[1], reverse=True)

            # Pega os top_n primeiros
            top_connections = sorted_connections[:top_n]

            print(f"\n--- As {top_n} principais conexões de {target_character} ---")
            for i, (character, weight) in enumerate(top_connections, 1):
                print(f"{i}. {character} (Peso Total da Relação: {weight})")
        else:
            print(f"\nPersonagem '{target_character}' não encontrado no grafo.")


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