"""Modelo de uma aula e leitura do código de horário do SIGAA.

Um código como ``35T23`` diz: terça e quinta (3 e 5), à tarde (T),
no segundo e terceiro horários (2 e 3). Uma turma pode ter mais de um
bloco separado por espaço, como ``24M12 6T34``, e um bloco pode atravessar
turnos, como ``35M5T1``.
"""

import re
from dataclasses import dataclass

DIAS = {2: "segunda", 3: "terça", 4: "quarta", 5: "quinta", 6: "sexta", 7: "sábado"}
HORARIOS_POR_TURNO = {"M": 5, "T": 6, "N": 4}

_BLOCO = re.compile(r"([2-7]+)((?:[MTN][1-6]+)+)")
_TURNO = re.compile(r"([MTN])([1-6]+)")


@dataclass(frozen=True)
class Aula:
    """Um encontro de uma turma, num dia, num intervalo contínuo de tempo.

    O intervalo é semiaberto, ``[inicio, fim)``, em minutos desde 00:00:
    uma aula que termina às 10:00 não conflita com outra que começa às 10:00.
    """

    turma: str
    dia: int
    inicio: int
    fim: int
    vagas: int = 0

    def __post_init__(self):
        if self.dia not in DIAS:
            raise ValueError(f"dia inválido: {self.dia}")
        if not 0 <= self.inicio < self.fim <= 24 * 60:
            raise ValueError(f"intervalo inválido: [{self.inicio}, {self.fim})")

    def sobrepoe(self, outra: "Aula") -> bool:
        return self.dia == outra.dia and self.inicio < outra.fim and outra.inicio < self.fim


def ler_codigo(codigo: str) -> list[tuple[int, str, int]]:
    """Desmonta um código do SIGAA em trincas ``(dia, turno, horário)``.

    >>> ler_codigo("35T23")
    [(3, 'T', 2), (3, 'T', 3), (5, 'T', 2), (5, 'T', 3)]
    """
    partes = codigo.split()
    if not partes:
        raise ValueError("código de horário vazio")

    trincas = set()
    for parte in partes:
        bloco = _BLOCO.fullmatch(parte)
        if not bloco:
            raise ValueError(f"código de horário inválido: {parte!r}")
        dias, turnos = bloco.groups()
        for turno, horarios in _TURNO.findall(turnos):
            for h in horarios:
                if int(h) > HORARIOS_POR_TURNO[turno]:
                    raise ValueError(f"horário {turno}{h} não existe em {parte!r}")
                for d in dias:
                    trincas.add((int(d), turno, int(h)))

    ordem_turno = {"M": 0, "T": 1, "N": 2}
    return sorted(trincas, key=lambda t: (t[0], ordem_turno[t[1]], t[2]))
