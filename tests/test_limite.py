import random
import unittest

from src.limite import pico, profundidade
from src.modelo import Aula


def profundidade_por_forca_bruta(aulas):
    """Conta, em cada minuto de cada dia, quantas aulas estão acontecendo."""
    melhor = 0
    for a in aulas:
        for t in range(a.inicio, a.fim):
            ativas = sum(1 for b in aulas if b.dia == a.dia and b.inicio <= t < b.fim)
            melhor = max(melhor, ativas)
    return melhor


class TestProfundidade(unittest.TestCase):
    def test_vazio(self):
        self.assertEqual(pico([]), (0, None, None))

    def test_uma_aula(self):
        self.assertEqual(profundidade([Aula("A", 2, 480, 600)]), 1)

    def test_encostadas_nao_somam(self):
        aulas = [Aula("A", 2, 480, 600), Aula("B", 2, 600, 700)]
        self.assertEqual(profundidade(aulas), 1)

    def test_mesmo_horario_em_dias_diferentes_nao_soma(self):
        aulas = [Aula("A", d, 480, 600) for d in range(2, 8)]
        self.assertEqual(profundidade(aulas), 1)

    def test_tres_sobrepostas_em_escada(self):
        aulas = [Aula("A", 3, 0, 100), Aula("B", 3, 50, 150), Aula("C", 3, 90, 200)]
        self.assertEqual(pico(aulas), (3, 3, 90))

    def test_profundidade_pode_ser_menor_que_o_grafo_sugere(self):
        # A conflita com B e com C, mas B e C não se cruzam: bastam 2 salas.
        aulas = [Aula("A", 2, 0, 100), Aula("B", 2, 0, 50), Aula("C", 2, 50, 100)]
        self.assertEqual(profundidade(aulas), 2)

    def test_confere_com_forca_bruta_em_instancias_aleatorias(self):
        rng = random.Random(44)
        for _ in range(200):
            aulas = []
            for i in range(rng.randint(0, 12)):
                inicio = rng.randrange(0, 100)
                aulas.append(Aula(f"T{i}", rng.choice([2, 3]), inicio, inicio + rng.randint(1, 40)))
            with self.subTest(aulas=aulas):
                self.assertEqual(profundidade(aulas), profundidade_por_forca_bruta(aulas))


if __name__ == "__main__":
    unittest.main()
