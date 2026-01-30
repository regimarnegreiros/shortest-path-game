# Nagrafo - Shortest Path Game 🎮

Um projeto desenvolvido para aprender e praticar **Teoria dos Grafos** e **Algoritmos de Busca**. O objetivo é encontrar o caminho mais curto entre dois personagens do universo Naruto.

## 📖 Sobre

Este projeto implementa um grafo com personagens de Naruto e seus relacionamentos. O jogador deve encontrar o caminho mais curto (menor número de "saltos") entre dois personagens aleatórios.

---

## 🚀 Instalação e Execução

### Pré-requisitos

- **Python 3.7+** instalado
- **pip** (gerenciador de pacotes Python)

### Passo 1: Clonar o Repositório

```bash
git clone https://github.com/seu-usuario/shortest-path-game.git
cd shortest-path-game
```

### Passo 2: Instalar Dependências

Instale as dependências do projeto:

```bash
pip install -r requirements.txt
```

### Passo 3: Iniciar o Servidor

#### 🪟 Windows

Clique duas vezes em **`iniciar.bat`** e o navegador abrirá automaticamente em `http://localhost:5000`

#### 🐧 Linux / macOS

```bash
chmod +x iniciar.sh
./iniciar.sh
```

Acesse `http://localhost:5000` no seu navegador

#### 🔧 Alternativa (Qualquer SO)

```bash
cd src/backend
python app.py
```

---

## 🎮 Como Jogar

1. O jogo escolhe **dois personagens aleatórios**
2. Clique nos botões para "caminhar" pelo grafo entre relacionamentos
3. Encontre o caminho mais curto até chegar ao personagem de destino

### Tela Inicial

![home](/assets/home.jpeg)

### Tela de Jogo

![game](/assets/game.jpeg)

### Vitória

![victory](/assets/victory.jpeg)

---

## 📁 Estrutura do Projeto

```
shortest-path-game/
├── src/
│   ├── backend/
│   │   ├── app.py              # Aplicação Flask
│   │   ├── routes.py           # Rotas da API
│   │   ├── Game.py             # Lógica do jogo
│   │   ├── Graph.py            # Implementação do grafo
│   │   ├── Character.py        # Classe do personagem
│   │   └── data/               # Dados em JSON
│   └── frontend/
│       ├── templates/          # HTML
│       └── static/             # CSS, JS, imagens
├── requirements.txt
├── iniciar.bat                 # Windows
├── iniciar.sh                  # Linux/macOS
└── README.md
```

---

## 🛠️ Tecnologias

- **Backend**: Flask, NetworkX, Python 3.7+
- **Frontend**: HTML5, CSS3, JavaScript
- **Dados**: JSON, GML (Graph Modelling Language)

---