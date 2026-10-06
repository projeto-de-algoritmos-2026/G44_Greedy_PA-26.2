# Salas da UnB

**Número do Grupo:** 44  ·  **Conteúdo da Disciplina:** Algoritmos Gulosos

Dada a oferta de turmas de um semestre da UnB, quantas salas são necessárias, no mínimo, para que nenhuma aula se sobreponha a outra na mesma sala?

## Alunos

| Matrícula | Aluno |
|---|---|
| _a preencher_ | Giovanni Dornelas Ferreira |
| _a preencher_ | _a preencher_ |

## Sobre

O problema é o de **Particionamento de Intervalos** (*interval partitioning*): cada aula é um intervalo de tempo, e queremos distribuir todos os intervalos no menor número de salas de modo que, dentro de uma sala, nenhum par se sobreponha.

(seção a ser detalhada)

## O algoritmo

### Alocação de salas

A função `alocar(aulas)`, de [src/guloso.py](src/guloso.py), resolve o
particionamento de intervalos. Cada encontro é um
`Aula(turma, dia, inicio, fim, vagas)`: os dias vão de 2 (segunda-feira)
a 7 (sábado), e os horários são minutos desde 00:00. O intervalo é
**semiaberto**, `[inicio, fim)`, portanto uma aula que termina às 10:00
pode compartilhar a sala com outra que começa às 10:00.

O algoritmo processa cada dia separadamente:

1. Ordena as aulas por horário de início, mantendo seus índices originais.
2. Mantém um heap mínimo de pares `(fim, sala)`, com o fim da última aula
   atribuída a cada sala. O topo indica a sala que libera primeiro.
3. Se o topo tiver `fim <= inicio` da aula atual, reutiliza essa sala e
   atualiza seu fim no heap.
4. Caso contrário, abre uma nova sala e insere seu par no heap.
5. Registra o número da sala na posição original da aula.

O retorno é uma `list[int]`, com `salas[i]` indicando a sala de `aulas[i]`.
A entrada não é modificada. As salas são numeradas a partir de zero em
cada dia: a sala 0 de segunda-feira e a sala 0 de terça-feira representam
a mesma sala física. Por isso, o número de salas da semana é o **máximo
dos totais diários**, e não sua soma. Para uma entrada vazia, o retorno é
`[]` e são necessárias zero salas.

Exemplo em uma segunda-feira:

| Aula | Intervalo | Sala |
|---|---|---|
| A | 08:00–10:00 | 0 |
| B | 09:00–11:00 | 1 |
| C | 10:00–12:00 | 0 |

Nesse exemplo, `alocar(aulas)` retorna `[0, 1, 0]`: A e B se sobrepõem,
mas C pode reutilizar a sala de A exatamente às 10:00.
O campo `vagas` é preservado nos dados; o modelo considera salas
intercambiáveis e não impõe restrições de capacidade ou equipamento.

### Prova de otimalidade

A **profundidade** é o maior número de aulas simultâneas em um mesmo dia
e instante. Se há `D` aulas simultâneas, qualquer alocação sem conflitos
precisa de pelo menos `D` salas. Esse limite inferior é calculado por
`profundidade(aulas)`, de [src/limite.py](src/limite.py).

Primeiro, o guloso sempre produz uma alocação válida. Ao reutilizar uma
sala, a última aula nela termina até o início da nova aula. Como as aulas
são processadas por início, a nova aula também não conflita com as aulas
anteriores dessa sala. Ao abrir uma sala, ela está vazia. Aulas em dias
diferentes não se sobrepõem.

Agora suponha que, em um dia, o algoritmo abra a **d-ésima sala**
(identificador `d - 1`) para uma aula que começa no instante `t`.
Para `d = 1`, a própria aula já exige uma sala. Para `d > 1`, a abertura
só ocorre quando o menor fim no heap é maior que `t`.
Logo, a última aula de cada uma das `d - 1` salas existentes termina
depois de `t`. Todas essas aulas começaram até `t`, pois foram processadas
antes da aula atual. Assim, elas estão acontecendo em `t`, juntamente
com a aula atual: há **d aulas simultâneas**. Qualquer solução precisa,
portanto, de pelo menos `d` salas.

Aplicando esse argumento à abertura da última sala do dia, o guloso usa
exatamente o mínimo necessário naquele dia. Os conjuntos de salas podem
ser reutilizados entre dias; consequentemente, o mínimo semanal é o
máximo dos mínimos diários. Concluímos que o número de salas do guloso é
igual à profundidade `D` de todo o conjunto, atingindo o limite inferior.

### Complexidade

Para `n` aulas, o agrupamento por dia custa **O(n)**. A ordenação custa
**O(n log n)** no total, e cada aula faz uma operação de heap de custo
**O(log n)**. Portanto, o tempo total é **O(n log n)** e o espaço auxiliar
é **O(n)**, incluindo os grupos, os heaps e a lista de alocação.

### Seleção de reservas em um auditório

O módulo [src/selecao.py](src/selecao.py) trata a variante em que há apenas
um auditório e queremos atender o maior número de pedidos em um dia.
`selecionar(pedidos)` ordena os pedidos por **menor horário de fim** e
aceita cada pedido que começa depois ou exatamente no fim do último
aceito. Retorna os pedidos escolhidos, com tempo **O(n log n)**.

A escolha é ótima por um argumento de troca: seja `g` o pedido que
termina mais cedo e `o` o primeiro pedido de uma seleção ótima.
Como `fim(g) <= fim(o)`, substituir `o` por `g` preserva a quantidade de
pedidos e a compatibilidade com todos os pedidos seguintes. Portanto,
existe uma solução ótima que começa com `g`. Repetindo o argumento nos
pedidos que começam a partir de `fim(g)`, obtemos a seleção gulosa inteira.

## Os dados

(seção a ser detalhada — instruções de download em `data/README.md`)

## Validação

(seção a ser detalhada)

## Achados

(seção a ser detalhada)

## Instalação

Requer Python 3.10 ou mais novo. Os comandos rodam da raiz do repositório.

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Testes

```bash
python -m unittest discover
```

## Apresentação

_link do vídeo_

## Referências

- KLEINBERG, J.; TARDOS, É. *Algorithm Design*. Pearson, 2005. Seção 4.1.
- CORMEN, T. H. et al. *Introduction to Algorithms*. 3. ed. Capítulo 16.
