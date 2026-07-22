from dataclasses import dataclass
from io import BytesIO
from pathlib import Path

from PIL import Image

from .compressor import comprimir_imagem
from .excecoes import ImagemInvalidaError
from .hash import gerar_hash_sha256
from .thumbnails import gerar_miniatura
from .validacao import validar_imagem


VERSAO_PROCESSADOR = "1.0"


@dataclass(frozen=True)
class ResultadoImagem:
    """
    Representa o resultado final do processamento de uma imagem.

    O objeto contém todos os dados necessários para criar
    um registro no modelo Arquivo.
    """

    nome_original: str
    tipo_mime: str
    extensao: str

    dados: bytes
    miniatura: bytes

    tamanho_bytes: int
    tamanho_miniatura_bytes: int

    largura: int
    altura: int

    largura_miniatura: int
    altura_miniatura: int

    hash_sha256: str

    qualidade: int
    modelo_compactacao: str
    versao_processador: str
    orientacao_corrigida: bool


def processar_imagem(file_storage) -> ResultadoImagem:
    """
    Executa todo o pipeline de processamento da imagem.

    Etapas:
        1. Validação do arquivo.
        2. Abertura da imagem com Pillow.
        3. Compressão da imagem principal.
        4. Geração da miniatura.
        5. Geração do hash SHA-256.
        6. Montagem do resultado final.

    Args:
        file_storage:
            Arquivo enviado por formulário Flask,
            normalmente um objeto FileStorage.

    Returns:
        ResultadoImagem:
            Dados prontos para persistência no banco.

    Raises:
        ImagemInvalidaError:
            Quando não for possível abrir ou processar a imagem.
    """

    validar_imagem(file_storage)

    nome_original = _obter_nome_original(file_storage)

    try:
        file_storage.seek(0)

        imagem = Image.open(file_storage)

        imagem.load()

        resultado_compressao = comprimir_imagem(
            imagem
        )

        imagem_processada = Image.open(
            BytesIO(resultado_compressao["dados"])
        )

        imagem_processada.load()

        resultado_miniatura = gerar_miniatura(
            imagem_processada
        )

        hash_sha256 = gerar_hash_sha256(
            resultado_compressao["dados"]
        )

        return ResultadoImagem(
            nome_original=nome_original,
            tipo_mime="image/webp",
            extensao="webp",

            dados=resultado_compressao["dados"],
            miniatura=resultado_miniatura["dados"],

            tamanho_bytes=resultado_compressao[
                "tamanho_bytes"
            ],
            tamanho_miniatura_bytes=resultado_miniatura[
                "tamanho_bytes"
            ],

            largura=resultado_compressao["largura"],
            altura=resultado_compressao["altura"],

            largura_miniatura=resultado_miniatura[
                "largura"
            ],
            altura_miniatura=resultado_miniatura[
                "altura"
            ],

            hash_sha256=hash_sha256,

            qualidade=resultado_compressao[
                "qualidade"
            ],
            modelo_compactacao=resultado_compressao[
                "modelo_compactacao"
            ],
            versao_processador=VERSAO_PROCESSADOR,
            orientacao_corrigida=resultado_compressao[
                "orientacao_corrigida"
            ]
        )

    except ImagemInvalidaError:
        raise

    except Exception as erro:
        raise ImagemInvalidaError(
            f"Não foi possível processar a imagem: {erro}"
        ) from erro

    finally:
        file_storage.seek(0)


def _obter_nome_original(file_storage) -> str:
    """
    Obtém e normaliza o nome original do arquivo.
    """

    nome = getattr(
        file_storage,
        "filename",
        None
    )

    if not nome:
        return "imagem"

    nome = Path(nome).name.strip()

    return nome or "imagem"