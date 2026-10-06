import unittest

from src.capacidade import alocar_com_capacidade, capacidades_minimas, excessos_de_capacidade
from src.modelo import Aula
from validacao import contar_conflitos


class TestCapacidade(unittest.TestCase):
    def test_dimensiona_mesma_sala_em_dias_diferentes(self):
        aulas = [Aula('A', 2, 0, 10, 30), Aula('B', 3, 0, 10, 80)]
        self.assertEqual(capacidades_minimas(aulas, [0, 0]), [80])
        self.assertEqual(capacidades_minimas(aulas, [0, 2]), [30, 0, 80])
        self.assertEqual(excessos_de_capacidade(aulas, [0, 0], [40]), [1])

    def test_aloca_sem_conflitos_e_respeita_capacidade(self):
        aulas = [Aula('Pequena', 2, 0, 10, 20), Aula('Grande', 2, 0, 20, 50),
                 Aula('Seguinte', 2, 10, 30, 30), Aula('Outro dia', 3, 0, 10, 50)]
        salas = alocar_com_capacidade(aulas, [60, 30])
        self.assertEqual(salas, [1, 0, 1, 0])
        self.assertEqual(contar_conflitos(aulas, salas), 0)
        self.assertEqual(excessos_de_capacidade(aulas, salas, [60, 30]), [])

    def test_entrada_vazia_e_sala_de_capacidade_zero(self):
        self.assertEqual(alocar_com_capacidade([], []), [])
        self.assertEqual(capacidades_minimas([], []), [])
        self.assertEqual(alocar_com_capacidade([Aula('A', 2, 0, 10)], [0]), [0])

    def test_rejeita_valores_invalidos(self):
        aulas = [Aula('A', 2, 0, 10, 30)]
        for salas in ([], [-1], [True], [1.0]):
            with self.subTest(salas=salas), self.assertRaises(ValueError):
                capacidades_minimas(aulas, salas)
        for capacidades in ([-1], [True], [1.5], []):
            with self.subTest(capacidades=capacidades), self.assertRaises(ValueError):
                alocar_com_capacidade(aulas, capacidades)
        with self.assertRaises(ValueError):
            excessos_de_capacidade(aulas, [1], [40])
        with self.assertRaises(ValueError):
            capacidades_minimas([Aula('A', 2, 0, 10, -1)], [0])

    def test_falha_da_heuristica_nao_prova_inviabilidade(self):
        aulas = [Aula('Curta', 2, 0, 10, 20), Aula('Longa', 2, 0, 100, 20),
                 Aula('Grande', 2, 10, 20, 50)]
        with self.assertRaisesRegex(ValueError, 'não prova inviabilidade'):
            alocar_com_capacidade(aulas, [30, 60])
        alternativa = [1, 0, 1]
        self.assertEqual(contar_conflitos(aulas, alternativa), 0)
        self.assertEqual(excessos_de_capacidade(aulas, alternativa, [30, 60]), [])
