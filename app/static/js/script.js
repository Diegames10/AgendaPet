console.log("AgendaPet Paranaguá iniciado com sucesso!");document.addEventListener("DOMContentLoaded", function () {
    const elementosParaRevelar = document.querySelectorAll(".revelar");
    const cabecalho = document.querySelector(".cabecalho-index");
    const anoAtual = document.getElementById("anoAtual");

    /*
     * Atualiza automaticamente o ano do rodapé.
     */
    if (anoAtual) {
        anoAtual.textContent = new Date().getFullYear();
    }

    /*
     * Adiciona sombra no cabeçalho após o início da rolagem.
     */
    function atualizarCabecalho() {
        if (!cabecalho) {
            return;
        }

        if (window.scrollY > 30) {
            cabecalho.classList.add("com-sombra");
        } else {
            cabecalho.classList.remove("com-sombra");
        }
    }

    window.addEventListener("scroll", atualizarCabecalho);
    atualizarCabecalho();

    /*
     * IntersectionObserver verifica quando cada elemento
     * entra na área visível da página.
     */
    const observador = new IntersectionObserver(
        function (entradas, observer) {
            entradas.forEach(function (entrada) {
                if (entrada.isIntersecting) {
                    entrada.target.classList.add("visivel");

                    /*
                     * O elemento deixa de ser observado após aparecer.
                     * Assim, a animação ocorre somente uma vez.
                     */
                    observer.unobserve(entrada.target);
                }
            });
        },
        {
            threshold: 0.18,
            rootMargin: "0px 0px -50px 0px"
        }
    );

    elementosParaRevelar.forEach(function (elemento) {
        observador.observe(elemento);
    });
});