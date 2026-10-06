import random
import unittest

from src.exato import minimo_de_salas
from src.guloso import alocar
from src.modelo import Aula


class TestMinimoDeSalas(unittest.TestCase):
    def test_vazio(self):
        self.assertEqual(minimo_de_salas([]), 0)

    def test_uma_aula(self):
        self.assertEqual(minimo_de_salas([Aula("A", 2, 480, 600)]), 1)

    def test_intervalos_encostados(self):
        aulas = [Aula("A", 2, 480, 600), Aula("B", 2, 600, 720)]
        self.assertEqual(minimo_de_salas(aulas), 1)

    def test_mesma_sala_em_dias_diferentes(self):
        aulas = [Aula("A", dia, 480, 600) for dia in range(2, 8)]
        self.assertEqual(minimo_de_salas(aulas), 1)

    def test_total_e_maximo_diario_e_nao_soma(self):
        aulas = [Aula("A", 2, 0, 100), Aula("B", 3, 0, 100),
                 Aula("C", 2, 0, 100), Aula("D", 3, 0, 100), Aula("E", 2, 0, 100)]
        self.assertEqual(minimo_de_salas(aulas), 3)

    def test_precisa_desfazer_atribuicoes_para_caber_em_duas_salas(self):
        # Na ordem A, D, B, C, colocar A e D na mesma sala bloqueia C.
        # A solução de duas salas exige revisitar a atribuição de D.
        aulas = [Aula("A", 2, 0, 2), Aula("D", 2, 4, 6),
                 Aula("B", 2, 1, 4), Aula("C", 2, 3, 5)]
        self.assertEqual(minimo_de_salas(aulas), 2)

    def test_aulas_identicas_sao_registros_distintos(self):
        aula = Aula("A", 2, 480, 600)
        self.assertEqual(minimo_de_salas([aula, aula, aula]), 3)

    def test_doze_aulas_sobrepostas(self):
        aulas = [Aula(str(i), 2, i, 100 - i) for i in range(12)]
        self.assertEqual(minimo_de_salas(aulas), 12)

    def test_doze_aulas_sem_conflitos(self):
        aulas = [Aula(str(i), 2, i * 10, (i + 1) * 10) for i in range(12)]
        self.assertEqual(minimo_de_salas(aulas), 1)

    def test_rejeita_instancia_maior_que_limite(self):
        aulas = [Aula(str(i), 2, i * 10, (i + 1) * 10) for i in range(13)]
        with self.assertRaisesRegex(ValueError, "no máximo 12 aulas"):
            minimo_de_salas(aulas)

    def test_nao_altera_entrada(self):
        aulas = [Aula("B", 2, 10, 30, 200), Aula("A", 2, 0, 20, 10)]
        original = aulas[:]
        self.assertEqual(minimo_de_salas(aulas), 2)
        self.assertEqual(aulas, original)

    def test_confere_com_guloso_em_instancias_aleatorias(self):
        rng = random.Random(44)
        for instancia in range(200):
            aulas = []
            # Inclui dias variados e casos concentrados em um único dia.
            dias = [2] if instancia % 2 == 0 else list(range(2, 8))
            for i in range(rng.randint(0, 12)):
                inicio = rng.randrange(0, 60)
                aulas.append(Aula(f"T{i}", rng.choice(dias), inicio,
                                  inicio + rng.randint(1, 40)))
            rng.shuffle(aulas)
            with self.subTest(instancia=instancia):
                self.assertEqual(minimo_de_salas(aulas), len(set(alocar(aulas))))


if __name__ == "__main__":
    unittest.main()
