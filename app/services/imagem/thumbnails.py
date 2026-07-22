from io import BytesIO

from PIL import Image, ImageOps

from .excecoes import CompressaoError


TAMANHO_MINIATURA = (300, 300)
QUALIDADE_INICIAL = 82
QUALIDADE_MINIMA = 68
TAMANHO_MAXIMO_KB = 60


def gerar_miniatura(
    imagem: Image.Image,
    tamanho: tuple[int, int] = TAMANHO_MINIATURA,
    tamanho_maximo_kb: int = TAMANHO_MAXIMO_KB
) -> dict:
    """
    Gera uma miniatura quadrada em WebP.

    A imagem é centralizada e recortada para preencher
    completamente o tamanho definido.

    Args:
        imagem: objeto PIL já validado e corrigido.
        tamanho: largura e altura da miniatura.
        tamanho_maximo_kb: limite desejado em KB.

    Returns:
        Dicionário com os bytes e metadados da miniatura.
    """

    if imagem is None:
        raise CompressaoError(
            "Não foi possível gerar a miniatura."
        )

    try:
        miniatura = imagem.copy()

        miniatura = ImageOps.fit(
            miniatura,
            tamanho,
            method=Image.Resampling.LANCZOS,
            centering=(0.5, 0.5)
        )

        miniatura = _converter_para_rgb(miniatura)

        dados, qualidade_utilizada = _salvar_com_limite(
            miniatura,
            tamanho_maximo_kb
        )

        return {
            "dados": dados,
            "tamanho_bytes": len(dados),
            "largura": miniatura.width,
            "altura": miniatura.height,
            "qualidade": qualidade_utilizada
        }

    except CompressaoError:
        raise

    except Exception as erro:
        raise CompressaoError(
            f"Erro ao gerar miniatura: {erro}"
        ) from erro


def _salvar_com_limite(
    imagem: Image.Image,
    tamanho_maximo_kb: int
) -> tuple[bytes, int]:
    """
    Salva uma imagem WebP reduzindo a qualidade progressivamente.
    """

    limite_bytes = tamanho_maximo_kb * 1024
    melhor_resultado = None
    qualidade_utilizada = QUALIDADE_INICIAL

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
            method=6,
            optimize=True
        )

        dados = buffer.getvalue()

        melhor_resultado = dados
        qualidade_utilizada = qualidade

        if len(dados) <= limite_bytes:
            break

    if melhor_resultado is None:
        raise CompressaoError(
            "Não foi possível gerar os dados da miniatura."
        )

    return melhor_resultado, qualidade_utilizada


def _converter_para_rgb(
    imagem: Image.Image
) -> Image.Image:
    """
    Converte a imagem para RGB tratando transparência.
    """

    if imagem.mode == "RGB":
        return imagem

    if imagem.mode in ("RGBA", "LA"):
        fundo = Image.new(
            "RGB",
            imagem.size,
            (255, 255, 255)
        )

        canal_alpha = imagem.getchannel("A")

        fundo.paste(
            imagem,
            mask=canal_alpha
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