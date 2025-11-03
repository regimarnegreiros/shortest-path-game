// responsável por todas interações diretas com HTML tipo eventos, manipulação de DOM e animações
import { startGameAPI, getOptionsAPI, getStatusAPI, postChooseAPI } from "./api.js"

document.addEventListener('DOMContentLoaded', startGame);



const character_origem = document.getElementById("origem")
const character_destino = document.getElementById("destino")
const barra_processo = document.getElementById("barra")
const perga = document.querySelector('.perga-container');



function lockOptions(lock) {
    const botoes = document.querySelectorAll('.char-display-options');
    botoes.forEach(btn => {
        btn.style.pointerEvents = lock ? 'none' : 'auto';  // quando for false bota como none, quando true bota auto (normal)
    });

}

async function startGame() {
    //listeners
    const characters_options = document.querySelectorAll(".char-display-options")
    characters_options.forEach((option) => {
        option.addEventListener("click", selected)
    });


    let gameState;
    try {
        gameState = await getStatusAPI();
        //console.log(gameState);

    }
    catch (error) {
        console.log("Começando novo game", error)
        try {
            gameState = await startGameAPI();

        } catch (error) {
            console.log("Erro em startGame");
        }
    }
    if (gameState) {
        updateCharDiplay(character_origem, gameState.initial);
        updateCharDiplay(character_destino, gameState.destination);
        await getOptions();

        // console.log(gameState);
    }
    else {
        alert("Erro, por favor recarregue a pagina");
    }
}


async function getOptions() {

    const container = document.querySelector('.div-Teste-options');

    container.innerHTML = '';

    try {

        let char_options = await getOptionsAPI();

        for (let i = 0; i < char_options.length; i++) {
            const char_data = char_options[i]; // salva o personagem na lista
            const novaOption = document.createElement('button');
            novaOption.classList.add('char-display', 'char-display-options');
            novaOption.dataset.id = char_data.id;
            novaOption.addEventListener('click', selected);
            updateCharDiplay(novaOption, char_data);
            container.appendChild(novaOption);
        }

    } catch (error) {
        console.log("Erro no getOptions", error);
    }
}

function updateCharDiplay(html_element, char_data) {

    html_element.innerHTML = '';
    if (!char_data) return;
    const char_img = document.createElement('img');
    if (char_data.images && char_data.images.length > 0) { // tenho que melhorar isso pq tem galera que tem iamgem mas num é do char

        char_img.src = char_data.images[0];

        html_element.appendChild(char_img);

    }
    else {

        console.log(char_data.name, 'não tem imagem')
        const char_name = document.createElement('p');
        char_name.textContent = char_data.name;
        html_element.appendChild(char_name);
    }

    const char_name_overlay = document.createElement('span');
    char_name_overlay.textContent = char_data.name;
    char_name_overlay.classList.add('char-name-overlay');
    html_element.appendChild(char_name_overlay);


}



// preciso da propriedade de caminho/lista de escolhas feitas do back
function carregaEscolhasAntigas(path) {
    const escolhasFeitas = document.querySelectorAll('.path-step');
    escolhasFeitas.forEach(passo => passo.remove());
    // daí agora eu pegaria do back 

}


async function selected(e) {

    const selectedOption = e.currentTarget; // botão clicado
    const currentOpstions = barra_processo.querySelectorAll('.char-display-options');
    const selected_id = selectedOption.dataset.id;
    console.log(selected_id); //teste
    console.log(selectedOption); //teste tmb
    lockOptions(true);
    selectedOption.removeEventListener('click', selected);
    localEscolha(currentOpstions, selectedOption);
    // slectedOption.classList.add('move');  classe depois pra animar
    perga.classList.add('fecha');
    try {
        const newState = await postChooseAPI(selected_id);
        if (newState.game_over) {
            console.log("Game over.", newState.win ? "Vitória!" : "Derrota!");
            perga.classList.remove('fecha'); // cancela a animação

            alert(newState.win ? "UHUL" : "BUUUH");
            lockOptions(false);
            return;
        }
        setTimeout(async () => {


            await getOptions();
            perga.classList.remove('fecha');
            perga.classList.add('open');

            setTimeout(() => {
                perga.classList.remove('open')
                lockOptions(false);
            }, 600)
        }, 600)

        console.log("clicado");
    } catch (error) {
        console.error("erro em processar as novas opções");
        lockOptions(false);
    }
}

function localEscolha(c_options, s_options) {
    if (c_options.length == 0) {

        barra_processo.insertBefore(s_options, character_destino);


    }
    else { // aqui vou ter que mudar quando for uma 'boa' ou 'má' escolha

        barra_processo.insertBefore(s_options, c_options[c_options.length - 1])

    }

}





//erro do favicon.ico, depois botar um 