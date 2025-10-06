from flask import Flask, jsonify, request, session
from Game import Game, character_graph
import uuid
import os


app = Flask(__name__)

# Chave secreta OBRIGATÓRIA para usar sessions (cookies seguros)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', str(uuid.uuid4())) 

# Armazenamento simples no backend para todas as instâncias de jogo.
ACTIVE_GAMES: dict[str, Game] = {}

def get_current_game() -> Game | None:
    """Busca a instância de Game associada ao usuário atual via session."""
    game_id = session.get('game_id')
    if game_id and game_id in ACTIVE_GAMES:
        return ACTIVE_GAMES[game_id]
    return None

def clear_game_state(game_id: str):
    """Remove a instância do jogo do armazenamento do servidor."""
    if game_id in ACTIVE_GAMES:
        del ACTIVE_GAMES[game_id]
        print(f"Jogo {game_id} removido do ACTIVE_GAMES.")

def _get_game_status_data(game: Game, game_id: str) -> dict:
    """Retorna um dicionário JSON completo do estado do jogo."""
    return {
        "game_id": game_id,
        "initial": vars(game.initial) if game.initial else None,
        "current": vars(game.current) if game.current else None,
        "destination": vars(game.destination) if game.destination else None,
        "choices_count": game.choices_count,
        "max_choices": game.max_choices,
        "game_over": game.game_over,
        "win": game.win,
        "loss": game.loss
    }

@app.route("/start", methods=["POST"])
def start_game():
    """
    Inicia um novo jogo.
    """
    # Cria um ID de jogo único
    game_id = str(uuid.uuid4())

    # Cria uma nova instância de jogo
    new_game = Game(character_graph, 30)

    # Armazena a instância no dicionário de jogos ativos
    ACTIVE_GAMES[game_id] = new_game

    # Armazena o ID do jogo na sessão do usuário (cookie)
    session['game_id'] = game_id

    print(ACTIVE_GAMES)

    return jsonify(_get_game_status_data(new_game, game_id))

@app.route("/options", methods=["GET"])
def get_options():
    """Retorna até 5 personagens vizinhos do atual"""
    game = get_current_game()
    if not game:
        return jsonify({"error": "Jogo não iniciado. Chame /start"}), 404
    
    # Verificação de game_over para impedir opções após o fim
    if game.game_over:
        return jsonify({"error": f"O jogo já terminou: {'Vitória' if game.win else 'Derrota'}"}), 400
        
    options = game.options()
    return jsonify([vars(opt) for opt in options])


@app.route("/choose", methods=["POST"])
def choose_character():
    """
    Processa a escolha do próximo personagem, atualiza o estado e limpa o jogo se game_over for True.
    Espera {"id": ...}
    """
    game = get_current_game()
    game_id = session.get('game_id') 

    if not game:
        return jsonify({"error": "Jogo não iniciado. Chame /start"}), 404

    data = request.get_json()
    char_id = data.get("id")

    if char_id is None:
        return jsonify({"error": "ID do personagem ausente"}), 400
    
    try:
        # A função choose atualiza o estado do jogo (current, choices_count, game_over)
        game.choose(char_id) 
        
        # Lógica de Limpeza: Verifica o flag game_over atualizado
        if game.game_over:
            clear_game_state(game_id)
            session.pop('game_id', None)
            
        # Retorna o novo estado completo do jogo
        return jsonify(_get_game_status_data(game, game_id))

    except RuntimeError as e:
        # Erro se tentar jogar após o fim (exceção levantada em Game.choose)
        return jsonify({"runtime error": str(e)}), 400
    except ValueError as e:
        # Erro de personagem não encontrado (exceção levantada em Game.choose)
        return jsonify({"value error": str(e)}), 400
    except TypeError as e:
        # Erro de tipo
        return jsonify({"type error": str(e)}), 400

@app.route("/status", methods=["GET"])
def get_status():
    """Retorna informações do jogo atual"""
    game = get_current_game()
    game_id = session.get('game_id')

    if not game:
        return jsonify({"error": "Nenhum jogo ativo."}), 404
    
    return jsonify(_get_game_status_data(game, game_id))


if __name__ == "__main__":
    app.run(debug=True)
