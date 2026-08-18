from app import create_app, db

from app.models.arquivo import Arquivo
from app.services.storage_service import StorageService


app = create_app()


def definir_pasta(arquivo):
    """
    Define onde o arquivo será salvo.

    Nesta primeira migração usamos uma pasta
    genérica para os arquivos antigos.
    """

    return f"migrados/{arquivo.id}"


def migrar():

    with app.app_context():

        arquivos = Arquivo.query.order_by(
            Arquivo.id.asc()
        ).all()

        total = len(arquivos)

        migrados = 0
        ignorados = 0
        erros = 0

        print(
            f"\nTotal de registros encontrados: {total}\n"
        )

        for arquivo in arquivos:

            print(
                f"Processando arquivo ID {arquivo.id}..."
            )

            try:

                # ==========================================
                # JÁ MIGRADO
                # ==========================================

                if arquivo.caminho:

                    print(
                        "  Já possui caminho. Ignorado."
                    )

                    ignorados += 1
                    continue

                # ==========================================
                # SEM DADOS BINÁRIOS
                # ==========================================

                if not arquivo.dados:

                    print(
                        "  Sem dados binários. Ignorado."
                    )

                    ignorados += 1
                    continue

                pasta = definir_pasta(
                    arquivo
                )

                # ==========================================
                # IMAGEM PRINCIPAL
                # ==========================================

                caminho = StorageService.salvar(
                    dados=arquivo.dados,
                    pasta=pasta,
                    extensao=(
                        arquivo.extensao
                        or "webp"
                    )
                )

                # ==========================================
                # MINIATURA
                # ==========================================

                caminho_miniatura = None

                if arquivo.miniatura:

                    caminho_miniatura = (
                        StorageService.salvar(
                            dados=arquivo.miniatura,
                            pasta=f"{pasta}/miniaturas",
                            extensao=(
                                arquivo.extensao
                                or "webp"
                            )
                        )
                    )

                # ==========================================
                # SALVAR CAMINHOS NO BANCO
                # ==========================================

                arquivo.caminho = caminho

                arquivo.caminho_miniatura = (
                    caminho_miniatura
                )

                db.session.commit()

                migrados += 1

                print(
                    f"  Migrado: {caminho}"
                )

            except Exception as erro:

                db.session.rollback()

                erros += 1

                print(
                    f"  ERRO: {erro}"
                )

        print("\n====================================")
        print("MIGRAÇÃO FINALIZADA")
        print("====================================")
        print(f"Total:     {total}")
        print(f"Migrados:  {migrados}")
        print(f"Ignorados: {ignorados}")
        print(f"Erros:     {erros}")
        print("====================================\n")


if __name__ == "__main__":
    migrar()