from flask import Flask, render_template
from webbrowser import open as wbopen
from routes import api_bp
from threading import Thread
import os, uuid

# Criação do app Flask com suporte aos templates e arquivos estáticos
app = Flask(
    __name__,
    template_folder="../frontend/templates",
    static_folder="../frontend/static"
)

# Chave secreta OBRIGATÓRIA para usar sessions (cookies seguros)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', str(uuid.uuid4()))

# Registro do Blueprint da API
app.register_blueprint(api_bp, url_prefix="/api")

# Rotas de páginas HTML
@app.route("/")
def index() -> str:
    return render_template("index.html")

@app.route("/game")
def game() -> str:
    return render_template("game.html")


if __name__ == "__main__":
    wbopen("http://127.0.0.1:5000")
    app.run(debug=True, use_reloader=False)
