import csv
import io
import tempfile
import types
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

import validacao
from src.modelo import Aula
from src.linhas_base import ESTRATEGIAS


class TestValidacao(unittest.TestCase):
    def setUp(self):
        self.aulas = [Aula("A", 2, 0, 20, 30), Aula("B", 2, 10, 30, 40),
                      Aula("C", 3, 0, 20, 50)]

    def test_compara_baseline_e_preserva_indices(self):
        resumo, alocacoes = validacao.comparar(self.aulas, {"uma_por_aula": lambda aulas: list(range(len(aulas)))})
        por_nome = {r["estrategia"]: r for r in resumo}
        self.assertEqual(por_nome["guloso"]["salas"], 2)
        self.assertEqual(por_nome["uma_por_aula"]["salas"], 3)
        self.assertEqual(por_nome["uma_por_aula"]["excesso"], 1)
        self.assertEqual(por_nome["uma_por_aula"]["conflitos"], 0)
        self.assertEqual([r["indice_aula"] for r in alocacoes], [0, 1, 2, 0, 1, 2])
        self.assertEqual([r["turma"] for r in alocacoes[:3]], ["A", "B", "C"])

    def test_conta_conflitos_sem_confundir_dias(self):
        self.assertEqual(validacao.contar_conflitos(self.aulas, [0, 0, 0]), 1)
        resumo, _ = validacao.comparar(self.aulas, {"invalida": lambda aulas: [0] * len(aulas)})
        self.assertEqual(resumo[-1]["conflitos"], 1)

    def test_rejeita_alocacoes_fora_do_contrato(self):
        for salas in ([0], [0, -1, 0], [0, True, 1], [0, 1.0, 1], (0, 1, 0)):
            with self.subTest(salas=salas), self.assertRaises(ValueError):
                validacao.contar_conflitos(self.aulas, salas)

    def test_subamostras_reproduziveis_e_limitadas_a_doze(self):
        aulas = [Aula(str(i), 2, i, i + 20) for i in range(30)]
        primeira = validacao.validar_subamostras(aulas, quantidade=5, semente=44)
        segunda = validacao.validar_subamostras(aulas, quantidade=5, semente=44)
        self.assertEqual([r["indices_aulas"] for r in primeira], [r["indices_aulas"] for r in segunda])
        self.assertTrue(all(r["aulas"] == 12 and r["confere"] for r in primeira))
        self.assertTrue(all(r["salas_exato"] == r["salas_guloso"] == r["limite"] for r in primeira))

    def test_entrada_vazia_e_amostras_desativadas(self):
        resumo, alocacoes = validacao.comparar([], {})
        self.assertEqual([r["salas"] for r in resumo], [0, 0])
        self.assertEqual(alocacoes, [])
        self.assertTrue(validacao.validar_subamostras([], quantidade=1)[0]["confere"])
        self.assertEqual(validacao.validar_subamostras(self.aulas, quantidade=0), [])

    def test_rejeita_parametros_de_amostragem_invalidos(self):
        for quantidade, tamanho in ((-1, 12), (1, 0), (1, 13)):
            with self.subTest(quantidade=quantidade, tamanho=tamanho), self.assertRaises(ValueError):
                validacao.validar_subamostras(self.aulas, quantidade, tamanho)

    def test_carrega_registro_de_estrategias(self):
        funcao = lambda aulas: list(range(len(aulas)))
        for registro in ({"base": funcao}, [("base", funcao)]):
            with self.subTest(registro=registro):
                modulo = types.SimpleNamespace(ESTRATEGIAS=registro)
                with patch.object(validacao.importlib, "import_module", return_value=modulo):
                    self.assertEqual(validacao.carregar_estrategias(), {"base": funcao})

    def test_modulo_ausente_e_dependencia_interna_ausente(self):
        ausente = ModuleNotFoundError(name="src.linhas_base")
        with patch.object(validacao.importlib, "import_module", side_effect=ausente):
            with self.assertRaisesRegex(ValueError, "comparação completa"):
                validacao.carregar_estrategias()
        erro_interno = ModuleNotFoundError(name="dependencia_interna")
        with patch.object(validacao.importlib, "import_module", side_effect=erro_interno):
            with self.assertRaises(ModuleNotFoundError):
                validacao.carregar_estrategias()

    def test_comando_salva_csvs_e_tabelas(self):
        exemplo = Path(__file__).with_name("turmas_exemplo.csv")
        with tempfile.TemporaryDirectory() as diretorio:
            saida = Path(diretorio) / "resultados"
            terminal = io.StringIO()
            with redirect_stdout(terminal), redirect_stderr(io.StringIO()):
                codigo = validacao.main([str(exemplo), "--saida", str(saida), "--amostras", "2"])
            self.assertEqual(codigo, 0)
            for nome in ESTRATEGIAS:
                self.assertIn(nome, terminal.getvalue())
            with (saida / "resumo.csv").open(encoding="utf-8", newline="") as arquivo:
                resumo = list(csv.DictReader(arquivo))
            self.assertEqual(resumo[1]["estrategia"], "guloso")
            self.assertEqual(resumo[1]["aulas"], "6")
            self.assertEqual({r["estrategia"] for r in resumo}, {"limite", "guloso", *ESTRATEGIAS})
            self.assertTrue(all(r["conflitos"] == "0" for r in resumo[1:]))
            with (saida / "alocacoes.csv").open(encoding="utf-8", newline="") as arquivo:
                self.assertEqual(len(list(csv.DictReader(arquivo))), 6 * (1 + len(ESTRATEGIAS)))
            with (saida / "subamostras.csv").open(encoding="utf-8", newline="") as arquivo:
                amostras = list(csv.DictReader(arquivo))
            self.assertEqual(len(amostras), 2)
            self.assertTrue(all(r["confere"] == "True" for r in amostras))
            with (saida / "capacidades.csv").open(encoding="utf-8", newline="") as arquivo:
                capacidades = list(csv.DictReader(arquivo))
            self.assertEqual(len(capacidades), 1 + len(ESTRATEGIAS))
            self.assertTrue(all(r["capacidade_minima"] == "40" for r in capacidades))

    def test_dimensiona_e_verifica_inventario(self):
        estrategias = {"capacidade_best_fit": lambda aulas: [0, 1, 1]}
        _, alocacoes = validacao.comparar(self.aulas, estrategias)
        linhas = validacao.dimensionar_capacidades(self.aulas, alocacoes, [30, 50])
        inventario = [r for r in linhas if r["estrategia"] == "capacidade_best_fit"]
        self.assertEqual([r["capacidade_minima"] for r in inventario], [30, 50])
        self.assertTrue(all(r["adequada"] for r in inventario))
        with self.assertRaises(ValueError):
            validacao.dimensionar_capacidades(self.aulas, alocacoes, [30, 40])

    def test_comando_retorna_falha_se_baseline_tem_conflitos(self):
        with tempfile.TemporaryDirectory() as diretorio:
            exemplo = Path(diretorio) / "turmas.csv"
            exemplo.write_text("turma,disciplina,horario,vagas\n"
                               "A,Disciplina,2M12,20\nB,Disciplina,2M12,30\n",
                               encoding="utf-8")
            with patch.object(validacao, "carregar_estrategias", return_value={"invalida": lambda aulas: [0] * len(aulas)}), \
                    redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                codigo = validacao.main([str(exemplo), "--saida", diretorio, "--amostras", "0"])
            self.assertEqual(codigo, 1)

    def test_rejeita_registro_vazio_duplicado_ou_invalido(self):
        funcao = lambda aulas: []
        for registro in ({}, {"base": None}, {"guloso": funcao},
                         [("base", funcao), ("base", funcao)]):
            with self.subTest(registro=registro):
                modulo = types.SimpleNamespace(ESTRATEGIAS=registro)
                with patch.object(validacao.importlib, "import_module", return_value=modulo):
                    with self.assertRaises(ValueError):
                        validacao.carregar_estrategias()


if __name__ == "__main__":
    unittest.main()
