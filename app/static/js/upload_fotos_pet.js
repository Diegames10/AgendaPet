document.addEventListener("DOMContentLoaded", function () {

    const componente = document.querySelector(
        "[data-upload-fotos-pet]"
    );

    if (!componente) {
        return;
    }

    const inputFotos = componente.querySelector(
        "[data-input-fotos-pet]"
    );

    const areaUpload = componente.querySelector(
        "[data-area-upload-pet]"
    );

    const preview = componente.querySelector(
        "[data-preview-fotos-pet]"
    );

    const contador = componente.querySelector(
        "[data-contador-fotos-pet]"
    );

    const erro = componente.querySelector(
        "[data-erro-fotos-pet]"
    );

    if (
        !inputFotos ||
        !areaUpload ||
        !preview ||
        !contador
    ) {
        console.error(
            "O componente de upload de fotos do pet está incompleto."
        );

        return;
    }

    const limiteTotal = Number(
        componente.dataset.limiteFotos || 3
    );

    const fotosExistentes = Number(
        componente.dataset.fotosExistentes || 0
    );

    const limiteNovas = Math.max(
        limiteTotal - fotosExistentes,
        0
    );

    const tiposPermitidos = [
        "image/jpeg",
        "image/png",
        "image/webp"
    ];

    const tamanhoMaximoBytes = 10 * 1024 * 1024;

    let arquivosSelecionados = [];

    function mostrarErro(mensagem) {

        if (erro) {
            erro.textContent = mensagem;
        }
    }

    function limparErro() {

        if (erro) {
            erro.textContent = "";
        }
    }

    function atualizarInput() {

        const transferencia = new DataTransfer();

        arquivosSelecionados.forEach(function (arquivo) {
            transferencia.items.add(arquivo);
        });

        inputFotos.files = transferencia.files;
    }

    function atualizarContador() {

        const totalAtual =
            fotosExistentes + arquivosSelecionados.length;

        contador.textContent =
            `${totalAtual} de ${limiteTotal} fotos`;
    }

    function arquivoDuplicado(arquivoNovo) {

        return arquivosSelecionados.some(
            function (arquivoExistente) {

                return (
                    arquivoExistente.name === arquivoNovo.name &&
                    arquivoExistente.size === arquivoNovo.size &&
                    arquivoExistente.lastModified ===
                        arquivoNovo.lastModified
                );
            }
        );
    }

    function removerArquivo(indice) {

        arquivosSelecionados.splice(indice, 1);

        atualizarInput();
        renderizarPreview();
        limparErro();
    }

    function renderizarPreview() {

        preview.innerHTML = "";

        arquivosSelecionados.forEach(
            function (arquivo, indice) {

                const item = document.createElement("article");
                item.className = "item-preview-pet";

                if (
                    fotosExistentes === 0 &&
                    indice === 0
                ) {
                    item.classList.add(
                        "foto-principal-preview"
                    );
                }

                const imagem = document.createElement("img");
                const urlTemporaria =
                    URL.createObjectURL(arquivo);

                imagem.src = urlTemporaria;
                imagem.alt =
                    `Pré-visualização da foto ${indice + 1}`;

                imagem.addEventListener(
                    "load",
                    function () {
                        URL.revokeObjectURL(
                            urlTemporaria
                        );
                    }
                );

                const identificacao =
                    document.createElement("div");

                identificacao.className =
                    "identificacao-preview-pet";

                const titulo =
                    document.createElement("span");

                titulo.textContent =
                    `Nova foto ${indice + 1}`;

                identificacao.appendChild(titulo);

                if (
                    fotosExistentes === 0 &&
                    indice === 0
                ) {
                    const principal =
                        document.createElement("strong");

                    principal.innerHTML =
                        '<i class="fa-solid fa-star"></i> Principal';

                    identificacao.appendChild(
                        principal
                    );
                }

                const botaoRemover =
                    document.createElement("button");

                botaoRemover.type = "button";
                botaoRemover.className =
                    "botao-remover-preview";

                botaoRemover.title =
                    "Remover foto selecionada";

                botaoRemover.setAttribute(
                    "aria-label",
                    `Remover foto ${indice + 1}`
                );

                botaoRemover.innerHTML =
                    '<i class="fa-solid fa-xmark"></i>';

                botaoRemover.addEventListener(
                    "click",
                    function () {
                        removerArquivo(indice);
                    }
                );

                item.appendChild(imagem);
                item.appendChild(identificacao);
                item.appendChild(botaoRemover);

                preview.appendChild(item);
            }
        );

        atualizarContador();
    }

    function adicionarArquivos(listaArquivos) {

        limparErro();

        const novosArquivos =
            Array.from(listaArquivos);

        for (const arquivo of novosArquivos) {

            if (
                arquivosSelecionados.length >=
                limiteNovas
            ) {
                mostrarErro(
                    limiteNovas === 0
                        ? "O limite de fotos já foi atingido."
                        : `Você pode adicionar somente ${limiteNovas} nova(s) foto(s).`
                );

                break;
            }

            if (
                !tiposPermitidos.includes(
                    arquivo.type
                )
            ) {
                mostrarErro(
                    `O arquivo "${arquivo.name}" possui formato inválido.`
                );

                continue;
            }

            if (
                arquivo.size >
                tamanhoMaximoBytes
            ) {
                mostrarErro(
                    `O arquivo "${arquivo.name}" excede o limite de 10 MB.`
                );

                continue;
            }

            if (arquivoDuplicado(arquivo)) {
                continue;
            }

            arquivosSelecionados.push(arquivo);
        }

        atualizarInput();
        renderizarPreview();
    }

    inputFotos.addEventListener(
        "change",
        function (evento) {

            adicionarArquivos(
                evento.target.files
            );
        }
    );

    areaUpload.addEventListener(
        "dragover",
        function (evento) {

            evento.preventDefault();

            areaUpload.classList.add(
                "arrastando"
            );
        }
    );

    areaUpload.addEventListener(
        "dragleave",
        function () {

            areaUpload.classList.remove(
                "arrastando"
            );
        }
    );

    areaUpload.addEventListener(
        "drop",
        function (evento) {

            evento.preventDefault();

            areaUpload.classList.remove(
                "arrastando"
            );

            adicionarArquivos(
                evento.dataTransfer.files
            );
        }
    );

    atualizarContador();
});