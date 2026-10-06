"""Dimensionamento de salas e alocação heurística com capacidades fixas."""

from src.modelo import Aula


def _validar(aulas, salas):
    if len(aulas) != len(salas) or any(type(sala) is not int or sala < 0 for sala in salas):
        raise ValueError("a alocação deve ter um inteiro não negativo por aula")
    if any(type(aula.vagas) is not int or aula.vagas < 0 for aula in aulas):
        raise ValueError("vagas devem ser inteiros não negativos")


def _validar_capacidades(capacidades):
    if any(type(capacidade) is not int or capacidade < 0 for capacidade in capacidades):
        raise ValueError("capacidades devem ser inteiros não negativos")


def capacidades_minimas(aulas: list[Aula], salas: list[int]) -> list[int]:
    """Máximo de vagas por sala em toda a semana, para uma alocação dada.

    O índice é o identificador físico da sala; salas não usadas têm zero.
    O resultado não é um inventário real nem minimiza a soma de capacidades.
    Tempo O(n + s), com s igual ao maior identificador de sala mais um.
    """
    _validar(aulas, salas)
    minimas = [0] * (max(salas, default=-1) + 1)
    for aula, sala in zip(aulas, salas):
        minimas[sala] = max(minimas[sala], aula.vagas)
    return minimas


def excessos_de_capacidade(aulas: list[Aula], salas: list[int], capacidades: list[int]) -> list[int]:
    """Índices das aulas cujas vagas excedem a capacidade da sala atribuída."""
    _validar(aulas, salas)
    _validar_capacidades(capacidades)
    if any(sala >= len(capacidades) for sala in salas):
        raise ValueError("a alocação referencia uma sala sem capacidade informada")
    return [i for i, (aula, sala) in enumerate(zip(aulas, salas))
            if aula.vagas > capacidades[sala]]


def alocar_com_capacidade(aulas: list[Aula], capacidades: list[int]) -> list[int]:
    """Best fit: usa a menor sala livre que comporte as vagas da aula.

    ``capacidades[i]`` descreve a sala física i, reutilizada entre dias.
    Processa por dia e início, priorizando mais vagas nos empates de início.
    Retorna list[int] na ordem original, sem alterar as entradas.
    Tempo O(n log n + n*s), sendo s a quantidade de salas disponíveis.

    Esta heurística não garante otimalidade nem encontrar toda alocação
    viável. Se falhar, gera ValueError; isso não prova inviabilidade.
    """
    _validar(aulas, [0] * len(aulas))
    _validar_capacidades(capacidades)
    ordem_salas = sorted(range(len(capacidades)), key=lambda sala: (capacidades[sala], sala))
    ordem_aulas = sorted(range(len(aulas)),
                         key=lambda i: (aulas[i].dia, aulas[i].inicio, -aulas[i].vagas))
    salas = [0] * len(aulas)
    liberacoes = {}
    for indice in ordem_aulas:
        aula = aulas[indice]
        fins = liberacoes.setdefault(aula.dia, [0] * len(capacidades))
        for sala in ordem_salas:
            if capacidades[sala] >= aula.vagas and fins[sala] <= aula.inicio:
                salas[indice] = sala
                fins[sala] = aula.fim
                break
        else:
            raise ValueError(f"a heurística de capacidade não conseguiu alocar a turma "
                             f"{aula.turma!r}; isso não prova inviabilidade do inventário")
    return salas
