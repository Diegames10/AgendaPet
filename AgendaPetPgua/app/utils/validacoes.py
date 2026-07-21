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