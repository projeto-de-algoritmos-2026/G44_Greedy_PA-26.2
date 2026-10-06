import io
import tempfile
import unittest
from contextlib import redirect_stderr
from pathlib import Path

from src.dados import carregar_aulas
from src.modelo import Aula


RAIZ = Path(__file__).resolve().parents[1]
EXEMPLO = Path(__file__).with_name("turmas_exemplo.csv")
DADOS_REAIS = RAIZ / "data" / "raw" / "turmas_gama_2026_2.csv"


class TestCarregarAulas(unittest.TestCase):
    def carregar_texto(self, texto, encoding="utf-8"):
        with tempfile.TemporaryDirectory() as diretorio:
            caminho = Path(diretorio) / "turmas.csv"
            caminho.write_text(texto, encoding=encoding)
            relatorio = io.StringIO()
            with redirect_stderr(relatorio):
                aulas = carregar_aulas(caminho)
            return aulas, relatorio.getvalue()

    def test_exemplo_converte_e_preserva_ordem_turma_e_vagas(self):
        relatorio = io.StringIO()
        with redirect_stderr(relatorio):
            aulas = carregar_aulas(EXEMPLO)
        self.assertEqual(aulas, [
            Aula("A-01", 3, 840, 950, 40),
            Aula("A-01", 5, 840, 950, 40),
            Aula("B-02", 2, 480, 590, 30),
            Aula("B-02", 4, 480, 590, 30),
            Aula("B-02", 6, 895, 1015, 30),
            Aula("C-01", 3, 720, 830, 12),
        ])
        texto = relatorio.getvalue()
        for trecho in ("Turmas lidas: 8", "válidas: 3", "sem horário: 2",
                       "horários inválidos: 3", "linhas inválidas: 0", "aulas geradas: 6"):
            self.assertIn(trecho, texto)
        for turma in ("SEM-01", "SEM-02", "INV-01", "INV-02", "INV-03"):
            self.assertIn(f"turma {turma}:", texto)

    def test_codigo_parcialmente_valido_nao_deixa_aulas_parciais(self):
        aulas, relatorio = self.carregar_texto(
            "turma,disciplina,horario,vagas\n"
            "INV,Inválida,2M12 9T1,20\n"
            "OK,Válida,2M12,30\n"
        )
        self.assertEqual(aulas, [Aula("OK", 2, 480, 590, 30)])
        self.assertIn("horários inválidos: 1", relatorio)

    def test_aceita_bom_colunas_reordenadas_e_espacos(self):
        aulas, _ = self.carregar_texto(
            'vagas,horario,disciplina,turma\n0, 7M1 ,"Introdução, teoria", 01 \n',
            encoding="utf-8-sig",
        )
        self.assertEqual(aulas, [Aula("01", 7, 480, 535, 0)])

    def test_cabecalho_sem_registros(self):
        aulas, relatorio = self.carregar_texto("turma,disciplina,horario,vagas\n")
        self.assertEqual(aulas, [])
        self.assertIn("Turmas lidas: 0", relatorio)

    def test_todas_as_turmas_descartadas(self):
        aulas, relatorio = self.carregar_texto(
            "turma,disciplina,horario,vagas\nSEM,Sem horário,,20\nINV,Inválida,8M12,30\n"
        )
        self.assertEqual(aulas, [])
        self.assertIn("sem horário: 1", relatorio)
        self.assertIn("horários inválidos: 1", relatorio)

    def test_cabecalho_invalido(self):
        for texto in ("", "turma,horario,vagas\n", "turma,disciplina,horario,vagas,vagas\n"):
            with self.subTest(texto=texto), self.assertRaisesRegex(ValueError, "cabeçalho"):
                self.carregar_texto(texto)

    def test_vagas_invalidas_nao_interrompem_leitura_nem_viram_zero(self):
        aulas, relatorio = self.carregar_texto(
            "turma,disciplina,horario,vagas\n"
            "A,Disciplina,2M12,-1\nB,Disciplina,2M12,abc\n"
            "C,Disciplina,2M12,\nOK,Disciplina,2M12,40\n"
        )
        self.assertEqual(aulas, [Aula("OK", 2, 480, 590, 40)])
        self.assertIn("linhas inválidas: 3", relatorio)

    def test_registros_incompletos_ou_com_campos_excedentes(self):
        aulas, relatorio = self.carregar_texto(
            "turma,disciplina,horario,vagas\n"
            "A,Disciplina,2M12\nB,Disciplina,2M12,30,extra\n"
            ",Disciplina,2M12,30\nC,,2M12,30\nOK,Disciplina,2M12,40\n"
        )
        self.assertEqual(aulas, [Aula("OK", 2, 480, 590, 40)])
        self.assertIn("linhas inválidas: 4", relatorio)

    def test_arquivo_inexistente(self):
        with tempfile.TemporaryDirectory() as diretorio:
            with self.assertRaises(FileNotFoundError):
                carregar_aulas(Path(diretorio) / "inexistente.csv")


@unittest.skipUnless(DADOS_REAIS.is_file(), "coleta real ausente em data/raw/")
class TestDadosReais(unittest.TestCase):
    def test_coleta_gama_2026_2_confere_com_numeros_documentados(self):
        relatorio = io.StringIO()
        with redirect_stderr(relatorio):
            aulas = carregar_aulas(DADOS_REAIS)
        self.assertEqual(len(aulas), 430)
        vagas_por_turma = {aula.turma: aula.vagas for aula in aulas}
        self.assertEqual(len(vagas_por_turma), 229)
        self.assertEqual(sum(vagas_por_turma.values()), 11836)
        self.assertEqual(vagas_por_turma["FGA0244-01"], 80)
        self.assertIn("sem horário: 0", relatorio.getvalue())
        self.assertIn("horários inválidos: 0", relatorio.getvalue())
        self.assertIn("linhas inválidas: 0", relatorio.getvalue())


if __name__ == "__main__":
    unittest.main()
