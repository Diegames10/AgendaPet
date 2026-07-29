document.addEventListener('DOMContentLoaded', function () {

    const calendarEl = document.getElementById('calendar');

    const modal = document.getElementById('modal-agendamento');
    const fecharModalTopo = document.getElementById('fechar-modal');
    const fecharModalRodape = document.getElementById('botao-fechar-modal');

    const campoPet = document.getElementById('modal-pet');
    const campoTutor = document.getElementById('modal-tutor');
    const campoVeterinario = document.getElementById('modal-veterinario');
    const campoTipo = document.getElementById('modal-tipo');
    const campoData = document.getElementById('modal-data');
    const campoHorario = document.getElementById('modal-horario');
    const campoStatus = document.getElementById('modal-status');
    const campoObservacoes = document.getElementById('modal-observacoes');
    const acoesAgendamento = document.getElementById('acoes-agendamento');
    const modalConfirmacao = document.getElementById('modal-confirmacao');

    const botaoVoltarCancelamento =
        document.getElementById('voltar-cancelamento');

    const botaoConfirmarCancelamento =
        document.getElementById('confirmar-cancelamento');

    let eventoPendenteCancelamento = null;

    function normalizarStatus(status) {
        return String(status || '')
            .trim()
            .toLowerCase()
            .normalize('NFD')
            .replace(/[\u0300-\u036f]/g, '');
    }

    function obterCorStatus(status) {
        const statusNormalizado = normalizarStatus(status);

        const cores = {
            agendado: '#f59e0b',
            confirmado: '#16a34a',
            em_atendimento: '#2563eb',
            'em atendimento': '#2563eb',
            concluido: '#475569',
            cancelado: '#dc2626'
        };

        return cores[statusNormalizado] || '#2563eb';
    }

    function formatarStatus(status) {
        if (!status) {
            return 'Não informado';
        }

        return String(status)
            .replaceAll('_', ' ')
            .replace(/\b\w/g, letra => letra.toUpperCase());
    }

    function abrirModalConfirmacao(evento) {
        eventoPendenteCancelamento = evento;

        modalConfirmacao.classList.add('aberto');
        modalConfirmacao.setAttribute('aria-hidden', 'false');
    }

    function fecharModalConfirmacao() {
        eventoPendenteCancelamento = null;

        modalConfirmacao.classList.remove('aberto');
        modalConfirmacao.setAttribute('aria-hidden', 'true');
    }    

    function montarAcoes(evento) {
    
    const dados = evento.extendedProps;
    acoesAgendamento.innerHTML = '';

    if (!dados.podeGerenciar) {
        return;
    }

    const status = normalizarStatus(dados.status);

    function criarBotao(texto, classe, callback) {

        const botao = document.createElement('button');

        botao.type = 'button';
        botao.className = classe;
        botao.textContent = texto;

        if (callback) {
            botao.addEventListener('click', callback);
        }

        return botao;
    }

    async function cancelarAgendamento() {

    abrirModalConfirmacao(evento);

    if (!confirmarCancelamento) {
        return;
    }

    const resposta = await fetch(
        `/calendario/cancelar/${evento.id}`,
        {
            method: 'POST'
        }
    );

    const dadosResposta = await resposta.json();

    if (!resposta.ok || !dadosResposta.sucesso) {
        alert(
            dadosResposta.mensagem ||
            'Não foi possível cancelar o agendamento.'
        );
        return;
    }

    evento.setExtendedProp(
        'status',
        dadosResposta.novo_status
    );

    const novaCor = obterCorStatus(
        dadosResposta.novo_status
    );

    evento.setProp('backgroundColor', novaCor);
    evento.setProp('borderColor', novaCor);

    abrirModal(evento);
}

    if (status === 'agendado') {

        acoesAgendamento.appendChild(

            criarBotao(

                'Confirmar',

                'btn-confirmar',

                async function () {

                    const resposta = await fetch(
                        `/calendario/confirmar/${evento.id}`,
                        {
                            method: 'POST'
                        }
                    );

                    const dadosResposta = await resposta.json();

                    if (!dadosResposta.sucesso) {

                        alert(dadosResposta.mensagem);

                        return;
                    }

                    evento.setExtendedProp(
                        'status',
                        dadosResposta.novo_status
                    );

                    evento.setProp(
                        'backgroundColor',
                        obterCorStatus(dadosResposta.novo_status)
                    );

                    evento.setProp(
                        'borderColor',
                        obterCorStatus(dadosResposta.novo_status)
                    );

                    abrirModal(evento);

                }

            )

        );

        acoesAgendamento.appendChild(
            criarBotao(
                'Editar',
                'btn-editar',

                function () {
                    window.location.href =
                        `/agendamentos/${evento.id}/editar`;
                }
            )
        );

        acoesAgendamento.appendChild(
            criarBotao(
                'Cancelar',
                'btn-cancelar',
                cancelarAgendamento
            )
        );
    }

    else if (status === 'confirmado') {

        acoesAgendamento.appendChild(
            criarBotao(
                'Iniciar atendimento',
                'btn-atendimento',

                async function () {

                    const resposta = await fetch(
                        `/calendario/iniciar-atendimento/${evento.id}`,
                        {
                            method: 'POST'
                        }
                    );

                    const dadosResposta = await resposta.json();

                    if (!resposta.ok || !dadosResposta.sucesso) {
                        alert(
                            dadosResposta.mensagem ||
                            'Não foi possível iniciar o atendimento.'
                        );
                        return;
                    }

                    evento.setExtendedProp(
                        'status',
                        dadosResposta.novo_status
                    );

                    const novaCor = obterCorStatus(
                        dadosResposta.novo_status
                    );

                    evento.setProp('backgroundColor', novaCor);
                    evento.setProp('borderColor', novaCor);

                    abrirModal(evento);
                }
            )
        );
        
        acoesAgendamento.appendChild(
            criarBotao(
                'Editar',
                'btn-editar',

                function () {
                    window.location.href =
                        `/agendamentos/${evento.id}/editar`;
                }
            )
        );

        acoesAgendamento.appendChild(
            criarBotao(
                'Cancelar',
                'btn-cancelar',
                cancelarAgendamento
            )
        );
    }




    else if (
        status === 'em atendimento' ||
        status === 'em_atendimento'
    ) {

        acoesAgendamento.appendChild(
            criarBotao(
                'Finalizar',
                'btn-finalizar',

                async function () {

                    const resposta = await fetch(
                        `/calendario/finalizar/${evento.id}`,
                        {
                            method: 'POST'
                        }
                    );

                    const dadosResposta = await resposta.json();

                    if (!resposta.ok || !dadosResposta.sucesso) {
                        alert(
                            dadosResposta.mensagem ||
                            'Não foi possível finalizar o atendimento.'
                        );
                        return;
                    }

                    evento.setExtendedProp(
                        'status',
                        dadosResposta.novo_status
                    );

                    const novaCor = obterCorStatus(
                        dadosResposta.novo_status
                    );

                    evento.setProp('backgroundColor', novaCor);
                    evento.setProp('borderColor', novaCor);

                    abrirModal(evento);
                }
            )
        );
    }

}

    function abrirModal(evento) {
        const dados = evento.extendedProps;
        const dataHora = evento.start;

        campoPet.textContent = dados.pet || 'Pet não informado';
        campoTutor.textContent = dados.tutor || 'Não informado';
        campoVeterinario.textContent =
            dados.veterinario || 'Não informado';
        campoTipo.textContent = dados.tipo || 'Não informado';

        campoData.textContent = dataHora
            ? dataHora.toLocaleDateString('pt-BR')
            : 'Não informada';

        campoHorario.textContent = dataHora
            ? dataHora.toLocaleTimeString('pt-BR', {
                hour: '2-digit',
                minute: '2-digit'
            })
            : 'Não informado';

        campoStatus.textContent = formatarStatus(dados.status);
        campoStatus.style.backgroundColor = obterCorStatus(dados.status);

        campoObservacoes.textContent =
            dados.observacoes || 'Nenhuma observação cadastrada.';

        montarAcoes(evento);
        modal.classList.add('aberto');
        modal.setAttribute('aria-hidden', 'false');
        document.body.classList.add('modal-aberto');
    }

    function fecharModal() {
        modal.classList.remove('aberto');
        modal.setAttribute('aria-hidden', 'true');
        document.body.classList.remove('modal-aberto');
    }

    const calendar = new FullCalendar.Calendar(calendarEl, {

        locale: 'pt-br',

        initialView: 'dayGridMonth',

        height: 'auto',

        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek,timeGridDay'
        },

        buttonText: {
            today: 'Hoje',
            month: 'Mês',
            week: 'Semana',
            day: 'Dia'
        },

        events: '/calendario/eventos',

        eventDidMount: function (info) {
            const cor = obterCorStatus(
                info.event.extendedProps.status
            );

            info.el.style.backgroundColor = cor;
            info.el.style.borderColor = cor;
        },

        eventClick: function (info) {
            abrirModal(info.event);
        }

    });

    fecharModalTopo.addEventListener('click', fecharModal);
    fecharModalRodape.addEventListener('click', fecharModal);

    modal.addEventListener('click', function (event) {
        if (event.target === modal) {
            fecharModal();
        }
    });

    document.addEventListener('keydown', function (event) {
        if (event.key === 'Escape') {
            fecharModal();
        }
    });

    botaoVoltarCancelamento.addEventListener(
    'click',
    fecharModalConfirmacao
);

botaoConfirmarCancelamento.addEventListener(
    'click',
    async function () {

        if (!eventoPendenteCancelamento) {
            return;
        }

        const evento = eventoPendenteCancelamento;

        botaoConfirmarCancelamento.disabled = true;
        botaoConfirmarCancelamento.textContent = 'Cancelando...';

        try {
            const resposta = await fetch(
                `/calendario/cancelar/${evento.id}`,
                {
                    method: 'POST'
                }
            );

            const dadosResposta = await resposta.json();

            if (!resposta.ok || !dadosResposta.sucesso) {
                alert(
                    dadosResposta.mensagem ||
                    'Não foi possível cancelar o agendamento.'
                );

                return;
            }

            evento.setExtendedProp(
                'status',
                dadosResposta.novo_status
            );

            const novaCor = obterCorStatus(
                dadosResposta.novo_status
            );

            evento.setProp('backgroundColor', novaCor);
            evento.setProp('borderColor', novaCor);

            fecharModalConfirmacao();
            abrirModal(evento);

        } catch (erro) {
            alert(
                'Ocorreu um erro ao cancelar o agendamento.'
            );

            console.error(erro);

        } finally {
            botaoConfirmarCancelamento.disabled = false;

            botaoConfirmarCancelamento.textContent =
                'Cancelar agendamento';
        }
    });
    modalConfirmacao.addEventListener('click', function (event) {
        if (event.target === modalConfirmacao) {
            fecharModalConfirmacao();
        }
    });

    calendar.render();

});