"""Particionamento ótimo de intervalos por início, usando um heap de salas."""

from heapq import heappush, heapreplace

from src.modelo import Aula


def alocar(aulas: list[Aula]) -> list[int]:
    """Devolve a sala de cada aula, na mesma ordem da lista recebida.

    Para cada dia, processa as aulas por início. O heap guarda ``(fim, sala)``
    do último encontro alocado a cada sala. Se a sala que libera primeiro
    estiver livre, ela é reutilizada; caso contrário, abre-se uma nova.
    ``fim <= inicio`` permite reutilizar a sala na borda de dois intervalos.

    A numeração começa em zero em cada dia: sala 0 de segunda e sala 0 de
    terça são a mesma sala. O total necessário é o maior total diário,
    igual à profundidade dos intervalos. Não altera a lista recebida.
    Tempo O(n log n) e espaço O(n).
    """
    por_dia: dict[int, list[tuple[int, Aula]]] = {}
    for indice, aula in enumerate(aulas):
        por_dia.setdefault(aula.dia, []).append((indice, aula))

    salas = [0] * len(aulas)
    for encontros in por_dia.values():
        encontros.sort(key=lambda encontro: encontro[1].inicio)
        heap: list[tuple[int, int]] = []
        for indice, aula in encontros:
            if heap and heap[0][0] <= aula.inicio:
                sala = heap[0][1]
                heapreplace(heap, (aula.fim, sala))
            else:
                sala = len(heap)
                heappush(heap, (aula.fim, sala))
            salas[indice] = sala

    return salas
