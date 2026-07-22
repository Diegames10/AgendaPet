from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from app import db
from app.models.historico import Historico
from app.models.agendamentoConsulta import AgendamentoConsulta
from app.models.pet import Pet

from io import BytesIO
import re
import unicodedata

from flask import send_file

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
    KeepTogether
)

historico_bp = Blueprint(
    "historico",
    __name__,
    url_prefix="/historico"
)


# =========================================================
# LISTAR HISTÓRICOS
# =========================================================

@historico_bp.route("/")
@login_required
def listar():

    historicos = (
        Historico.query
        .join(Pet, Historico.pet_id == Pet.id)
        .filter(Pet.tutor_id == current_user.id)
        .order_by(Historico.data_atendimento.desc())
        .all()
    )

    return render_template(
        "historico/listar_historico.html",
        historicos=historicos
    )


# =========================================================
# VER DETALHES DO HISTÓRICO
# =========================================================

@historico_bp.route("/detalhes/<int:historico_id>")
@login_required
def detalhes(historico_id):

    historico = (
        Historico.query
        .join(Pet, Historico.pet_id == Pet.id)
        .filter(
            Historico.id == historico_id,
            Pet.tutor_id == current_user.id
        )
        .first_or_404()
    )

    return render_template(
        "historico/detalhes_historico.html",
        historico=historico
    )


# =========================================================
# FINALIZAR ATENDIMENTO
# =========================================================

@historico_bp.route(
    "/finalizar/<int:agendamento_id>",
    methods=["GET", "POST"]
)
@login_required
def finalizar_atendimento(agendamento_id):

    agendamento = AgendamentoConsulta.query.filter_by(
        id=agendamento_id,
        tutor_id=current_user.id
    ).first_or_404()

    # Impede finalizar um atendimento cancelado
    if agendamento.status == "Cancelado":

        flash(
            "Não é possível finalizar um agendamento cancelado.",
            "erro"
        )

        return redirect(
            url_for("agendamento_consulta.listar")
        )

    # Verifica se já existe histórico para esse agendamento
    historico_existente = Historico.query.filter_by(
        agendamento_id=agendamento.id
    ).first()

    if historico_existente:

        flash(
            "Este atendimento já foi finalizado.",
            "aviso"
        )

        return redirect(
            url_for(
                "historico.detalhes",
                historico_id=historico_existente.id
            )
        )

    if request.method == "POST":

        diagnostico = request.form.get(
            "diagnostico",
            ""
        ).strip()

        tratamento = request.form.get(
            "tratamento",
            ""
        ).strip()

        observacoes = request.form.get(
            "observacoes",
            ""
        ).strip()

        if not diagnostico:

            flash(
                "Informe o diagnóstico do atendimento.",
                "erro"
            )

            return render_template(
                "historico/finalizar.html",
                agendamento=agendamento
            )

        novo_historico = Historico(
            data_atendimento=agendamento.data,
            tipo_atendimento=agendamento.tipo,
            diagnostico=diagnostico,
            tratamento=tratamento,
            observacoes=observacoes,
            pet_id=agendamento.pet_id,
            veterinario_id=agendamento.veterinario_id,
            agendamento_id=agendamento.id
        )

        agendamento.status = "Concluído"

        try:

            db.session.add(novo_historico)
            db.session.commit()

            flash(
                "Atendimento finalizado e registrado no histórico.",
                "sucesso"
            )

            return redirect(
                url_for(
                    "historico.detalhes",
                    historico_id=novo_historico.id
                )
            )

        except Exception as erro:

            db.session.rollback()

            print(
                f"Erro ao finalizar atendimento: {erro}"
            )

            flash(
                "Não foi possível finalizar o atendimento.",
                "erro"
            )

    return render_template(
        "historico/finalizar.html",
        agendamento=agendamento
    )
    
# =========================================================
# VISUALIZAR RECEITA
# =========================================================

@historico_bp.route("/<int:historico_id>/receita")
@login_required
def receita(historico_id):

    historico = (
        Historico.query
        .join(Pet, Historico.pet_id == Pet.id)
        .filter(
            Historico.id == historico_id,
            Pet.tutor_id == current_user.id
        )
        .first_or_404()
    )

    return render_template(
        "historico/receita.html",
        historico=historico
    ) 
    
# =========================================================
# BAIXAR RECEITA EM PDF
# =========================================================

@historico_bp.route("/<int:historico_id>/receita/pdf")
@login_required
def baixar_receita_pdf(historico_id):

    historico = (
        Historico.query
        .join(Pet, Historico.pet_id == Pet.id)
        .filter(
            Historico.id == historico_id,
            Pet.tutor_id == current_user.id
        )
        .first_or_404()
    )

    buffer = BytesIO()

    documento = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=15 * mm,
        bottomMargin=18 * mm,
        title=f"Receita Veterinária - {historico.pet.nome}",
        author="AgendaPet Paranaguá"
    )

    estilos = getSampleStyleSheet()

    estilo_titulo = ParagraphStyle(
        "TituloAgendaPet",
        parent=estilos["Title"],
        fontName="Helvetica-Bold",
        fontSize=22,
        leading=26,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#087f5b"),
        spaceAfter=4
    )

    estilo_subtitulo = ParagraphStyle(
        "SubtituloAgendaPet",
        parent=estilos["Normal"],
        fontName="Helvetica",
        fontSize=11,
        leading=14,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#64748b"),
        spaceAfter=16
    )

    estilo_secao = ParagraphStyle(
        "SecaoAgendaPet",
        parent=estilos["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=16,
        textColor=colors.HexColor("#065f46"),
        spaceBefore=10,
        spaceAfter=8
    )

    estilo_rotulo = ParagraphStyle(
        "RotuloAgendaPet",
        parent=estilos["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#64748b")
    )

    estilo_valor = ParagraphStyle(
        "ValorAgendaPet",
        parent=estilos["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=13,
        textColor=colors.HexColor("#1f2937")
    )

    estilo_texto = ParagraphStyle(
        "TextoAgendaPet",
        parent=estilos["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=15,
        alignment=TA_LEFT,
        textColor=colors.HexColor("#1f2937")
    )

    estilo_data = ParagraphStyle(
        "DataAgendaPet",
        parent=estilos["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=13,
        alignment=TA_RIGHT,
        textColor=colors.HexColor("#374151")
    )

    estilo_assinatura = ParagraphStyle(
        "AssinaturaAgendaPet",
        parent=estilos["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=14,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#111827")
    )

    elementos = []

    elementos.append(
        Paragraph("AgendaPet Paranaguá", estilo_titulo)
    )

    elementos.append(
        Paragraph(
            "Sistema de Agendamento Veterinário",
            estilo_subtitulo
        )
    )

    elementos.append(
        HRFlowable(
            width="100%",
            thickness=2,
            color=colors.HexColor("#087f5b"),
            spaceBefore=2,
            spaceAfter=14
        )
    )

    elementos.append(
        Paragraph("RECEITA VETERINÁRIA", estilo_secao)
    )

    elementos.append(
        Paragraph(
            f"Documento referente ao atendimento nº {historico.id}",
            estilo_subtitulo
        )
    )

    elementos.append(
        Paragraph("IDENTIFICAÇÃO DO PACIENTE", estilo_secao)
    )

    nome_pet = historico.pet.nome or "Não informado"
    especie = historico.pet.especie or "Não informada"
    raca = historico.pet.raca or "Não informada"
    sexo = historico.pet.sexo or "Não informado"

    if historico.pet.peso:
        peso = f"{historico.pet.peso} kg"
    else:
        peso = "Não informado"

    if historico.data_atendimento:
        data_atendimento = historico.data_atendimento.strftime("%d/%m/%Y")
    else:
        data_atendimento = "Não informada"

    dados_pet = [
        [
            Paragraph("NOME DO ANIMAL", estilo_rotulo),
            Paragraph("ESPÉCIE", estilo_rotulo),
        ],
        [
            Paragraph(nome_pet, estilo_valor),
            Paragraph(especie, estilo_valor),
        ],
        [
            Paragraph("RAÇA", estilo_rotulo),
            Paragraph("SEXO", estilo_rotulo),
        ],
        [
            Paragraph(raca, estilo_valor),
            Paragraph(sexo, estilo_valor),
        ],
        [
            Paragraph("PESO", estilo_rotulo),
            Paragraph("DATA DO ATENDIMENTO", estilo_rotulo),
        ],
        [
            Paragraph(peso, estilo_valor),
            Paragraph(data_atendimento, estilo_valor),
        ],
    ]

    tabela_pet = Table(
        dados_pet,
        colWidths=[87 * mm, 87 * mm],
        hAlign="LEFT"
    )

    tabela_pet.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
            ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#dbe3e8")),
            ("INNERGRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#e2e8f0")),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 7),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ])
    )

    elementos.append(tabela_pet)
    elementos.append(Spacer(1, 10))

    elementos.append(
        Paragraph("IDENTIFICAÇÃO DO TUTOR", estilo_secao)
    )

    if historico.pet.tutor:
        nome_tutor = historico.pet.tutor.nome or "Não informado"
    else:
        nome_tutor = "Não informado"

    tabela_tutor = Table(
        [
            [Paragraph("NOME COMPLETO", estilo_rotulo)],
            [Paragraph(nome_tutor, estilo_valor)],
        ],
        colWidths=[174 * mm]
    )

    tabela_tutor.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
            ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#dbe3e8")),
            ("INNERGRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#e2e8f0")),
            ("TOPPADDING", (0, 0), (-1, -1), 7),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ])
    )

    elementos.append(tabela_tutor)
    elementos.append(Spacer(1, 10))

    elementos.append(
        Paragraph("PRESCRIÇÃO VETERINÁRIA", estilo_secao)
    )

    tratamento = historico.tratamento or (
        "Nenhuma prescrição foi registrada para este atendimento."
    )

    tratamento_html = tratamento.replace("\n", "<br/>")

    tabela_prescricao = Table(
        [[Paragraph(tratamento_html, estilo_texto)]],
        colWidths=[174 * mm],
        minRowHeights=[55 * mm]
    )

    tabela_prescricao.setStyle(
        TableStyle([
            ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor("#94a3b8")),
            ("LINEBEFORE", (0, 0), (0, -1), 4, colors.HexColor("#087f5b")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING", (0, 0), (-1, -1), 12),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
            ("LEFTPADDING", (0, 0), (-1, -1), 12),
            ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ])
    )

    elementos.append(tabela_prescricao)
    elementos.append(Spacer(1, 10))

    elementos.append(
        Paragraph("ORIENTAÇÕES COMPLEMENTARES", estilo_secao)
    )

    observacoes = historico.observacoes or (
        "Não há orientações complementares registradas."
    )

    observacoes_html = observacoes.replace("\n", "<br/>")

    tabela_orientacoes = Table(
        [[Paragraph(observacoes_html, estilo_texto)]],
        colWidths=[174 * mm],
        minRowHeights=[25 * mm]
    )

    tabela_orientacoes.setStyle(
        TableStyle([
            ("BOX", (0, 0), (-1, -1), 0.7, colors.HexColor("#94a3b8")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING", (0, 0), (-1, -1), 10),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
            ("LEFTPADDING", (0, 0), (-1, -1), 10),
            ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ])
    )

    elementos.append(tabela_orientacoes)
    elementos.append(Spacer(1, 18))

    elementos.append(
        Paragraph(
            f"Paranaguá, {data_atendimento}.",
            estilo_data
        )
    )

    elementos.append(Spacer(1, 38))

    if historico.veterinario:
        nome_veterinario = (
            historico.veterinario.nome or
            "Médico(a)-veterinário(a)"
        )

        crmv = getattr(
            historico.veterinario,
            "crmv",
            None
        ) or "__________________"
    else:
        nome_veterinario = "Assinatura do(a) médico(a)-veterinário(a)"
        crmv = "__________________"

    bloco_assinatura = KeepTogether([
        HRFlowable(
            width=90 * mm,
            thickness=0.7,
            color=colors.black,
            hAlign="CENTER",
            spaceAfter=6
        ),
        Paragraph(
            f"Dr(a). {nome_veterinario}",
            estilo_assinatura
        ),
        Paragraph(
            f"CRMV-PR: {crmv}",
            estilo_assinatura
        ),
    ])

    elementos.append(bloco_assinatura)
    elementos.append(Spacer(1, 15))

    elementos.append(
        HRFlowable(
            width="100%",
            thickness=0.5,
            color=colors.HexColor("#dbe3e8"),
            spaceBefore=6,
            spaceAfter=6
        )
    )

    elementos.append(
        Paragraph(
            "AgendaPet Paranaguá — Documento emitido eletronicamente.",
            estilo_subtitulo
        )
    )

    documento.build(elementos)

    buffer.seek(0)

    nome_pet_arquivo = historico.pet.nome or "Pet"

    nome_pet_arquivo = unicodedata.normalize(
        "NFKD",
        nome_pet_arquivo
    ).encode(
        "ASCII",
        "ignore"
    ).decode(
        "ASCII"
    )

    nome_pet_arquivo = re.sub(
        r"[^A-Za-z0-9_-]+",
        "_",
        nome_pet_arquivo
    ).strip("_")

    if not nome_pet_arquivo:
        nome_pet_arquivo = "Pet"

    if historico.data_atendimento:
        data_arquivo = historico.data_atendimento.strftime("%d-%m-%Y")
    else:
        data_arquivo = "sem_data"

    nome_arquivo = (
        f"Receita_Veterinaria_"
        f"{nome_pet_arquivo}_"
        f"{data_arquivo}.pdf"
    )

    return send_file(
        buffer,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=nome_arquivo
    )
    
# =========================================================
# VISUALIZAR COMPROVANTE DE ATENDIMENTO
# =========================================================

@historico_bp.route("/<int:historico_id>/comprovante")
@login_required
def comprovante(historico_id):

    historico = (
        Historico.query
        .join(Pet, Historico.pet_id == Pet.id)
        .filter(
            Historico.id == historico_id,
            Pet.tutor_id == current_user.id
        )
        .first_or_404()
    )

    return render_template(
        "historico/comprovante.html",
        historico=historico
    )


# =========================================================
# BAIXAR COMPROVANTE EM PDF
# =========================================================

@historico_bp.route("/<int:historico_id>/comprovante/pdf")
@login_required
def baixar_comprovante_pdf(historico_id):

    historico = (
        Historico.query
        .join(Pet, Historico.pet_id == Pet.id)
        .filter(
            Historico.id == historico_id,
            Pet.tutor_id == current_user.id
        )
        .first_or_404()
    )

    buffer = BytesIO()

    documento = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=16 * mm,
        bottomMargin=18 * mm,
        title=f"Comprovante de Atendimento - {historico.pet.nome}",
        author="AgendaPet Paranaguá"
    )

    estilos = getSampleStyleSheet()

    estilo_titulo = ParagraphStyle(
        "TituloComprovante",
        parent=estilos["Title"],
        fontName="Helvetica-Bold",
        fontSize=22,
        leading=26,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#087f5b"),
        spaceAfter=4
    )

    estilo_subtitulo = ParagraphStyle(
        "SubtituloComprovante",
        parent=estilos["Normal"],
        fontName="Helvetica",
        fontSize=11,
        leading=14,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#64748b"),
        spaceAfter=14
    )

    estilo_secao = ParagraphStyle(
        "SecaoComprovante",
        parent=estilos["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=15,
        textColor=colors.HexColor("#065f46"),
        spaceBefore=10,
        spaceAfter=7
    )

    estilo_rotulo = ParagraphStyle(
        "RotuloComprovante",
        parent=estilos["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#64748b")
    )

    estilo_valor = ParagraphStyle(
        "ValorComprovante",
        parent=estilos["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#1f2937")
    )

    estilo_destaque = ParagraphStyle(
        "DestaqueComprovante",
        parent=estilos["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#1f2937")
    )

    estilo_data = ParagraphStyle(
        "DataComprovante",
        parent=estilos["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        alignment=TA_RIGHT,
        textColor=colors.HexColor("#374151")
    )

    estilo_assinatura = ParagraphStyle(
        "AssinaturaComprovante",
        parent=estilos["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=14,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#111827")
    )

    elementos = []

    elementos.append(
        Paragraph("AgendaPet Paranaguá", estilo_titulo)
    )

    elementos.append(
        Paragraph(
            "Sistema de Agendamento Veterinário",
            estilo_subtitulo
        )
    )

    elementos.append(
        HRFlowable(
            width="100%",
            thickness=2,
            color=colors.HexColor("#087f5b"),
            spaceAfter=14
        )
    )

    elementos.append(
        Paragraph(
            "COMPROVANTE DE ATENDIMENTO VETERINÁRIO",
            estilo_secao
        )
    )

    elementos.append(
        Paragraph(
            f"Documento referente ao atendimento nº {historico.id}",
            estilo_subtitulo
        )
    )

    pet = historico.pet
    tutor = pet.tutor if pet else None
    veterinario = historico.veterinario

    nome_pet = pet.nome if pet and pet.nome else "Não informado"
    especie = pet.especie if pet and pet.especie else "Não informada"
    raca = pet.raca if pet and pet.raca else "Não informada"
    sexo = pet.sexo if pet and pet.sexo else "Não informado"

    nome_tutor = (
        tutor.nome
        if tutor and tutor.nome
        else "Não informado"
    )

    cpf_tutor = (
        tutor.cpf
        if tutor and tutor.cpf
        else "Não informado"
    )

    telefone_tutor = (
        tutor.telefone
        if tutor and tutor.telefone
        else "Não informado"
    )

    nome_veterinario = (
        veterinario.nome
        if veterinario and veterinario.nome
        else "Não informado"
    )

    crmv = (
        getattr(veterinario, "crmv", None)
        if veterinario
        else None
    ) or "Não informado"

    if historico.data_atendimento:
        data_atendimento = historico.data_atendimento.strftime(
            "%d/%m/%Y"
        )
    else:
        data_atendimento = "Não informada"

    tipo_atendimento = (
        historico.tipo_atendimento
        or "Atendimento veterinário"
    )

    elementos.append(
        Paragraph("DADOS DO ATENDIMENTO", estilo_secao)
    )

    tabela_atendimento = Table(
        [
            [
                Paragraph("NÚMERO DO ATENDIMENTO", estilo_rotulo),
                Paragraph("DATA", estilo_rotulo),
            ],
            [
                Paragraph(str(historico.id), estilo_destaque),
                Paragraph(data_atendimento, estilo_destaque),
            ],
            [
                Paragraph("TIPO DE ATENDIMENTO", estilo_rotulo),
                Paragraph("STATUS", estilo_rotulo),
            ],
            [
                Paragraph(tipo_atendimento, estilo_valor),
                Paragraph("Concluído", estilo_destaque),
            ],
        ],
        colWidths=[87 * mm, 87 * mm]
    )

    tabela_atendimento.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
            ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#dbe3e8")),
            ("INNERGRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#e2e8f0")),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 7),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ])
    )

    elementos.append(tabela_atendimento)

    elementos.append(
        Paragraph("DADOS DO PACIENTE", estilo_secao)
    )

    tabela_pet = Table(
        [
            [
                Paragraph("NOME DO PET", estilo_rotulo),
                Paragraph("ESPÉCIE", estilo_rotulo),
            ],
            [
                Paragraph(nome_pet, estilo_destaque),
                Paragraph(especie, estilo_valor),
            ],
            [
                Paragraph("RAÇA", estilo_rotulo),
                Paragraph("SEXO", estilo_rotulo),
            ],
            [
                Paragraph(raca, estilo_valor),
                Paragraph(sexo, estilo_valor),
            ],
        ],
        colWidths=[87 * mm, 87 * mm]
    )

    tabela_pet.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
            ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#dbe3e8")),
            ("INNERGRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#e2e8f0")),
            ("TOPPADDING", (0, 0), (-1, -1), 7),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ])
    )

    elementos.append(tabela_pet)

    elementos.append(
        Paragraph("DADOS DO TUTOR", estilo_secao)
    )

    tabela_tutor = Table(
        [
            [
                Paragraph("NOME COMPLETO", estilo_rotulo),
                Paragraph(nome_tutor, estilo_destaque),
            ],
            [
                Paragraph("CPF", estilo_rotulo),
                Paragraph(cpf_tutor, estilo_valor),
            ],
            [
                Paragraph("TELEFONE", estilo_rotulo),
                Paragraph(telefone_tutor, estilo_valor),
            ],
        ],
        colWidths=[45 * mm, 129 * mm]
    )

    tabela_tutor.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#eef7f5")),
            ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#dbe3e8")),
            ("INNERGRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#e2e8f0")),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ])
    )

    elementos.append(tabela_tutor)

    elementos.append(
        Paragraph("RESPONSÁVEL PELO ATENDIMENTO", estilo_secao)
    )

    tabela_veterinario = Table(
        [
            [
                Paragraph("MÉDICO(A)-VETERINÁRIO(A)", estilo_rotulo),
                Paragraph("CRMV-PR", estilo_rotulo),
            ],
            [
                Paragraph(nome_veterinario, estilo_destaque),
                Paragraph(crmv, estilo_valor),
            ],
        ],
        colWidths=[120 * mm, 54 * mm]
    )

    tabela_veterinario.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
            ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#dbe3e8")),
            ("INNERGRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#e2e8f0")),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ])
    )

    elementos.append(tabela_veterinario)

    elementos.append(
        Paragraph("RESUMO DO ATENDIMENTO", estilo_secao)
    )

    diagnostico = (
        historico.diagnostico
        or "Não informado."
    )

    observacoes = (
        historico.observacoes
        or "Nenhuma observação registrada."
    )

    resumo_html = (
        f"<b>Diagnóstico:</b><br/>{diagnostico.replace(chr(10), '<br/>')}"
        f"<br/><br/>"
        f"<b>Observações:</b><br/>{observacoes.replace(chr(10), '<br/>')}"
    )

    tabela_resumo = Table(
        [[Paragraph(resumo_html, estilo_valor)]],
        colWidths=[174 * mm],
        minRowHeights=[35 * mm]
    )

    tabela_resumo.setStyle(
        TableStyle([
            ("BOX", (0, 0), (-1, -1), 0.7, colors.HexColor("#94a3b8")),
            ("LINEBEFORE", (0, 0), (0, -1), 4, colors.HexColor("#087f5b")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING", (0, 0), (-1, -1), 11),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 11),
            ("LEFTPADDING", (0, 0), (-1, -1), 12),
            ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ])
    )

    elementos.append(tabela_resumo)
    elementos.append(Spacer(1, 18))

    elementos.append(
        Paragraph(
            f"Paranaguá, {data_atendimento}.",
            estilo_data
        )
    )

    elementos.append(Spacer(1, 35))

    bloco_assinatura = KeepTogether([
        HRFlowable(
            width=90 * mm,
            thickness=0.7,
            color=colors.black,
            hAlign="CENTER",
            spaceAfter=6
        ),
        Paragraph(
            f"Dr(a). {nome_veterinario}",
            estilo_assinatura
        ),
        Paragraph(
            f"CRMV-PR: {crmv}",
            estilo_assinatura
        ),
    ])

    elementos.append(bloco_assinatura)
    elementos.append(Spacer(1, 14))

    elementos.append(
        HRFlowable(
            width="100%",
            thickness=0.5,
            color=colors.HexColor("#dbe3e8"),
            spaceAfter=6
        )
    )

    elementos.append(
        Paragraph(
            "AgendaPet Paranaguá — Comprovante emitido eletronicamente.",
            estilo_subtitulo
        )
    )

    documento.build(elementos)

    buffer.seek(0)

    nome_pet_arquivo = nome_pet

    nome_pet_arquivo = unicodedata.normalize(
        "NFKD",
        nome_pet_arquivo
    ).encode(
        "ASCII",
        "ignore"
    ).decode(
        "ASCII"
    )

    nome_pet_arquivo = re.sub(
        r"[^A-Za-z0-9_-]+",
        "_",
        nome_pet_arquivo
    ).strip("_")

    if not nome_pet_arquivo:
        nome_pet_arquivo = "Pet"

    if historico.data_atendimento:
        data_arquivo = historico.data_atendimento.strftime(
            "%d-%m-%Y"
        )
    else:
        data_arquivo = "sem_data"

    nome_arquivo = (
        f"Comprovante_Atendimento_"
        f"{nome_pet_arquivo}_"
        f"{data_arquivo}.pdf"
    )

    return send_file(
        buffer,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=nome_arquivo
    )