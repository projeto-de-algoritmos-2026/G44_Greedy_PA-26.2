"""Estratégias de comparação por primeira sala compatível, em O(n²)."""

from src.modelo import Aula


def _primeira_compativel(aulas: list[Aula], ordem: list[int]) -> list[int]:
    """Testa todas as aulas já colocadas na sala, mesmo fora da ordem temporal."""
    ocupacoes: list[list[Aula]] = []
    salas = [0] * len(aulas)
    for indice in ordem:
        aula = aulas[indice]
        for sala, encontros in enumerate(ocupacoes):
            if all(not aula.sobrepoe(outra) for outra in encontros):
                encontros.append(aula)
                salas[indice] = sala
                break
        else:
            salas[indice] = len(ocupacoes)
            ocupacoes.append([aula])
    return salas


def ordem_entrada(aulas: list[Aula]) -> list[int]:
    """Aloca na ordem recebida, usando a primeira sala compatível."""
    return _primeira_compativel(aulas, list(range(len(aulas))))


def menor_fim(aulas: list[Aula]) -> list[int]:
    """Processa primeiro as aulas que terminam mais cedo."""
    ordem = sorted(range(len(aulas)), key=lambda i: aulas[i].fim)
    return _primeira_compativel(aulas, ordem)


def maior_duracao(aulas: list[Aula]) -> list[int]:
    """Processa primeiro os intervalos mais longos."""
    ordem = sorted(range(len(aulas)), key=lambda i: aulas[i].fim - aulas[i].inicio,
                   reverse=True)
    return _primeira_compativel(aulas, ordem)


# Todas devolvem list[int] na ordem original e compartilham salas entre dias.
# São heurísticas de comparação, sem garantia de minimizar o número de salas.
ESTRATEGIAS = {
    "ordem_entrada": ordem_entrada,
    "menor_fim": menor_fim,
    "maior_duracao": maior_duracao,
}
