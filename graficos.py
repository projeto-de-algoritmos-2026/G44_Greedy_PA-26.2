"""Gera PNGs e SVGs dos CSVs de validação: python graficos.py --help."""

import argparse
import csv
from collections import Counter, defaultdict
from pathlib import Path

from src.modelo import DIAS


def ler_csv(caminho, campos):
    with caminho.open(encoding="utf-8-sig", newline="") as arquivo:
        leitor = csv.DictReader(arquivo)
        if not set(campos).issubset(leitor.fieldnames or []):
            raise ValueError(f"campos obrigatórios ausentes em {caminho.name}")
        return list(leitor)


def ocupacao_por_dia(alocacoes):
    """Agrupa eventos no mesmo instante: fim e início encostados não se somam."""
    eventos = defaultdict(Counter)
    for aula in alocacoes:
        dia = int(aula["dia"])
        eventos[dia][int(aula["inicio"])] += 1
        eventos[dia][int(aula["fim"])] -= 1
    series = {}
    for dia in DIAS:
        tempos, ativos, atual = [0], [0], 0
        for instante, delta in sorted(eventos[dia].items()):
            atual += delta
            tempos.append(instante)
            ativos.append(atual)
        tempos.append(1440)
        ativos.append(0)
        series[dia] = (tempos, ativos)
    return series


def gerar_graficos(resultados: Path, saida: Path) -> list[Path]:
    """Lê os CSVs existentes e exporta quatro figuras em PNG e SVG."""
    resumo = ler_csv(resultados / "resumo.csv", ["estrategia", "salas", "limite", "tempo_ms"])
    alocacoes = ler_csv(resultados / "alocacoes.csv", ["estrategia", "dia", "inicio", "fim"])
    capacidades = ler_csv(resultados / "capacidades.csv", ["estrategia", "sala", "capacidade_minima"])
    algoritmos = [r for r in resumo if r["estrategia"] != "limite"]
    if not algoritmos:
        raise ValueError("resumo.csv não contém estratégias para comparar")
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    saida.mkdir(parents=True, exist_ok=True)
    arquivos = []

    def salvar(figura, nome):
        figura.tight_layout()
        for extensao in ("png", "svg"):
            caminho = saida / f"{nome}.{extensao}"
            figura.savefig(caminho, dpi=160, facecolor="white")
            arquivos.append(caminho)
        plt.close(figura)

    nomes = [r["estrategia"] for r in algoritmos]
    fig, ax = plt.subplots(figsize=(9, 4))
    valores = [int(r["salas"]) for r in algoritmos]
    barras = ax.bar(nomes, valores, color="#2563eb")
    ax.bar_label(barras, padding=3)
    ax.axhline(int(algoritmos[0]["limite"]), color="#dc2626", linestyle="--", label="Profundidade")
    ax.set(ylabel="Número de salas", title="Salas por estratégia")
    ax.set_ylim(0, max([1] + valores) * 1.2)
    if "capacidade_best_fit" in nomes:
        ax.set_title("Salas por estratégia (best fit usa inventário com capacidades)")
    ax.legend()
    salvar(fig, "comparacao_salas")

    fig, ax = plt.subplots(figsize=(9, 4))
    tempos = [float(r["tempo_ms"]) for r in algoritmos]
    barras = ax.bar(nomes, tempos, color="#0d9488")
    ax.bar_label(barras, fmt="%.3f", padding=3)
    ax.set(ylabel="Tempo (ms)", title="Tempo de uma execução — sem conferência e gravação")
    ax.set_ylim(0, max([0.001] + tempos) * 1.25)
    salvar(fig, "tempos")

    guloso = [r for r in alocacoes if r["estrategia"] == "guloso"]
    fig, ax = plt.subplots(figsize=(10, 5))
    for dia, (minutos, ativas) in ocupacao_por_dia(guloso).items():
        ax.step([t / 60 for t in minutos], ativas, where="post", label=DIAS[dia])
    ax.set(xlabel="Hora do dia", ylabel="Aulas simultâneas", title="Ocupação semanal por dia", xlim=(0, 24))
    ax.set_xticks(range(0, 25, 2))
    ax.grid(axis="y", alpha=0.25)
    ax.legend(ncol=3)
    salvar(fig, "ocupacao_por_dia")

    salas = sorted((r for r in capacidades if r["estrategia"] == "guloso"), key=lambda r: int(r["sala"]))
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.bar([r["sala"] for r in salas], [int(r["capacidade_minima"]) for r in salas], color="#7c3aed")
    ax.set(xlabel="Identificador da sala", ylabel="Vagas mínimas",
           title="Capacidade necessária por sala na alocação gulosa — não é inventário físico")
    salvar(fig, "capacidades_guloso")
    return arquivos


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    raiz = Path(__file__).resolve().parent
    parser.add_argument("resultados", nargs="?", type=Path, default=raiz / "resultados")
    parser.add_argument("--saida", type=Path)
    args = parser.parse_args(argv)
    try:
        arquivos = gerar_graficos(args.resultados, args.saida or args.resultados / "graficos")
    except (OSError, ValueError, ImportError) as erro:
        parser.exit(1, f"Erro: {erro}. Execute a validação e instale requirements.txt.\n")
    print(f"{len(arquivos)} arquivos de gráficos salvos em {arquivos[0].parent.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
