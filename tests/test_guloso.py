import random
import unittest
from itertools import combinations

from src.guloso import alocar
from src.limite import profundidade
from src.modelo import Aula


class TestAlocar(unittest.TestCase):
    def conferir_alocacao(self, aulas):
        original = aulas[:]
        salas = alocar(aulas)
        self.assertEqual(aulas, original)
        self.assertEqual(len(salas), len(aulas))
        self.assertTrue(all(type(sala) is int and sala >= 0 for sala in salas))
        usadas = set(salas)
        self.assertEqual(usadas, set(range(len(usadas))))
        self.assertEqual(len(usadas), profundidade(aulas))
        for i, j in combinations(range(len(aulas)), 2):
            if salas[i] == salas[j]:
                self.assertFalse(aulas[i].sobrepoe(aulas[j]),
                                 f"Conflito entre aulas {i} e {j} na sala {salas[i]}")
        return salas

    def test_vazio(self):
        self.assertEqual(self.conferir_alocacao([]), [])

    def test_uma_aula(self):
        self.assertEqual(self.conferir_alocacao([Aula("A", 2, 480, 600)]), [0])

    def test_encostadas_reutilizam_sala(self):
        aulas = [Aula("A", 2, 480, 600), Aula("B", 2, 600, 700), Aula("C", 2, 700, 800)]
        self.assertEqual(self.conferir_alocacao(aulas), [0, 0, 0])

    def test_preserva_ordem_original_com_entrada_desordenada(self):
        aulas = [Aula("Tardia", 2, 20, 30), Aula("Cedo", 2, 0, 10), Aula("Meio", 2, 5, 25)]
        self.assertEqual(self.conferir_alocacao(aulas), [0, 0, 1])

    def test_reutiliza_sala_que_libera_primeiro(self):
        aulas = [Aula("Longa", 2, 0, 100), Aula("Curta", 2, 10, 20), Aula("Nova", 2, 20, 30)]
        self.assertEqual(self.conferir_alocacao(aulas), [0, 1, 1])

    def test_mesma_sala_em_dias_diferentes(self):
        aulas = [Aula("A", dia, 480, 600) for dia in range(2, 8)]
        self.assertEqual(self.conferir_alocacao(aulas), [0] * 6)

    def test_total_e_maximo_diario_e_nao_soma_dos_dias(self):
        aulas = [Aula("A", 2, 0, 100), Aula("B", 3, 0, 100),
                 Aula("C", 2, 0, 100), Aula("D", 3, 0, 100),
                 Aula("E", 2, 0, 100), Aula("F", 7, 0, 100)]
        self.assertEqual(self.conferir_alocacao(aulas), [0, 0, 1, 1, 2, 0])

    def test_aulas_identicas_continuam_sendo_registros_distintos(self):
        aula = Aula("A", 2, 480, 600)
        self.assertEqual(self.conferir_alocacao([aula, aula, aula]), [0, 1, 2])

    def test_intervalos_aninhados(self):
        aulas = [Aula(str(i), 2, i, 100 - i) for i in range(10)]
        self.assertEqual(len(set(self.conferir_alocacao(aulas))), 10)

    def test_varias_salas_liberam_no_mesmo_instante(self):
        aulas = [Aula("A", 2, 0, 10), Aula("B", 2, 0, 10),
                 Aula("C", 2, 10, 20), Aula("D", 2, 10, 20)]
        self.assertEqual(self.conferir_alocacao(aulas), [0, 1, 0, 1])

    def test_vagas_nao_limitam_alocacao(self):
        aulas = [Aula("A", 2, 0, 10, 10), Aula("B", 2, 10, 20, 200)]
        self.assertEqual(self.conferir_alocacao(aulas), [0, 0])

    def test_instancias_aleatorias_sem_conflitos_e_otimas(self):
        rng = random.Random(44)
        for instancia in range(300):
            aulas = []
            for i in range(rng.randint(0, 60)):
                inicio = rng.randrange(0, 120)
                aulas.append(Aula(f"T{i}", rng.randint(2, 7), inicio,
                                  inicio + rng.randint(1, 60), rng.randint(0, 200)))
            rng.shuffle(aulas)
            with self.subTest(instancia=instancia):
                self.conferir_alocacao(aulas)


if __name__ == "__main__":
    unittest.main()
