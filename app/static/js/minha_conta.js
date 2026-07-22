document.addEventListener("DOMContentLoaded", function () {

    const campoCep =
        document.getElementById("cep");

    const botaoBuscarCep =
        document.getElementById("buscar-cep");

    const mensagemCep =
        document.getElementById("mensagem-cep");

    const campoLogradouro =
        document.getElementById("logradouro");

    const campoNumero =
        document.getElementById("numero");

    const campoBairro =
        document.getElementById("bairro");

    const campoCidade =
        document.getElementById("cidade");

    const campoUf =
        document.getElementById("uf");


    if (!campoCep) {
        return;
    }


    function aplicarMascaraCep(valor) {

        let numeros =
            valor.replace(/\D/g, "");

        numeros =
            numeros.substring(0, 8);

        if (numeros.length > 5) {

            return (
                numeros.substring(0, 5) +
                "-" +
                numeros.substring(5)
            );

        }

        return numeros;

    }


    function limparMensagemCep() {

        if (!mensagemCep) {
            return;
        }

        mensagemCep.textContent = "";

        mensagemCep.classList.remove(
            "erro",
            "sucesso",
            "buscando"
        );

    }


    function exibirMensagemCep(texto, tipo) {

        if (!mensagemCep) {
            return;
        }

        mensagemCep.textContent = texto;

        mensagemCep.classList.remove(
            "erro",
            "sucesso",
            "buscando"
        );

        mensagemCep.classList.add(tipo);

    }


    function limparEndereco() {

        if (campoLogradouro) {
            campoLogradouro.value = "";
        }

        if (campoBairro) {
            campoBairro.value = "";
        }

        if (campoCidade) {
            campoCidade.value = "";
        }

        if (campoUf) {
            campoUf.value = "";
        }

    }


    function preencherEndereco(endereco) {

        if (campoLogradouro) {

            campoLogradouro.value =
                endereco.logradouro || "";

        }

        if (campoBairro) {

            campoBairro.value =
                endereco.bairro || "";

        }

        if (campoCidade) {

            campoCidade.value =
                endereco.localidade || "";

        }

        if (campoUf) {

            campoUf.value =
                endereco.uf || "";

        }

    }


    async function consultarCep() {

        const cep =
            campoCep.value.replace(/\D/g, "");

        limparMensagemCep();


        if (!cep) {
            return;
        }


        if (cep.length !== 8) {

            exibirMensagemCep(
                "Informe um CEP com 8 números.",
                "erro"
            );

            return;

        }


        if (botaoBuscarCep) {

            botaoBuscarCep.disabled = true;

            botaoBuscarCep.innerHTML =
                '<i class="fa-solid fa-spinner fa-spin"></i>';

        }


        exibirMensagemCep(
            "Buscando endereço...",
            "buscando"
        );


        try {

            const resposta = await fetch(
                `https://viacep.com.br/ws/${cep}/json/`
            );


            if (!resposta.ok) {

                throw new Error(
                    "Erro ao consultar o CEP."
                );

            }


            const endereco =
                await resposta.json();


            if (endereco.erro) {

                limparEndereco();

                exibirMensagemCep(
                    "CEP não encontrado.",
                    "erro"
                );

                return;

            }


            preencherEndereco(endereco);


            exibirMensagemCep(
                "Endereço encontrado com sucesso.",
                "sucesso"
            );


            if (campoNumero) {

                campoNumero.focus();

            }

        } catch (erro) {

            exibirMensagemCep(
                "Não foi possível consultar o CEP no momento.",
                "erro"
            );

        } finally {

            if (botaoBuscarCep) {

                botaoBuscarCep.disabled = false;

                botaoBuscarCep.innerHTML =
                    '<i class="fa-solid fa-magnifying-glass"></i>';

            }

        }

    }


    campoCep.addEventListener("input", function () {

        campoCep.value =
            aplicarMascaraCep(campoCep.value);

        limparMensagemCep();

    });


    campoCep.addEventListener("blur", function () {

        const cep =
            campoCep.value.replace(/\D/g, "");

        if (cep.length === 8) {

            consultarCep();

        }

    });


    campoCep.addEventListener("keydown", function (evento) {

        if (evento.key === "Enter") {

            evento.preventDefault();

            consultarCep();

        }

    });


    if (botaoBuscarCep) {

        botaoBuscarCep.addEventListener(
            "click",
            consultarCep
        );

    }


    if (campoUf) {

        campoUf.addEventListener("input", function () {

            campoUf.value =
                campoUf.value
                    .replace(/[^a-zA-Z]/g, "")
                    .toUpperCase()
                    .substring(0, 2);

        });

    }

});