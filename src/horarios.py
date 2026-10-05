"""Converte os horários do SIGAA em intervalos de minutos.

Tabela de horários da UnB, conforme publicada pelo Departamento de Design
(design.unb.br/codigos-aulas-sigaa).
"""

from itertools import groupby

from src.modelo import Aula, ler_codigo


def _min(hhmm: str) -> int:
    h, m = hhmm.split(":")
    return int(h) * 60 + int(m)


TABELA = {
    ("M", 1): ("08:00", "08:55"),
    ("M", 2): ("08:55", "09:50"),
    ("M", 3): ("10:00", "10:55"),
    ("M", 4): ("10:55", "11:50"),
    ("M", 5): ("12:00", "12:55"),
    ("T", 1): ("12:55", "13:50"),
    ("T", 2): ("14:00", "14:55"),
    ("T", 3): ("14:55", "15:50"),
    ("T", 4): ("16:00", "16:55"),
    ("T", 5): ("16:55", "17:50"),
    ("T", 6): ("18:00", "18:55"),
    # A fonte publica N1 como 19:00–19:55, mas N2 começa às 19:50; tratamos
    # como erro de digitação, senão N1 e N2 de turmas diferentes conflitariam.
    ("N", 1): ("19:00", "19:50"),
    ("N", 2): ("19:50", "20:40"),
    ("N", 3): ("20:50", "21:40"),
    ("N", 4): ("21:40", "22:30"),
}

INTERVALOS = {chave: (_min(a), _min(b)) for chave, (a, b) in TABELA.items()}
ORDEM = list(TABELA)


def aulas_da_turma(turma: str, codigo: str, vagas: int = 0) -> list[Aula]:
    """Transforma o código de horário de uma turma nas suas aulas da semana.

    Horários consecutivos no mesmo dia viram uma aula só, do início do
    primeiro ao fim do último: a turma ocupa a sala também no intervalo
    entre eles (``M2`` termina 09:50, ``M3`` começa 10:00).

    >>> [(a.dia, a.inicio, a.fim) for a in aulas_da_turma("X", "35T23")]
    [(3, 840, 950), (5, 840, 950)]
    """
    aulas = []
    for dia, trincas in groupby(ler_codigo(codigo), key=lambda t: t[0]):
        posicoes = [ORDEM.index((turno, h)) for _, turno, h in trincas]
        bloco = [posicoes[0]]
        for p in posicoes[1:]:
            if p == bloco[-1] + 1:
                bloco.append(p)
            else:
                aulas.append(_aula(turma, dia, bloco, vagas))
                bloco = [p]
        aulas.append(_aula(turma, dia, bloco, vagas))
    return aulas


def _aula(turma: str, dia: int, bloco: list[int], vagas: int) -> Aula:
    inicio = INTERVALOS[ORDEM[bloco[0]]][0]
    fim = INTERVALOS[ORDEM[bloco[-1]]][1]
    return Aula(turma, dia, inicio, fim, vagas)
