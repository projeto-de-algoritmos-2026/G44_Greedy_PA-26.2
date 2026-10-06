"""Compara alocações e salva resultados: python validacao.py --help."""

import argparse
import csv
import importlib
import random
from collections.abc import Mapping
from itertools import combinations
from pathlib import Path
from time import perf_counter

from src.dados import carregar_aulas
from src.capacidade import alocar_com_capacidade, capacidades_minimas, excessos_de_capacidade
from src.exato import MAX_AULAS, minimo_de_salas
from src.guloso import alocar
from src.limite import profundidade


RAIZ = Path(__file__).resolve().parent


def carregar_estrategias():
    """Lê ESTRATEGIAS como mapa nome -> função ou sequência de pares."""
    try:
        modulo = importlib.import_module("src.linhas_base")
    except ModuleNotFoundError as erro:
        if erro.name != "src.linhas_base":
            raise
        raise ValueError("src/linhas_base.py ausente; não é possível executar "
                         "a comparação completa") from erro
    registro = modulo.ESTRATEGIAS
    pares = registro.items() if isinstance(registro, Mapping) else registro
    estrategias = {}
    for nome, funcao in pares:
        if not isinstance(nome, str) or not nome or not callable(funcao):
            raise ValueError("ESTRATEGIAS deve conter pares de nome e função de alocação")
        if nome in estrategias or nome in {"guloso", "limite", "capacidade_best_fit"}:
            raise ValueError(f"nome de estratégia duplicado ou reservado: {nome!r}")
        estrategias[nome] = funcao
    if not estrategias:
        raise ValueError("ESTRATEGIAS não pode estar vazio")
    return estrategias


def contar_conflitos(aulas, salas):
    """Confere o contrato e conta pares sobrepostos na mesma sala."""
    if not isinstance(salas, list) or len(salas) != len(aulas):
        raise ValueError("a alocação deve ser list[int] na mesma ordem das aulas")
    if any(type(sala) is not int or sala < 0 for sala in salas):
        raise ValueError("os números de sala devem ser inteiros não negativos")
    return sum(salas[i] == salas[j] and aulas[i].sobrepoe(aulas[j])
               for i, j in combinations(range(len(aulas)), 2))


def comparar(aulas, estrategias):
    """Compara o guloso e as linhas de base com o limite; preserva a entrada."""
    inicio = perf_counter()
    limite = profundidade(aulas)
    resultados = [{"estrategia": "limite", "aulas": len(aulas), "salas": limite,
                   "limite": limite, "excesso": 0, "conflitos": "",
                   "tempo_ms": round((perf_counter() - inicio) * 1000, 6)}]
    alocacoes = []
    for nome, funcao in [("guloso", alocar), *estrategias.items()]:
        # Uma estratégia que ordena a própria lista não modifica as demais.
        inicio = perf_counter()
        salas = funcao(aulas[:])
        tempo = (perf_counter() - inicio) * 1000
        conflitos = contar_conflitos(aulas, salas)
        total = len(set(salas))
        if nome == "guloso" and (conflitos or total != limite):
            raise ValueError("o guloso não produziu uma alocação ótima sem conflitos")
        resultados.append({"estrategia": nome, "aulas": len(aulas), "salas": total,
                           "limite": limite, "excesso": total - limite,
                           "conflitos": conflitos, "tempo_ms": round(tempo, 6)})
        for indice, (aula, sala) in enumerate(zip(aulas, salas)):
            alocacoes.append({"estrategia": nome, "indice_aula": indice,
                              "turma": aula.turma, "dia": aula.dia,
                              "inicio": aula.inicio, "fim": aula.fim,
                              "vagas": aula.vagas, "sala": sala})
    return resultados, alocacoes


def validar_subamostras(aulas, quantidade=10, tamanho=12, semente=44):
    """Sorteia índices reproduzíveis e compara exato, guloso e limite."""
    if quantidade < 0 or not 1 <= tamanho <= MAX_AULAS:
        raise ValueError(f"amostras deve ser >= 0 e tamanho deve estar entre 1 e {MAX_AULAS}")
    rng = random.Random(semente)
    resultados = []
    for numero in range(1, quantidade + 1):
        indices = sorted(rng.sample(range(len(aulas)), min(tamanho, len(aulas))))
        amostra = [aulas[i] for i in indices]
        limite = profundidade(amostra)
        inicio = perf_counter()
        salas = alocar(amostra)
        tempo_guloso = (perf_counter() - inicio) * 1000
        conflitos = contar_conflitos(amostra, salas)
        inicio = perf_counter()
        exato = minimo_de_salas(amostra)
        tempo_exato = (perf_counter() - inicio) * 1000
        total = len(set(salas))
        confere = not conflitos and total == exato == limite
        resultados.append({"amostra": numero, "semente": semente,
                           "indices_aulas": " ".join(map(str, indices)),
                           "aulas": len(amostra), "limite": limite,
                           "salas_guloso": total, "salas_exato": exato,
                           "conflitos": conflitos, "confere": confere,
                           "tempo_guloso_ms": round(tempo_guloso, 6),
                           "tempo_exato_ms": round(tempo_exato, 6)})
    return resultados


def salvar_csv(caminho, campos, registros):
    with caminho.open("w", encoding="utf-8", newline="") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=campos)
        escritor.writeheader()
        escritor.writerows(registros)


def dimensionar_capacidades(aulas, alocacoes, capacidades=None):
    """Dimensiona as salas de cada estratégia e verifica o inventário quando usado."""
    por_estrategia = {}
    for registro in alocacoes:
        por_estrategia.setdefault(registro["estrategia"], []).append(registro)
    resultados = []
    for nome, registros in por_estrategia.items():
        registros.sort(key=lambda registro: registro["indice_aula"])
        salas = [registro["sala"] for registro in registros]
        minimas = capacidades_minimas(aulas, salas)
        if nome == "capacidade_best_fit":
            if capacidades is None or excessos_de_capacidade(aulas, salas, capacidades):
                raise ValueError("a alocação com capacidade excedeu o inventário informado")
        for sala in sorted(set(salas)):
            disponivel = capacidades[sala] if nome == "capacidade_best_fit" else ""
            resultados.append({"estrategia": nome, "sala": sala,
                               "capacidade_minima": minimas[sala],
                               "capacidade_informada": disponivel,
                               "adequada": minimas[sala] <= disponivel if disponivel != "" else ""})
    return resultados


def imprimir_tabela(registros, campos):
    linhas = [[str(registro[campo]) for campo in campos] for registro in registros]
    larguras = [max([len(campo)] + [len(linha[i]) for linha in linhas])
                for i, campo in enumerate(campos)]
    for linha in [campos, ["-" * largura for largura in larguras], *linhas]:
        print(" | ".join(valor.ljust(largura) for valor, largura in zip(linha, larguras)))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("caminho", nargs="?", type=Path,
                        default=RAIZ / "data/raw/turmas_gama_2026_2.csv")
    parser.add_argument("--saida", type=Path, default=RAIZ / "resultados")
    parser.add_argument("--amostras", type=int, default=10)
    parser.add_argument("--tamanho", type=int, default=12)
    parser.add_argument("--semente", type=int, default=44)
    parser.add_argument("--capacidades", type=int, nargs="+",
                        help="inventário opcional: capacidade da sala 0, sala 1, etc.")
    args = parser.parse_args(argv)
    if args.amostras < 0 or not 1 <= args.tamanho <= MAX_AULAS:
        parser.error(f"--amostras deve ser >= 0 e --tamanho deve estar entre 1 e {MAX_AULAS}")
    try:
        aulas = carregar_aulas(args.caminho)
        estrategias = carregar_estrategias()
        if args.capacidades is not None:
            estrategias["capacidade_best_fit"] = lambda aulas: alocar_com_capacidade(aulas, args.capacidades)
        resumo, alocacoes = comparar(aulas, estrategias)
        capacidades = dimensionar_capacidades(aulas, alocacoes, args.capacidades)
        amostras = validar_subamostras(aulas, args.amostras, args.tamanho, args.semente)
        args.saida.mkdir(parents=True, exist_ok=True)
        salvar_csv(args.saida / "resumo.csv",
                   ["estrategia", "aulas", "salas", "limite", "excesso", "conflitos", "tempo_ms"],
                   resumo)
        salvar_csv(args.saida / "alocacoes.csv",
                   ["estrategia", "indice_aula", "turma", "dia", "inicio", "fim", "vagas", "sala"],
                   alocacoes)
        salvar_csv(args.saida / "subamostras.csv",
                   ["amostra", "semente", "indices_aulas", "aulas", "limite", "salas_guloso",
                    "salas_exato", "conflitos", "confere", "tempo_guloso_ms", "tempo_exato_ms"],
                   amostras)
        salvar_csv(args.saida / "capacidades.csv",
                   ["estrategia", "sala", "capacidade_minima", "capacidade_informada", "adequada"],
                   capacidades)
    except (OSError, ValueError, AttributeError) as erro:
        parser.exit(1, f"Erro: {erro}\n")

    print(f"Dados: {args.caminho.resolve()}")
    imprimir_tabela(resumo, ["estrategia", "aulas", "salas", "limite", "excesso", "conflitos", "tempo_ms"])
    if amostras:
        print("\nComparação em subamostras:")
        imprimir_tabela(amostras, ["amostra", "aulas", "limite", "salas_guloso", "salas_exato", "confere"])
    print(f"\nCSVs salvos em: {args.saida.resolve()}")
    return int(any(r["conflitos"] for r in resumo) or any(not r["confere"] for r in amostras))


if __name__ == "__main__":
    raise SystemExit(main())
