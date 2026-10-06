"""Busca exata do mínimo de salas por backtracking em instâncias pequenas."""

from src.modelo import Aula


MAX_AULAS = 12


def minimo_de_salas(aulas: list[Aula]) -> int:
    """Testa 1, 2, 3... salas até encontrar uma alocação sem conflitos.

    Em cada tentativa, atribui a próxima aula a todas as salas compatíveis
    e desfaz a atribuição quando o restante não pode ser alocado. Salas
    vazias são equivalentes, então basta tentar a primeira delas.

    Usa apenas ``Aula.sobrepoe``, sem depender do guloso ou da profundidade.
    Salas podem ser compartilhadas entre dias. Não altera a entrada.
    Retorna zero para uma lista vazia e rejeita mais de 12 aulas, pois a
    busca tem custo exponencial no pior caso.
    """
    if len(aulas) > MAX_AULAS:
        raise ValueError(f"a busca exata aceita no máximo {MAX_AULAS} aulas")
    if not aulas:
        return 0

    def cabe(quantidade: int) -> bool:
        salas: list[list[Aula]] = [[] for _ in range(quantidade)]

        def tentar(indice: int) -> bool:
            if indice == len(aulas):
                return True
            aula = aulas[indice]
            for sala in salas:
                if any(aula.sobrepoe(outra) for outra in sala):
                    continue
                sala.append(aula)
                if tentar(indice + 1):
                    return True
                sala.pop()
                if not sala:
                    # Trocar apenas os números de salas vazias não muda a solução.
                    break
            return False

        return tentar(0)

    for quantidade in range(1, len(aulas)):
        if cabe(quantidade):
            return quantidade
    # Uma sala por aula sempre é uma solução, mesmo no pior caso.
    return len(aulas)
