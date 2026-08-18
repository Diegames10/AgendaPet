from pathlib import Path
from uuid import uuid4

from flask import current_app


class StorageService:
    """
    Serviço responsável pelo armazenamento físico
    dos arquivos do AgendaPet.

    Em desenvolvimento:
        storage/

    Em produção no Render:
        /data/agendapet/
    """

    @staticmethod
    def raiz() -> Path:

        caminho = Path(
            current_app.config["STORAGE_PATH"]
        )

        caminho.mkdir(
            parents=True,
            exist_ok=True
        )

        return caminho

    @classmethod
    def salvar(
        cls,
        dados: bytes,
        pasta: str,
        extensao: str
    ) -> str:

        if not dados:
            raise ValueError(
                "Não há dados para armazenar."
            )

        extensao = extensao.lower().lstrip(".")

        diretorio = cls.raiz() / pasta

        diretorio.mkdir(
            parents=True,
            exist_ok=True
        )

        nome_arquivo = (
            f"{uuid4().hex}.{extensao}"
        )

        caminho_fisico = (
            diretorio / nome_arquivo
        )

        caminho_fisico.write_bytes(dados)

        caminho_relativo = (
            caminho_fisico.relative_to(
                cls.raiz()
            )
        )

        return caminho_relativo.as_posix()

    @classmethod
    def obter_caminho(
        cls,
        caminho_relativo: str
    ) -> Path:

        if not caminho_relativo:
            raise ValueError(
                "Caminho do arquivo não informado."
            )

        raiz = cls.raiz().resolve()

        caminho = (
            raiz / caminho_relativo
        ).resolve()

        if caminho != raiz and raiz not in caminho.parents:
            raise ValueError(
                "Caminho de armazenamento inválido."
            )

        return caminho

    @classmethod
    def existe(
        cls,
        caminho_relativo: str
    ) -> bool:

        if not caminho_relativo:
            return False

        try:
            return cls.obter_caminho(
                caminho_relativo
            ).is_file()

        except ValueError:
            return False

    @classmethod
    def excluir(
        cls,
        caminho_relativo: str
    ) -> bool:

        if not caminho_relativo:
            return False

        try:
            caminho = cls.obter_caminho(
                caminho_relativo
            )

        except ValueError:
            return False

        if not caminho.is_file():
            return False

        caminho.unlink()

        return True