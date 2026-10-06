import random
import unittest
from itertools import combinations

from src.modelo import Aula
from src.selecao import selecionar


def maximo_por_forca_bruta(pedidos):
    """Enumera subconjuntos por tamanho, sem usar ordenação gulosa."""
    for tamanho in range(len(pedidos), -1, -1):
        for subconjunto in combinations(pedidos, tamanho):
            if all(not a.sobrepoe(b) for a, b in combinations(subconjunto, 2)):
                return tamanho


class TestSelecionar(unittest.TestCase):
    def test_vazio(self):
        self.assertEqual(selecionar([]), [])

    def test_um_pedido_preserva_turma_e_vagas(self):
        pedido = Aula("Reserva", 2, 480, 600, 80)
        self.assertEqual(selecionar([pedido]), [pedido])
        self.assertIs(selecionar([pedido])[0], pedido)

    def test_intervalos_encostados_sao_aceitos(self):
        pedidos = [Aula("A", 2, 480, 600), Aula("B", 2, 600, 720)]
        self.assertEqual(selecionar(pedidos), pedidos)

    def test_escolhe_menor_fim_e_nao_menor_inicio(self):
        longa = Aula("Longa", 2, 0, 100)
        a = Aula("A", 2, 1, 2)
        b = Aula("B", 2, 2, 3)
        self.assertEqual(selecionar([longa, b, a]), [a, b])

    def test_escolhe_menor_fim_e_nao_menor_duracao(self):
        a = Aula("A", 2, 0, 4)
        curta = Aula("Curta", 2, 3, 5)
        b = Aula("B", 2, 4, 8)
        self.assertEqual(selecionar([curta, a, b]), [a, b])

    def test_todos_sobrepostos_aceita_apenas_um(self):
        pedidos = [Aula(str(i), 2, i, 100 - i) for i in range(10)]
        self.assertEqual(selecionar(pedidos), [pedidos[-1]])

    def test_empates_de_fim_preservam_ordem_original(self):
        a = Aula("A", 2, 5, 10)
        b = Aula("B", 2, 0, 10)
        c = Aula("C", 2, 10, 20)
        self.assertEqual(selecionar([a, b, c]), [a, c])

    def test_pedidos_identicos_nao_sao_aceitos_duas_vezes(self):
        pedido = Aula("A", 2, 480, 600)
        self.assertEqual(selecionar([pedido, pedido]), [pedido])

    def test_nao_altera_entrada_e_ordena_resultado(self):
        pedidos = [Aula("B", 7, 10, 20), Aula("A", 7, 0, 10)]
        original = pedidos[:]
        self.assertEqual(selecionar(pedidos), [pedidos[1], pedidos[0]])
        self.assertEqual(pedidos, original)

    def test_rejeita_pedidos_de_dias_diferentes(self):
        with self.assertRaisesRegex(ValueError, "mesmo dia"):
            selecionar([Aula("A", 2, 480, 600), Aula("B", 3, 480, 600)])

    def test_vagas_nao_pesam_na_selecao(self):
        longa = Aula("Longa", 2, 0, 30, 1000)
        a = Aula("A", 2, 0, 10, 1)
        b = Aula("B", 2, 10, 20, 1)
        c = Aula("C", 2, 20, 30, 1)
        self.assertEqual(selecionar([longa, a, b, c]), [a, b, c])

    def test_confere_com_forca_bruta_em_instancias_aleatorias(self):
        rng = random.Random(44)
        for instancia in range(200):
            dia = rng.randint(2, 7)
            pedidos = []
            for i in range(rng.randint(0, 12)):
                inicio = rng.randrange(0, 40)
                pedidos.append(Aula(str(i), dia, inicio, inicio + rng.randint(1, 20)))
            rng.shuffle(pedidos)
            with self.subTest(instancia=instancia):
                escolhidos = selecionar(pedidos)
                self.assertEqual(len(escolhidos), maximo_por_forca_bruta(pedidos))
                self.assertTrue(all(any(pedido is original for original in pedidos)
                                    for pedido in escolhidos))
                self.assertTrue(all(not a.sobrepoe(b) for a, b in combinations(escolhidos, 2)))


if __name__ == "__main__":
    unittest.main()
