from flask import Flask, jsonify, request, session, Blueprint, Response
from Game import Game, character_graph
from Character import Character
from typing import Any
import uuid
# import os


api_bp: Blueprint = Blueprint('api_bp', __name__)

# Armazenamento simples no backend para todas as instâncias de jogo.
ACTIVE_GAMES: dict[str, Game] = {}

def get_current_game() -> Game | None:
    """Busca a instância de Game associada ao usuário atual via session."""
    game_id: str = session.get('game_id')

    if game_id and game_id in ACTIVE_GAMES:
        return ACTIVE_GAMES[game_id]

    return None

def clear_game_state(game_id: str) -> None:
    """Remove a instância do jogo do armazenamento do servidor."""
    if game_id in ACTIVE_GAMES:
        del ACTIVE_GAMES[game_id]
        print(f"Jogo {game_id} removido do ACTIVE_GAMES.")

def _get_game_status_data(game: Game, game_id: str) -> dict[str, Any]:
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
        "loss": game.loss,
        "path": game.path
    }

# @api_bp.before_request
# def restrict_origin():
#     allowed_origins = ["http://localhost:5000"]
#     origin = request.headers.get("Origin")
#     if origin and origin not in allowed_origins:
#         return jsonify({"error": "Origem não autorizada"}), 403

@api_bp.route("/start", methods=["POST"])
def start_game() -> Response:
    """
    Inicia um novo jogo.
    """
    # Cria um ID de jogo único
    game_id: str = str(uuid.uuid4())

    # Cria uma nova instância de jogo
    new_game: Game = Game(character_graph, 15)

    # Armazena a instância no dicionário de jogos ativos
    ACTIVE_GAMES[game_id] = new_game

    # Armazena o ID do jogo na sessão do usuário (cookie)
    session['game_id'] = game_id

    print(ACTIVE_GAMES)

    return jsonify(_get_game_status_data(new_game, game_id))

@api_bp.route("/options", methods=["GET"])
def get_options() -> Response | tuple[Response, int]:
    """Retorna até 5 personagens vizinhos do atual"""
    game: Game | None = get_current_game()

    if not game:
        return jsonify({"error": "Jogo não iniciado. Chame /start"}), 404

    # Verificação de game_over para impedir opções após o fim
    if game.game_over:
        state_msg: str = "Vitoria" if game.win else "Derrota"

        return jsonify({"error": f"O jogo já terminou: {state_msg}"}), 400

    options: list[Character] = game.options()

    return jsonify([vars(opt) for opt in options])


@api_bp.route("/choose", methods=["POST"])
def choose_character() -> Response | tuple[Response, int]:
    """
    Processa a escolha do próximo personagem, atualiza o estado
    e limpa o jogo se game_over for True.
    Espera {"id": ...}
    """
    game: Game = get_current_game()
    game_id: str = session.get("game_id") 

    if not game:
        return jsonify({"error": "Jogo não iniciado. Chame /start"}), 404

    data: dict[str, Any] = request.get_json()
    char_id: int = data.get("id")

    if char_id is None:
        return jsonify({"error": "ID do personagem ausente"}), 400

    try:
        # A função choose atualiza o estado do jogo
        # (current, choices_count, game_over)
        game.choose(char_id) 

        # Lógica de Limpeza: Verifica o flag game_over atualizado
        if game.game_over:
            clear_game_state(game_id)
            session.pop("game_id", None)

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

@api_bp.route("/status", methods=["GET"])
def get_status() -> Response | tuple[Response, int]:
    """Retorna informações do jogo atual"""
    game: Game = get_current_game()
    game_id: str = session.get("game_id")

    if not game:
        return jsonify({"error": "Nenhum jogo ativo."}), 404

    return jsonify(_get_game_status_data(game, game_id))
