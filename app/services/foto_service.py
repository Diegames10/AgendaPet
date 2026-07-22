from app import db

from app.models.foto_usuario import FotoUsuario
from app.models.foto_pet import FotoPet

from app.services.upload_service import UploadService


class FotoService:
    """
    Serviço responsável pelos vínculos entre imagens,
    usuários e pets.

    O commit da transação deve ser realizado pela rota.
    """

    LIMITE_FOTOS_PET = 3

    # =====================================================
    # FOTO DO USUÁRIO
    # =====================================================

    @staticmethod
    def salvar_foto_usuario(usuario, file_storage):
        """
        Substitui a foto de perfil do usuário.

        Caso já exista uma foto, o vínculo anterior será
        removido juntamente com o arquivo órfão.
        """

        if usuario.foto_perfil:

            db.session.delete(
                usuario.foto_perfil
            )

            db.session.flush()

        arquivo = UploadService.criar_arquivo(
            file_storage
        )

        foto = FotoUsuario(
            usuario=usuario,
            arquivo=arquivo
        )

        db.session.add(foto)
        db.session.flush()

        return foto

    # =====================================================
    # ADICIONAR FOTO AO PET
    # =====================================================

    @staticmethod
    def salvar_foto_pet(
        pet,
        file_storage,
        descricao=None
    ):
        """
        Adiciona uma nova foto ao pet.

        Regras:
        - no máximo três fotos;
        - ocupa automaticamente a primeira posição disponível;
        - a primeira foto do pet torna-se principal.
        """

        fotos_atuais = list(pet.fotos or [])

        if len(fotos_atuais) >= FotoService.LIMITE_FOTOS_PET:

            raise ValueError(
                "O pet já possui o limite máximo de 3 fotos."
            )

        posicoes_ocupadas = {
            foto.posicao
            for foto in fotos_atuais
        }

        posicao_disponivel = next(
            (
                posicao
                for posicao in range(
                    1,
                    FotoService.LIMITE_FOTOS_PET + 1
                )
                if posicao not in posicoes_ocupadas
            ),
            None
        )

        if posicao_disponivel is None:

            raise ValueError(
                "Não foi possível determinar uma posição para a foto."
            )

        arquivo = UploadService.criar_arquivo(
            file_storage
        )

        primeira_foto = len(fotos_atuais) == 0

        foto = FotoPet(
            pet=pet,
            arquivo=arquivo,
            posicao=posicao_disponivel,
            principal=primeira_foto,
            descricao=descricao or None
        )

        db.session.add(foto)
        db.session.flush()

        return foto

    # =====================================================
    # SALVAR VÁRIAS FOTOS
    # =====================================================

    @staticmethod
    def salvar_fotos_pet(
        pet,
        arquivos
    ):
        """
        Salva várias fotos enviadas para o pet.

        Arquivos vazios são ignorados.
        """

        arquivos_validos = [
            arquivo
            for arquivo in arquivos
            if arquivo
            and arquivo.filename
        ]

        quantidade_disponivel = (
            FotoService.LIMITE_FOTOS_PET
            - len(pet.fotos or [])
        )

        if len(arquivos_validos) > quantidade_disponivel:

            raise ValueError(
                f"Você pode adicionar somente "
                f"{quantidade_disponivel} foto(s) a este pet."
            )

        fotos_criadas = []

        for arquivo in arquivos_validos:

            foto = FotoService.salvar_foto_pet(
                pet=pet,
                file_storage=arquivo
            )

            fotos_criadas.append(foto)

        return fotos_criadas

    # =====================================================
    # SUBSTITUIR FOTO
    # =====================================================

    @staticmethod
    def substituir_foto_pet(
        pet,
        foto_id,
        file_storage
    ):
        """
        Substitui o arquivo de uma foto, preservando:
        - posição;
        - indicador principal;
        - descrição.
        """

        foto = FotoService._buscar_foto_do_pet(
            pet=pet,
            foto_id=foto_id
        )

        posicao = foto.posicao
        principal = foto.principal
        descricao = foto.descricao

        db.session.delete(foto)
        db.session.flush()

        arquivo = UploadService.criar_arquivo(
            file_storage
        )

        nova_foto = FotoPet(
            pet=pet,
            arquivo=arquivo,
            posicao=posicao,
            principal=principal,
            descricao=descricao
        )

        db.session.add(nova_foto)
        db.session.flush()

        return nova_foto

    # =====================================================
    # DEFINIR FOTO PRINCIPAL
    # =====================================================

    @staticmethod
    def definir_foto_principal(
        pet,
        foto_id
    ):
        """
        Define uma foto como principal e desmarca as demais.
        """

        foto_principal = FotoService._buscar_foto_do_pet(
            pet=pet,
            foto_id=foto_id
        )

        for foto in pet.fotos:

            foto.principal = (
                foto.id == foto_principal.id
            )

        db.session.flush()

        return foto_principal

    # =====================================================
    # REMOVER FOTO
    # =====================================================

    @staticmethod
    def remover_foto_pet(
        pet,
        foto_id
    ):
        """
        Remove uma foto do pet.

        Caso a foto removida seja a principal, a primeira
        foto restante passa a ser principal.
        """

        foto = FotoService._buscar_foto_do_pet(
            pet=pet,
            foto_id=foto_id
        )

        era_principal = foto.principal

        db.session.delete(foto)
        db.session.flush()

        fotos_restantes = (
            FotoPet.query
            .filter_by(pet_id=pet.id)
            .order_by(FotoPet.posicao.asc())
            .all()
        )

        if era_principal and fotos_restantes:

            fotos_restantes[0].principal = True

        FotoService._reorganizar_posicoes(
            fotos_restantes
        )

        db.session.flush()

    # =====================================================
    # EXCLUIR TODAS AS FOTOS
    # =====================================================

    @staticmethod
    def excluir_todas_fotos_pet(pet):
        """
        Remove todas as fotos vinculadas ao pet.
        """

        for foto in list(pet.fotos or []):

            db.session.delete(foto)

        db.session.flush()

    # =====================================================
    # MÉTODOS INTERNOS
    # =====================================================

    @staticmethod
    def _buscar_foto_do_pet(
        pet,
        foto_id
    ):
        """
        Busca uma foto garantindo que ela pertence ao pet.
        """

        foto = FotoPet.query.filter_by(
            id=foto_id,
            pet_id=pet.id
        ).first()

        if foto is None:

            raise ValueError(
                "Foto não encontrada para este pet."
            )

        return foto

    @staticmethod
    def _reorganizar_posicoes(fotos):
        """
        Reorganiza as posições para 1, 2 e 3.
        """

        for indice, foto in enumerate(
            fotos,
            start=1
        ):

            foto.posicao = indice