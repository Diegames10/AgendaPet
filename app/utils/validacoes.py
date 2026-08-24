import re


def cpf_valido(cpf):

    cpf = re.sub(r"\D", "", cpf or "")

    if len(cpf) != 11:
        return False

    if cpf == cpf[0] * 11:
        return False

    soma = sum(
        int(cpf[indice]) * (10 - indice)
        for indice in range(9)
    )

    resto = soma % 11

    primeiro_digito = (
        0 if resto < 2 else 11 - resto
    )

    soma = sum(
        int(cpf[indice]) * (11 - indice)
        for indice in range(10)
    )

    resto = soma % 11

    segundo_digito = (
        0 if resto < 2 else 11 - resto
    )

    return cpf[-2:] == (
        f"{primeiro_digito}{segundo_digito}"
    )
    
def telefone_valido(telefone):

    if not telefone:
        return True

    numeros = re.sub(
        r"\D",
        "",
        telefone
    )

    # Fixo com DDD = 10 dígitos
    # Celular com DDD = 11 dígitos
    if len(numeros) not in (10, 11):
        return False

    # DDD não deve começar com 0
    if numeros[0] == "0":
        return False

    return True