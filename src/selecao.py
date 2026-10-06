"""Seleção do maior número de reservas para um auditório em um único dia."""

from src.modelo import Aula


def selecionar(pedidos: list[Aula]) -> list[Aula]:
    """Retorna uma seleção de cardinalidade máxima, ordenada por fim.

    Cada pedido usa o modelo ``Aula``. Todos devem pertencer ao mesmo dia;
    uma entrada com dias diferentes gera ``ValueError``. A lista vazia
    resulta em uma seleção vazia. A lista recebida não é modificada.

    Ordena por menor horário de fim e aceita cada pedido cujo início seja
    maior ou igual ao fim do último aceito. Intervalos encostados são
    compatíveis. Empates de fim preservam a ordem original dos pedidos.
    O objetivo é maximizar a quantidade de reservas, independentemente
    de suas vagas ou duração. Tempo O(n log n) e espaço O(n).
    """
    if len({pedido.dia for pedido in pedidos}) > 1:
        raise ValueError("os pedidos de reserva devem pertencer ao mesmo dia")

    selecionados = []
    ultimo_fim = 0
    for pedido in sorted(pedidos, key=lambda pedido: pedido.fim):
        if pedido.inicio >= ultimo_fim:
            selecionados.append(pedido)
            ultimo_fim = pedido.fim
    return selecionados
