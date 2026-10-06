# Figuras da coleta Gama 2026.2

Geradas a partir de `data/raw/turmas_gama_2026_2.csv`, com 229 turmas e
430 encontros semanais, em 05/10/2026. Validação com 10 subamostras,
tamanho 12 e semente 44, sem inventário de capacidades informado.

Para reproduzir, na raiz do projeto:

```bash
python -m pip install -r requirements.txt
python validacao.py
python graficos.py --saida docs/graficos
```

Os quatro algoritmos usam 28 salas sem conflitos. A profundidade é 28.
O dimensionamento do guloso soma 2.947 lugares, com capacidades de 10 a
131 vagas. Isso descreve essa alocação, não um inventário real nem uma
soma de capacidades comprovadamente mínima.

Cada figura está disponível em PNG e SVG. Os tempos são os de uma única
execução e variam por máquina e execução; não constituem um benchmark.
