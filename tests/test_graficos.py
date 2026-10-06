import importlib.util
import io
import tempfile
import unittest
import xml.etree.ElementTree as ET
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

import graficos
import validacao


class TestGraficos(unittest.TestCase):
    def test_eventos_encostados_e_dias_independentes(self):
        registros = [{'dia': 2, 'inicio': 480, 'fim': 600},
                     {'dia': 2, 'inicio': 600, 'fim': 720},
                     {'dia': 3, 'inicio': 480, 'fim': 720}]
        series = graficos.ocupacao_por_dia(registros)
        self.assertEqual(series[2], ([0, 480, 600, 720, 1440], [0, 1, 1, 0, 0]))
        self.assertEqual(max(series[3][1]), 1)
        self.assertEqual(series[7], ([0, 1440], [0, 0]))

    @unittest.skipUnless(importlib.util.find_spec('matplotlib'), 'matplotlib não instalado')
    def test_pipeline_exporta_pngs_e_svgs_validos(self):
        exemplo = Path(__file__).with_name('turmas_exemplo.csv')
        with tempfile.TemporaryDirectory() as diretorio:
            resultados = Path(diretorio)
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                self.assertEqual(validacao.main([str(exemplo), '--saida', diretorio,
                                                '--amostras', '0', '--capacidades', '40', '80']), 0)
            arquivos = graficos.gerar_graficos(resultados, resultados / 'graficos')
            self.assertEqual(len(arquivos), 8)
            for arquivo in arquivos:
                if arquivo.suffix == '.png':
                    self.assertTrue(arquivo.read_bytes().startswith(b'\x89PNG\r\n\x1a\n'))
                else:
                    self.assertEqual(ET.parse(arquivo).getroot().tag, '{http://www.w3.org/2000/svg}svg')

    def test_rejeita_csv_sem_campos_obrigatorios(self):
        with tempfile.TemporaryDirectory() as diretorio:
            arquivo = Path(diretorio) / 'resumo.csv'
            arquivo.write_text('estrategia\nguloso\n', encoding='utf-8')
            with self.assertRaises(ValueError):
                graficos.ler_csv(arquivo, ['estrategia', 'salas'])
