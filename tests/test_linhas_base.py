import random
import unittest
from itertools import combinations

from src.guloso import alocar
from src.limite import profundidade
from src.linhas_base import ESTRATEGIAS, ordem_entrada
from src.modelo import Aula


class TestLinhasBase(unittest.TestCase):
    def conferir(self, aulas):
        original = aulas[:]
        for nome, estrategia in ESTRATEGIAS.items():
            with self.subTest(estrategia=nome):
                salas = estrategia(aulas)
                self.assertEqual(aulas, original)
                self.assertIsInstance(salas, list)
                self.assertEqual(len(salas), len(aulas))
                self.assertTrue(all(type(sala) is int and sala >= 0 for sala in salas))
                self.assertEqual(set(salas), set(range(len(set(salas)))))
                self.assertGreaterEqual(len(set(salas)), profundidade(aulas))
                for i, j in combinations(range(len(aulas)), 2):
                    if salas[i] == salas[j]:
                        self.assertFalse(aulas[i].sobrepoe(aulas[j]))

    def test_vazio(self):
        for estrategia in ESTRATEGIAS.values():
            self.assertEqual(estrategia([]), [])

    def test_encostadas_e_dias_diferentes_reutilizam_sala(self):
        aulas = [Aula("A", 2, 0, 10), Aula("B", 2, 10, 20), Aula("C", 3, 0, 20)]
        for estrategia in ESTRATEGIAS.values():
            self.assertEqual(estrategia(aulas), [0, 0, 0])

    def test_preserva_ordem_original_ao_processar_por_fim_ou_duracao(self):
        aulas = [Aula("Tardia", 2, 20, 30), Aula("Longa", 2, 0, 25), Aula("Cedo", 2, 0, 10)]
        self.conferir(aulas)

    def test_registros_identicos_precisam_de_salas_distintas(self):
        aula = Aula("A", 2, 0, 20)
        for estrategia in ESTRATEGIAS.values():
            self.assertEqual(estrategia([aula, aula, aula]), [0, 1, 2])

    def test_ordem_entrada_pode_usar_mais_salas_que_guloso(self):
        aulas = [Aula("A", 2, 0, 2), Aula("D", 2, 4, 6),
                 Aula("B", 2, 1, 4), Aula("C", 2, 3, 5)]
        self.assertEqual(len(set(ordem_entrada(aulas))), 3)
        self.assertEqual(len(set(alocar(aulas))), 2)
        self.conferir(aulas)

    def test_instancias_aleatorias_sem_conflitos(self):
        rng = random.Random(44)
        for instancia in range(100):
            aulas = []
            for i in range(rng.randint(0, 40)):
                inicio = rng.randrange(0, 100)
                aulas.append(Aula(str(i), rng.randint(2, 7), inicio, inicio + rng.randint(1, 50)))
            rng.shuffle(aulas)
            with self.subTest(instancia=instancia):
                self.conferir(aulas)


if __name__ == "__main__":
    unittest.main()
