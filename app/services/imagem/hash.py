import hashlib


def gerar_hash_sha256(dados: bytes) -> str:
    """
    Gera o hash SHA-256 dos dados binários recebidos.

    Args:
        dados: conteúdo binário da imagem processada.

    Returns:
        Hash SHA-256 em formato hexadecimal.
    """

    if not dados:
        raise ValueError(
            "Não foi possível gerar o hash: dados vazios."
        )

    return hashlib.sha256(dados).hexdigest()