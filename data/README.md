# Oferta de turmas da UnB Gama

## Fonte e recorte

A fonte é a [consulta pública de turmas do SIGAA da UnB](https://sigaa.unb.br/sigaa/public/turmas/listar.jsf).
A [Faculdade de Medicina da UnB](https://fm.unb.br/graduacao/secretaria-de-graduacao-assuntos/lista-de-ofertas)
também indica esse portal para consultar a oferta, incluindo horários e vagas.

O recorte escolhido para este projeto é **UnB Gama, graduação, semestre
2026.2**. No filtro de unidade do SIGAA, selecione **CAMPUS UNB GAMA:
FACULDADE DE CIÊNCIAS E TECNOLOGIAS EM ENGENHARIA - BRASÍLIA**
(FCTE, anteriormente FGA; valor `673` no formulário verificado).
O conjunto de dados inclui as turmas de graduação ofertadas por essa
unidade. Os resultados do projeto se referem a esse recorte.
O filtro é a **unidade ofertante**, e não o endereço da sala: a turma
`FGA0299-01`, por exemplo, aparece na consulta do Gama com local informado
como `FT - UnB / Campus Darcy Ribeiro` e foi preservada no conjunto.
A oferta pode mudar; registre a data da coleta e preserve o arquivo usado
nos experimentos para permitir a reprodução dos resultados.

## Verificação de acesso e exportação

Verificação e recebimento do conteúdo da consulta em **05/10/2026**:

- O formulário público foi acessado sem login. Ele contém os filtros
  **Nível de Ensino**, **Unidade** e **Ano - Período**.
- Unidade e ano/período aparecem como obrigatórios. A unidade do Gama
  está disponível no formulário com valor `673`.
- O formulário envia uma requisição POST e usa `javax.faces.ViewState`
  (JSF). Uma coleta automatizada precisa manter a sessão e ler o estado
  e o nome do botão Buscar do formulário, sem fixá-los no código.
- A tabela de resultados fornecida pelo usuário contém número da turma,
  ano/período, docente, horário, **Qtde Vagas Ofertadas**, vagas ocupadas e
  local, agrupados por código e nome do componente curricular. A página
  informa **229 turmas encontradas**, e todas as 229 foram extraídas.
- Não foi encontrado um controle de exportação CSV/XLS no formulário
  inicial nem uma indicação de exportação no texto dos resultados enviado.
  A cópia textual não permite descartar controles representados por ícones;
  portanto, não há exportação direta confirmada.
- A coleta usada nos experimentos foi obtida por **extração do texto da
  tabela**, copiado do navegador pelo usuário. Isso permite gerar o CSV
  sem depender de exportação nativa nem transcrever turmas manualmente.
  A raspagem HTTP automática não foi concluída: as tentativas de POST
  retornaram erro de página inativa, mesmo mantendo a sessão.

**Decisão de coleta:** preservar o texto fornecido e normalizar a tabela
para CSV. Para atualizar a oferta, repetir a consulta no navegador e salvar
o HTML ou copiar o texto completo dos resultados. Uma raspagem diretamente
do SIGAA exigirá resolver a manutenção da sessão JSF; isso não impede o uso
da coleta já obtida. Não há necessidade de consultar detalhes adicionais
para obter os quatro campos desta coleta.

## Como obter o arquivo

1. Abra a consulta pública e selecione **GRADUAÇÃO**, ano **2026** e período
   **2**. Escolha **CAMPUS UNB GAMA: FACULDADE DE CIÊNCIAS E TECNOLOGIAS
   EM ENGENHARIA - BRASÍLIA** e clique em **Buscar**.
2. Use o código e nome do componente que agrupam as linhas, o número da
   turma na coluna **Código**, o **Horário** e a **Qtde Vagas Ofertadas**.
   Não use **Qtde Vagas Ocupadas** como quantidade de vagas da turma.
3. Salve o HTML dos resultados ou copie o texto completo para
   `data/raw/gama_2026_2.txt`, incluindo filtros e total de turmas. Se houver
   exportação, também preserve o arquivo original. Percorra todas as páginas
   caso haja paginação. Cabeçalhos de disciplina e totais não são turmas.
4. Confira se os resultados correspondem à graduação, unidade do Gama e
   semestre 2026.2. Registre eventuais erros. Não classifique uma consulta
   com erro como uma unidade sem oferta. Se precisar salvar pelo navegador,
   use `data/raw/gama_2026_2.html` para a primeira página e nomes distintos
   para as demais páginas, caso haja paginação.
5. Consolide os registros no formato abaixo. Uma turma encontrada em mais
   de uma consulta deve aparecer uma única vez: use o identificador do
   SIGAA, quando disponível. Não remova turmas distintas só porque têm
   o mesmo horário, disciplina ou número de turma.
6. Salve a coleta em `data/raw/turmas_gama_2026_2.csv` e preencha os números de
   conferência desta documentação. Preserve também, em `data/raw/`, um
   registro dos filtros, data, unidade consultada e arquivos de origem.

### Normalização da coleta recebida

- O identificador `turma` é `CODIGO_DO_COMPONENTE-NUMERO_DA_TURMA`, por
  exemplo `FGA0124-01`. As 229 combinações são distintas no texto recebido.
- `disciplina` preserva o cabeçalho completo de código e nome do componente.
- `horario` preserva todos os blocos do código, na ordem publicada, removendo
  apenas o sufixo de datas, como `(10/08/2026 - 14/12/2026)`. Espaços externos
  e linhas vazias de apresentação são removidos. Docentes e suas cargas
  horárias não fazem parte do código de horário.
- `vagas` vem da primeira coluna numérica da linha de capacidade, a de vagas
  **ofertadas**. Informações de local, inclusive observações sobre capacidade,
  não substituem esse valor. Por exemplo, `FGA0244-01` tem **80** vagas
  ofertadas, apesar de 117 ocupadas e da observação de 120 vagas no local.
- Nenhum horário foi corrigido ou inventado; todos os códigos extraídos
  foram aceitos por `aulas_da_turma`.

Arquivos locais desta coleta:

| Arquivo em `data/raw/` | Conteúdo |
|---|---|
| `gama_2026_2.txt` | Cópia integral do texto fornecido pelo usuário. |
| `turmas_gama_2026_2.csv` | 229 turmas normalizadas no formato abaixo. |
| `coleta_gama_2026_2.json` | Fonte, filtros, data de recebimento, contagens e hashes SHA-256 da fonte e do CSV. |

Para raspagem, faça as consultas sequencialmente, com intervalo entre
requisições, mantenha a sessão da consulta pública e interrompa a coleta
se houver erro de sessão. Não use o portal autenticado como substituto
silencioso da fonte pública.

## Formato de `data/raw/turmas_gama_2026_2.csv`

CSV em **UTF-8**, aceitando BOM, separado por **vírgulas**, com cabeçalho
exatamente nesta ordem e **uma linha por turma**, não por encontro semanal:

```csv
turma,disciplina,horario,vagas
```

| Coluna | Conteúdo |
|---|---|
| `turma` | Identificador único da turma no semestre, tratado como texto. Preferir o ID do SIGAA; se indisponível, combinar código do componente e número da turma e conferir colisões. `01` sozinho não identifica uma turma. |
| `disciplina` | Código e nome do componente curricular, como publicados na fonte. |
| `horario` | Código do SIGAA, por exemplo `35T23` ou `24M12 6T34`. Campo vazio se a turma não tiver horário. |
| `vagas` | Número inteiro não negativo de vagas **totais ofertadas**, não vagas restantes nem quantidade de matriculados. |

Exemplo **fictício**, apenas para ilustrar o formato:

```csv
turma,disciplina,horario,vagas
EXEMPLO001-01,EXEMPLO001 - Disciplina A,35T23,40
EXEMPLO002-02,EXEMPLO002 - Disciplina B,24M12 6T34,30
EXEMPLO003-01,EXEMPLO003 - Disciplina C,,20
```

Use aspas duplas para campos que contenham vírgulas ou aspas, conforme
as regras usuais de CSV. Preserve zeros à esquerda dos identificadores.
Não invente horários ou vagas: valores de vagas ausentes precisam ser
resolvidos na fonte antes de considerar o arquivo completo; zero só
representa zero vagas quando isso estiver informado na fonte.

Preserve turmas sem horário no CSV. Um marcador textual de ausência
(por exemplo, um traço) pode virar campo vazio, mas registre essa
normalização na descrição da coleta. Preserve códigos não vazios que
pareçam inválidos para que o carregador possa contá-los e relatá-los.

O carregador deve transformar cada registro em aulas usando
`aulas_da_turma(turma, horario, vagas)`, de `src/horarios.py`. Uma turma
pode gerar várias aulas. Os dias vão de 2 (segunda) a 7 (sábado), e os
intervalos são semiabertos, em minutos desde 00:00. A capacidade das salas
não é uma restrição do problema de particionamento de intervalos.

`data/raw/` está no `.gitignore`: os dados e os arquivos de origem ficam
fora do versionamento. Os exemplos fictícios não substituem a coleta real.

## Números para conferência

As contagens abaixo foram obtidas da cópia textual da consulta fornecida
pelo usuário. O CSV contém exatamente o total de turmas declarado pelo
SIGAA, sem identificadores duplicados.

| Medida | Gama, graduação, 2026.2 |
|---|---|
| Data de recebimento do texto da consulta | 05/10/2026 |
| Unidade consultada | Gama / FCTE (`673`) |
| Total de turmas declarado pelo SIGAA | 229 |
| Total de turmas distintas (linhas do CSV, sem cabeçalho) | 229 |
| Componentes curriculares distintos | 133 |
| Turmas sem horário | 0 |
| Turmas com horário inválido | 0 |
| Turmas com horário válido | 229 |
| Total de aulas geradas pelos horários válidos | 430 |
| Soma de vagas ofertadas nas turmas | 11.836 |

A soma de vagas conta vagas em turmas, não estudantes distintos nem salas.
Os 430 encontros são aulas semanais do modelo, não ocorrências repetidas
ao longo de todas as semanas do semestre.

Após obter o arquivo, rode o trecho abaixo na raiz do repositório. Ele
usa somente a biblioteca padrão e o conversor já existente; não depende
do futuro `src/dados.py`. Pode ser salvo temporariamente como um script
Python e executado com `python caminho_do_script.py`.

```python
import csv
from pathlib import Path

from src.horarios import aulas_da_turma

caminho = Path("data/raw/turmas_gama_2026_2.csv")
with caminho.open(encoding="utf-8-sig", newline="") as arquivo:
    leitor = csv.DictReader(arquivo)
    assert leitor.fieldnames == ["turma", "disciplina", "horario", "vagas"]
    registros = list(leitor)

ids = set()
sem_horario = invalidas = validas = total_aulas = 0
for linha, registro in enumerate(registros, start=2):
    assert None not in registro and None not in registro.values(), linha
    turma = registro["turma"].strip()
    assert turma and turma not in ids, (linha, turma)
    ids.add(turma)
    assert registro["disciplina"].strip(), linha
    vagas = int(registro["vagas"])
    assert vagas >= 0, linha
    codigo = registro["horario"].strip()
    if not codigo:
        sem_horario += 1
        continue
    try:
        aulas = aulas_da_turma(turma, codigo, vagas)
    except ValueError:
        invalidas += 1
    else:
        validas += 1
        total_aulas += len(aulas)

assert len(registros) == sem_horario + invalidas + validas
print(f"Total de turmas: {len(registros)}")
print(f"Sem horário: {sem_horario}")
print(f"Horário inválido: {invalidas}")
print(f"Horário válido: {validas}")
print(f"Aulas geradas: {total_aulas}")
```

Essas contagens conferem o CSV, mas não provam que a coleta cobre toda
a oferta de graduação do Gama. Confira também a contagem da consulta de
origem e se todas as páginas foram incluídas, levando em conta turmas
repetidas entre consultas.
