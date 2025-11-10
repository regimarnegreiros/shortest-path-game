// Responsável pelas requisições do Flask
// Separado em outro script pra facilitar as futuras mudanças do front

export async function startGameAPI() {
    try {
        // fetch recebe (url,{objeto de config tipo method,header e body}),
        // se num passo nada no segundo, ele faz um get
        const res = await fetch("/api/start", { method: "POST" });

        if (!res.ok)  // 200 a 299
            throw new Error("Erro no /api/start");

        return res.json();
    }
    catch (error) {
        console.error("Função startGameAPI não funcionou");
        throw error;
    }
}

export async function getStatusAPI() {
    try {
        const res = await fetch("/api/status", { method: "GET" });

        if (!res.ok)
            throw new Error("Nenhum game encontrado");

        return res.json();
    }
    catch (error) {
        throw (error);
    }
}

export async function getOptionsAPI() {
    try {
        const res = await fetch("/api/options", { method: "GET" });

        if (!res.ok)
            throw new Error("Erro na /options");

        return res.json();
    }
    catch (error) {
        console.error("Função getOptionsAPI não funcionou")
        throw error;
    }
}

export async function postChooseAPI(char_id) {
    try {
        const res = await fetch("/api/choose", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ id: parseInt(char_id) })
        });

        if (!res.ok)
            throw new Error("Erro em postChooseAPI");

        return res.json();
    }
    catch (error) {
        throw error;
    }
}
