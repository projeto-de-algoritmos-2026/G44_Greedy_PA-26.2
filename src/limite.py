"""Limite inferior para o número de salas: a profundidade do conjunto de aulas.

Se ``d`` aulas acontecem ao mesmo tempo, nenhuma alocação usa menos de ``d``
salas. O teorema do particionamento de intervalos diz que o guloso usa
exatamente ``d`` — então comparar os dois é a prova empírica de otimalidade.
"""

from src.modelo import Aula


def pico(aulas: list[Aula]) -> tuple[int, int | None, int | None]:
    """Devolve ``(profundidade, dia, minuto)`` do primeiro instante de pico.

    Varredura de eventos: cada aula abre em ``inicio`` e fecha em ``fim``.
    Num mesmo instante, os fechamentos vêm antes das aberturas, porque o
    intervalo é semiaberto. Para um conjunto vazio, ``(0, None, None)``.
    """
    eventos = []
    for a in aulas:
        eventos.append((a.dia, a.inicio, 1))
        eventos.append((a.dia, a.fim, -1))
    eventos.sort()

    atual, melhor, dia_pico, minuto_pico = 0, 0, None, None
    for dia, minuto, delta in eventos:
        atual += delta
        if atual > melhor:
            melhor, dia_pico, minuto_pico = atual, dia, minuto
    return melhor, dia_pico, minuto_pico


def profundidade(aulas: list[Aula]) -> int:
    return pico(aulas)[0]
