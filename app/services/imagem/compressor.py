from io import BytesIO

from PIL import Image, ImageOps

from .excecoes import CompressaoError

LARGURA_MAXIMA = 1200
ALTURA_MAXIMA = 1200

QUALIDADE_INICIAL = 82
QUALIDADE_MINIMA = 68

TAMANHO_MAXIMO_KB = 350


def comprimir_imagem(
    imagem: Image.Image,
    largura_maxima=LARGURA_MAXIMA,
    altura_maxima=ALTURA_MAXIMA,
    tamanho_maximo_kb=TAMANHO_MAXIMO_KB
):
    """
    Processa uma imagem para armazenamento.

    Retorna:
        dict
    """

    if imagem is None:
        raise CompressaoError(
            "Imagem inválida."
        )

    try:

        orientacao_corrigida = False

        imagem, orientacao_corrigida = _corrigir_orientacao(
            imagem
        )

        imagem = _converter_para_rgb(imagem)

        imagem.thumbnail(
            (
                largura_maxima,
                altura_maxima
            ),
            Image.Resampling.LANCZOS
        )

        dados, qualidade = _salvar_webp(
            imagem,
            tamanho_maximo_kb
        )

        return {

            "dados": dados,

            "tamanho_bytes": len(dados),

            "largura": imagem.width,

            "altura": imagem.height,

            "qualidade": qualidade,

            "modelo_compactacao": "WEBP_LOSSY",

            "orientacao_corrigida": orientacao_corrigida

        }

    except CompressaoError:
        raise

    except Exception as erro:

        raise CompressaoError(
            f"Erro ao comprimir imagem: {erro}"
        ) from erro


def _corrigir_orientacao(
    imagem: Image.Image
) -> tuple[Image.Image, bool]:
    """
    Corrige a orientação conforme os metadados EXIF.
    """

    try:
        exif = imagem.getexif()

        orientacao = exif.get(
            274,
            1
        )

        precisa_corrigir = orientacao not in (
            None,
            1
        )

        imagem_corrigida = ImageOps.exif_transpose(
            imagem
        )

        return (
            imagem_corrigida,
            precisa_corrigir
        )

    except Exception:
        return imagem, False


def _converter_para_rgb(imagem):

    if imagem.mode == "RGB":
        return imagem

    if imagem.mode in ("RGBA", "LA"):

        fundo = Image.new(
            "RGB",
            imagem.size,
            (255, 255, 255)
        )

        fundo.paste(
            imagem,
            mask=imagem.getchannel("A")
        )

        return fundo

    if imagem.mode == "P":

        imagem = imagem.convert("RGBA")

        fundo = Image.new(
            "RGB",
            imagem.size,
            (255, 255, 255)
        )

        fundo.paste(
            imagem,
            mask=imagem.getchannel("A")
        )

        return fundo

    return imagem.convert("RGB")


def _salvar_webp(
    imagem,
    tamanho_maximo_kb
):

    limite = tamanho_maximo_kb * 1024

    melhor = None

    qualidade_final = QUALIDADE_INICIAL

    for qualidade in range(
        QUALIDADE_INICIAL,
        QUALIDADE_MINIMA - 1,
        -2
    ):

        buffer = BytesIO()

        imagem.save(

            buffer,

            format="WEBP",

            quality=qualidade,

            optimize=True,

            method=6

        )

        dados = buffer.getvalue()

        melhor = dados

        qualidade_final = qualidade

        if len(dados) <= limite:
            break

    if melhor is None:

        raise CompressaoError(
            "Falha ao gerar WebP."
        )

    return melhor, qualidade_final