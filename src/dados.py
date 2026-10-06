"""Carrega a oferta de turmas em CSV e relata os registros descartados."""

import csv
import sys
from pathlib import Path

from src.horarios import aulas_da_turma
from src.modelo import Aula


def carregar_aulas(caminho: str | Path) -> list[Aula]:
    """Lê um CSV UTF-8 (com ou sem BOM) com turma, disciplina, horario e vagas.

    Preserva a ordem das turmas e usa ``aulas_da_turma`` para os encontros.
    Turmas sem horário, com código inválido ou com dados incompletos são
    descartadas e contadas. Os motivos e o resumo são escritos em stderr.
    Vagas devem ser inteiros não negativos; valores inválidos não viram zero.
    Arquivo inexistente e cabeçalho inválido geram exceções ao chamador.
    """
    aulas = []
    total = sem_horario = horarios_invalidos = linhas_invalidas = 0
    with Path(caminho).open(encoding="utf-8-sig", newline="") as arquivo:
        leitor = csv.DictReader(arquivo)
        campos = leitor.fieldnames or []
        obrigatorios = {"turma", "disciplina", "horario", "vagas"}
        if not obrigatorios.issubset(campos) or len(campos) != len(set(campos)):
            raise ValueError(
                "cabeçalho CSV inválido: requer turma, disciplina, horario e vagas "
                "sem colunas duplicadas"
            )

        for registro in leitor:
            total += 1
            linha = leitor.line_num
            if (None in registro or any(valor is None for valor in registro.values())
                    or not registro["turma"].strip() or not registro["disciplina"].strip()):
                linhas_invalidas += 1
                print(f"Linha {linha}: registro incompleto ou com campos excedentes; ignorado.",
                      file=sys.stderr)
                continue

            turma = registro["turma"].strip()
            codigo = registro["horario"].strip()
            if not codigo:
                sem_horario += 1
                print(f"Linha {linha}, turma {turma}: sem horário; ignorada.", file=sys.stderr)
                continue

            try:
                vagas = int(registro["vagas"])
                if vagas < 0:
                    raise ValueError("vagas negativas")
            except ValueError:
                linhas_invalidas += 1
                print(f"Linha {linha}, turma {turma}: vagas inválidas "
                      f"{registro['vagas']!r}; ignorada.", file=sys.stderr)
                continue

            try:
                encontros = aulas_da_turma(turma, codigo, vagas)
            except ValueError as erro:
                horarios_invalidos += 1
                print(f"Linha {linha}, turma {turma}: horário inválido "
                      f"{codigo!r} ({erro}); ignorada.", file=sys.stderr)
                continue
            aulas.extend(encontros)

    validas = total - sem_horario - horarios_invalidos - linhas_invalidas
    print(f"Turmas lidas: {total}; válidas: {validas}; sem horário: {sem_horario}; "
          f"horários inválidos: {horarios_invalidos}; linhas inválidas: {linhas_invalidas}; "
          f"aulas geradas: {len(aulas)}.", file=sys.stderr)
    return aulas
