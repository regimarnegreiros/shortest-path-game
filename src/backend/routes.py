from flask import Flask, jsonify, request
from Game import game_instance, Game, Character

app = Flask(__name__)


@app.route("/start", methods=["POST"])
def start_game():
    """
    Inicia o jogo definindo personagem inicial e destino.
    Espera receber JSON com {"initial_id": ..., "destination_id": ...}
    """
    data = request.get_json()
    initial_id = data.get("initial_id")
    destination_id = data.get("destination_id")

    # Exemplo de uso do Game
    game_instance.initial = game_instance.set_initial()  # lógica interna
    game_instance.destination = game_instance.set_destination()

    return jsonify({
        "initial": vars(game_instance.initial) if game_instance.initial else None,
        "destination": vars(game_instance.destination) if game_instance.destination else None
    })


@app.route("/options", methods=["GET"])
def get_options():
    """Retorna até 5 personagens vizinhos do atual"""
    options = game_instance.options()
    return jsonify([vars(opt) for opt in options])


@app.route("/choose", methods=["POST"])
def choose_character():
    """
    Escolhe o próximo personagem.
    Espera {"id": ...}
    """
    data = request.get_json()
    char_id = data.get("id")

    reached = game_instance.choose(char_id)
    return jsonify({
        "current": vars(game_instance.current) if game_instance.current else None,
        "reached_destination": reached,
        "choices_count": game_instance.choices_count
    })


@app.route("/status", methods=["GET"])
def get_status():
    """Retorna informações do jogo atual"""
    return jsonify({
        "initial": vars(game_instance.initial) if game_instance.initial else None,
        "current": vars(game_instance.current) if game_instance.current else None,
        "destination": vars(game_instance.destination) if game_instance.destination else None,
        "choices_count": game_instance.choices_count,
        "max_choices": game_instance.max_choices
    })


if __name__ == "__main__":
    app.run(debug=True)
