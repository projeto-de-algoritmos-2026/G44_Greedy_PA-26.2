import unittest

from src.horarios import INTERVALOS, ORDEM, aulas_da_turma


def hm(minutos):
    return f"{minutos // 60:02d}:{minutos % 60:02d}"


class TestTabela(unittest.TestCase):
    def test_tem_todos_os_horarios(self):
        self.assertEqual(len(ORDEM), 5 + 6 + 4)

    def test_horarios_nao_se_sobrepoem_e_estao_em_ordem(self):
        for a, b in zip(ORDEM, ORDEM[1:]):
            with self.subTest(a=a, b=b):
                self.assertLessEqual(INTERVALOS[a][1], INTERVALOS[b][0])

    def test_n1_termina_quando_n2_comeca(self):
        self.assertEqual(INTERVALOS[("N", 1)][1], INTERVALOS[("N", 2)][0])


class TestAulasDaTurma(unittest.TestCase):
    def test_exemplo_do_design_unb(self):
        # 6M1234: sexta-feira das 8h às 11h50
        [aula] = aulas_da_turma("X", "6M1234")
        self.assertEqual((aula.dia, hm(aula.inicio), hm(aula.fim)), (6, "08:00", "11:50"))

    def test_exemplo_do_portal_sig(self):
        # 246M34: segunda, quarta e sexta, das 10h às 11h50
        aulas = aulas_da_turma("X", "246M34")
        self.assertEqual([a.dia for a in aulas], [2, 4, 6])
        for a in aulas:
            self.assertEqual((hm(a.inicio), hm(a.fim)), ("10:00", "11:50"))

    def test_horarios_nao_consecutivos_viram_duas_aulas(self):
        aulas = aulas_da_turma("X", "2M13")
        self.assertEqual([(hm(a.inicio), hm(a.fim)) for a in aulas],
                         [("08:00", "08:55"), ("10:00", "10:55")])

    def test_atravessa_turno_vira_uma_aula(self):
        [aula] = aulas_da_turma("X", "3M5T1")
        self.assertEqual((hm(aula.inicio), hm(aula.fim)), ("12:00", "13:50"))

    def test_t6_e_n1_sao_consecutivos(self):
        [aula] = aulas_da_turma("X", "4T6N1")
        self.assertEqual((hm(aula.inicio), hm(aula.fim)), ("18:00", "19:50"))

    def test_preserva_turma_e_vagas(self):
        [aula] = aulas_da_turma("CIC0004-A", "2M12", vagas=60)
        self.assertEqual((aula.turma, aula.vagas), ("CIC0004-A", 60))


if __name__ == "__main__":
    unittest.main()
