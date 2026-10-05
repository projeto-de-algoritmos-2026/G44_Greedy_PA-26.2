import unittest

from src.modelo import Aula, ler_codigo


class TestAula(unittest.TestCase):
    def test_intervalo_semiaberto_nao_conflita_na_borda(self):
        a = Aula("A", 2, 480, 600)
        b = Aula("B", 2, 600, 700)
        self.assertFalse(a.sobrepoe(b))
        self.assertFalse(b.sobrepoe(a))

    def test_sobreposicao_parcial(self):
        a = Aula("A", 2, 480, 600)
        b = Aula("B", 2, 599, 700)
        self.assertTrue(a.sobrepoe(b))

    def test_dias_diferentes_nunca_conflitam(self):
        a = Aula("A", 2, 480, 600)
        b = Aula("B", 3, 480, 600)
        self.assertFalse(a.sobrepoe(b))

    def test_rejeita_dia_inexistente(self):
        with self.assertRaises(ValueError):
            Aula("A", 1, 480, 600)

    def test_rejeita_intervalo_vazio_ou_invertido(self):
        with self.assertRaises(ValueError):
            Aula("A", 2, 600, 600)
        with self.assertRaises(ValueError):
            Aula("A", 2, 700, 600)


class TestLerCodigo(unittest.TestCase):
    def test_codigo_simples(self):
        self.assertEqual(
            ler_codigo("35T23"),
            [(3, "T", 2), (3, "T", 3), (5, "T", 2), (5, "T", 3)],
        )

    def test_varios_blocos(self):
        self.assertEqual(
            ler_codigo("24M12 6T34"),
            [(2, "M", 1), (2, "M", 2), (4, "M", 1), (4, "M", 2), (6, "T", 3), (6, "T", 4)],
        )

    def test_bloco_que_atravessa_turnos(self):
        self.assertEqual(ler_codigo("3M5T1"), [(3, "M", 5), (3, "T", 1)])

    def test_exemplo_do_portal_sig(self):
        self.assertEqual(len(ler_codigo("246M34")), 6)

    def test_ordena_e_remove_repetidos(self):
        self.assertEqual(ler_codigo("2T1 2M1 2T1"), [(2, "M", 1), (2, "T", 1)])

    def test_rejeita_horario_que_nao_existe(self):
        with self.assertRaises(ValueError):
            ler_codigo("2M6")
        with self.assertRaises(ValueError):
            ler_codigo("2N5")

    def test_rejeita_lixo(self):
        for codigo in ["", "   ", "M12", "8M1", "2X1", "2M"]:
            with self.subTest(codigo=codigo), self.assertRaises(ValueError):
                ler_codigo(codigo)


if __name__ == "__main__":
    unittest.main()
