// responsável por todas interações diretas com HTML tipo eventos, manipulação de DOM e animações
import { startGameAPI,getOptionsAPI,getStatusAPI,postChooseAPI } from "./api.js"

document.addEventListener('DOMContentLoaded', startGame);


const characters_options = document.querySelectorAll(".char-display-options")
const character_origem = document.getElementById("origem")
const character_destino = document.getElementById("destino")
const barra_processo = document.getElementById("barra")
const perga = document.querySelector('.perga-container');

characters_options.forEach((option) => {
    option.addEventListener("click",selected)
});

/*async function startGame() {
    
    try{
    const gameState = await startGameAPI();
    //console.log(gameState);
    updateCharDiplay(character_origem,gameState.initial);
    updateCharDiplay(character_destino,gameState.destination);
    }
    catch(error){
        console.log("Erro iniciando o game",error)
    }
}*/

async function startGame() {
    
    let gameState;
    try{
        gameState = await getStatusAPI();
        console.log(gameState);
    
    }
    catch(error){
        console.log("Começando novo game",error)
        try {
             gameState = await startGameAPI();
            
        } catch (error) {
            console.log("Erro em startGame");
        }
    }
    if (gameState) {
        updateCharDiplay(character_origem,gameState.initial);
        updateCharDiplay(character_destino,gameState.destination);
        await getOptions();
    }
    else{
        alert("Erro, por favor recarregue a pagina");
    }
}

async function getOptions() {
    try {
        let  char_options = await getOptionsAPI();
        let  botoes = document.querySelectorAll('.char-display-options');
        for (let i = 0; i < char_options.length; i++) {
            
            botoes[i].dataset.id = char_options[i].id;
            updateCharDiplay(botoes[i],char_options[i]);          
                  
        }
    } catch (error) {
        console.log("Erro na getOptions")
    }
}


function updateCharDiplay(html_element, char_data){

    html_element.innerHTML='';
    if(!char_data) return;
    const char_img = document.createElement('img');
    if(char_data.images && char_data.images.length >0){ // tenho que melhorar isso pq tem galera que tem iamgem mas num é do char

        char_img.src = char_data.images[0];
       
        html_element.appendChild(char_img);

    }
    else{
        
        console.log(char_data.name,'não tem imagem')
        const char_name = document.createElement('p');
        char_name.textContent = char_data.name;
        html_element.appendChild(char_name);
    }
   
    
    //const char_name = document.createElement('p');
    //perga.textContent = char_data.name; 
   
    //html_element.appendChild(char_name);

}



// preciso da propriedade de caminho/lista de escolhas feitas do back
function carregaEscolhasAntigas(path){
    const escolhasFeitas = document.querySelectorAll('.path-step');
    escolhasFeitas.forEach(passo =>passo.remove());
    // daí agora eu pegaria do back 

}


async function selected(e) {

    const selectedOption = e.currentTarget; // botão clicado
    const currentOpstions = barra_processo.querySelectorAll('.char-display-options');
    const selected_id = selectedOption.dataset.id;
    console.log(selected_id); //teste
    //if (!selected_id) return;
    if (!selected_id || selectedOption.parentElement.id === 'barra') return;
    /*try {
         n_gameState = await postChooseAPI(selected_id); 
    
    } catch (error) {
        console.log("Erro no selected,postChoose");
    }*/
   
   
    if (currentOpstions.length == 0){

     barra_processo.insertBefore(selectedOption, character_destino);


    }
    else { // aqui vou ter que mudar quando for uma 'boa' ou 'má' escolha

        barra_processo.insertBefore(selectedOption,currentOpstions[currentOpstions.length-1])

    }
    // slectedOption.classList.add('move');  classe depois pra animar
    perga.classList.add('fecha');
    setTimeout(()=>{
        //atualizaPerga();
        getOptions();
        perga.classList.remove('fecha');
        perga.classList.add('open');

    setTimeout(()=>{
        perga.classList.remove('open')
    },600)
    },600)
    console.log("clicado");
}




 function atualizaPerga() {
  const container = document.querySelector('.div-Teste-options');
  container.innerHTML = ''; // limpa as opções antigas

  // cria 5 novos botões de exemplo
  for (let i = 0; i < 5; i++) {
    const novaOption = document.createElement('button');
    novaOption.classList.add('char-display', 'char-display-options');
    novaOption.addEventListener('click', selected);
    container.appendChild(novaOption);
  }
}
//console.log(characters_options);


//erro do favicon.ico, depois botar um 