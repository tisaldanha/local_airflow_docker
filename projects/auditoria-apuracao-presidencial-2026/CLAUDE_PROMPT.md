# PROMPT PARA CLAUDE — Auditoria forense da divulgação presidencial 2026

Você atuará como **engenheiro de dados sênior, auditor forense de sistemas distribuídos e especialista em integridade de dados**, com foco em rastreabilidade, consistência temporal, arquivos JSON, hashes, cache/CDN, versionamento, reconciliação de agregados e cadeia de custódia.

Seu trabalho é realizar uma **auditoria técnica, reproduzível e politicamente neutra** dos dados públicos da eleição presidencial brasileira de 2026.

## PRINCÍPIO CENTRAL

NÃO assuma fraude, manipulação, erro ou normalidade.

Você deve testar hipóteses.

Uma pausa na divulgação, mudança percentual, lote grande ou comportamento visual estranho NÃO constitui prova de alteração de votos.

Só afirme que houve falha, perda, correção ou alteração quando houver evidência técnica reproduzível.

Sempre diferencie:

- falha de coleta;
- falha do coletor;
- falha de rede;
- cache/CDN;
- atraso de publicação;
- geração tardia de arquivo;
- problema de parser;
- problema de ordenação temporal;
- reprocessamento;
- regressão real de contador;
- inconsistência de totalização;
- simples mudança de composição geográfica dos novos votos.

---

# 1. FONTES

Use prioritariamente fontes oficiais do TSE.

Documentação técnica:

- https://www.tse.jus.br/eleicoes/informacoes-tecnicas-sobre-a-divulgacao-de-resultados
- https://www.tse.jus.br/eleicoes/historia/processo-eleitoral-brasileiro/divulgacao-de-resultados
- https://www.tse.jus.br/comunicacao/noticias/2026/Outubro/entenda-a-diferenca-entre-apuracao-e-totalizacao-de-votos
- https://www.tse.jus.br/legislacao/compilada/res/2026/resolucao-no-23-751-de-26-de-fevereiro-de-2026

Base histórica auxiliar já identificada:

- https://github.com/ArvorCo/PNAD
- arquivo principal:
  `analysis/apuracao_2026/dados/linha_do_tempo.json`

A base auxiliar NÃO deve ser tratada como fonte oficial sem validação. Use-a para reconstruir a sequência e depois confronte com os artefatos oficiais.

---

# 2. OBJETIVO

Quero saber exatamente:

1. onde existem gaps temporais;
2. se o gap é de geração, publicação, cache ou coleta;
3. se algum contador regrediu;
4. se votos absolutos de qualquer candidato diminuíram;
5. se votos válidos diminuíram;
6. se número de seções totalizadas diminuiu;
7. se dados mudaram sem incremento de seção;
8. se seções aumentaram enquanto votos válidos diminuíram;
9. se o agregado nacional deixou de refletir a soma dos estados;
10. por quanto tempo isso ocorreu;
11. se alguma versão mais antiga foi publicada depois de uma nova;
12. se houve repetição de conteúdo com timestamps diferentes;
13. se houve conteúdo diferente com mesmo identificador/versionamento;
14. se o cache/CDN devolveu conteúdo defasado;
15. se ETag/Last-Modified/Date/Age são coerentes;
16. se existe perda de rastreabilidade entre versões;
17. se existe alteração não explicada em arquivos de seção/BU;
18. se hashes de arquivos equivalentes mudaram;
19. se o arquivo nacional pode ser reconstruído a partir dos inferiores;
20. qual é a causa técnica mais provável de cada anomalia.

---

# 3. PRESERVAÇÃO E CADEIA DE CUSTÓDIA

Antes de analisar qualquer arquivo:

- nunca sobrescreva o original;
- armazene byte a byte em `data/raw`;
- registre URL completa;
- timestamp UTC e BRT da coleta;
- status HTTP;
- Content-Length;
- Content-Type;
- ETag;
- Last-Modified;
- Date;
- Age;
- Cache-Control;
- Via;
- servidor/CDN quando presente;
- SHA-256 do corpo bruto;
- tamanho em bytes.

Gere para cada arquivo:

- `raw_sha256`: hash dos bytes exatamente recebidos;
- `canonical_json_sha256`: hash do JSON normalizado com chaves ordenadas e separadores determinísticos;
- `content_length`;
- timestamp de geração declarado no JSON;
- timestamp de captura;
- URL.

Crie também uma cadeia de hashes:

```
chain_hash_n = SHA256(
    chain_hash_n-1
    + raw_sha256_n
    + url
    + captured_at_utc
)
```

Grave em:

- `output/chain_of_custody.jsonl`
- `output/hash_manifest.csv`

Não confunda hashes de software publicados pelo TSE com hashes de BUs ou arquivos de resultado. Antes de comparar qualquer hash, documente exatamente **o que aquele hash representa**.

---

# 4. RECONSTRUÇÃO MINUTO A MINUTO

Reconstrua toda a linha do tempo presidencial do primeiro turno de 2026.

Unidade mínima:

- versão real, com precisão de segundos;
- depois agregação por minuto para visualização.

Para cada versão nacional registre:

- `gerado_em`;
- `capturado_em`;
- identificador de geração/versionamento, se existir;
- seções totalizadas;
- percentual de seções;
- votos válidos;
- votos de TODOS os candidatos;
- votos brancos/nulos quando aplicável;
- diferenças para a versão imediatamente anterior.

Para cada candidato calcule:

```
delta_votos = votos_atual - votos_anterior
```

E:

```
delta_secoes
delta_votos_validos
delta_comparecimento
delta_brancos
delta_nulos
```

Não use somente percentuais.

Percentual pode cair enquanto votos absolutos sobem.

---

# 5. INVARIANTES OBRIGATÓRIAS

Teste automaticamente cada versão.

## A. Monotonicidade de seções

Flag se:

```
secoes_atual < secoes_anterior
```

Classificação inicial: ALTA.

## B. Monotonicidade de votos válidos

Flag se:

```
votos_validos_atual < votos_validos_anterior
```

Classificação inicial: ALTA.

## C. Monotonicidade por candidato

Para TODO candidato:

```
votos_candidato_atual < votos_candidato_anterior
```

Registrar exatamente quantos votos diminuíram.

NÃO conclua manipulação automaticamente. Investigue reprocessamento, versão regressiva, cache e retotalização.

## D. Coerência do lote

Se:

```
delta_votos_candidato > delta_votos_validos
```

flag CRÍTICO.

Se a soma dos deltas positivos de candidatos ultrapassar os novos votos válidos, investigar imediatamente.

## E. Mudança sem novas seções

Se:

```
delta_secoes == 0
AND
algum total eleitoral mudou
```

flag:

`VALUE_CHANGE_WITHOUT_SECTION_CHANGE`

Pode indicar:

- reprocessamento;
- correção;
- substituição;
- versão regressiva;
- alteração de situação jurídica;
- cache/ordenação;
- erro.

Investigue.

## F. Novas seções com redução de votos

Se:

```
delta_secoes > 0
AND
delta_votos_validos < 0
```

flag CRÍTICO.

## G. Timestamp regressivo

Detecte:

- `gerado_em` menor que versão anterior;
- captura nova contendo arquivo gerado antes;
- ID de geração regressivo;
- versão velha depois de versão nova.

---

# 6. HASH A HASH

Faça comparação hash a hash entre snapshots consecutivos.

Para cada par:

```
snapshot[n-1]
snapshot[n]
```

registre:

- raw SHA anterior;
- raw SHA atual;
- canonical SHA anterior;
- canonical SHA atual;
- igualdade byte a byte;
- igualdade lógica;
- campos alterados.

Se o raw hash mudar mas canonical hash não mudar:

classifique como:

`SERIALIZATION_ONLY_CHANGE`

Se ambos mudarem:

produza diff estruturado JSON path por JSON path.

Exemplo:

```
/abrangencia/secoes_totalizadas
/candidatos/22/votos
/candidatos/13/votos
/timestamp
```

NÃO produza apenas diff textual.

Gere:

`output/json_field_diffs.jsonl`

---

# 7. CACHE / CDN / HTTP

Verifique se o aparente gap pode ter sido gerado pela distribuição.

Analise:

- ETag repetido;
- Last-Modified congelado;
- HTTP 304;
- HTTP Date;
- Age;
- Cache-Control;
- Via;
- conteúdo repetido;
- body hash repetido.

Procure o padrão:

```
collector consulta
→ CDN responde 304 ou mesmo ETag
→ origem posteriormente publica versão muito mais avançada
```

Se isso ocorrer, não chame automaticamente de falha de totalização.

Classifique como possível:

- publication lag;
- cache lag;
- CDN lag;
- origin generation gap.

---

# 8. GAP TEMPORAL

Liste todos os gaps superiores a:

- 2 minutos;
- 5 minutos;
- 8 minutos;
- 10 minutos;
- 20 minutos;
- 30 minutos.

Para cada um mostre:

| início | fim | duração | seções antes | seções depois | Δ seções | Δ válidos | Δ candidato A | Δ candidato B | hash antes | hash depois |

Determine se no intervalo:

- arquivos UF continuaram mudando;
- arquivos municipais continuaram mudando;
- arquivos de outros cargos continuaram sendo gerados;
- nenhum arquivo de resultado foi gerado.

Isso permite separar:

`NATIONAL_AGGREGATION_LAG`

de:

`GLOBAL_PUBLICATION_GAP`

---

# 9. RECONCILIAÇÃO NACIONAL × UF

Para cada instante possível:

```
SUM(UF.secoes_totalizadas)
vs
BR.secoes_totalizadas
```

e:

```
SUM(UF.votos_candidato)
vs
BR.votos_candidato
```

Faça o mesmo para votos válidos.

Como arquivos não são necessariamente gerados no mesmo milissegundo:

- use nearest-before;
- use nearest-after;
- informe a defasagem temporal;
- nunca compare snapshots temporalmente incompatíveis sem avisar.

Produza:

`output/reconciliation_br_uf.csv`

Campos:

- timestamp;
- br_st;
- sum_uf_st;
- gap_st;
- br_candidate_votes;
- sum_uf_candidate_votes;
- gap_votes;
- max_age_seconds_das_ufs.

---

# 10. UF × MUNICÍPIO × SEÇÃO

Repita a reconciliação em cascata:

```
BR
↓
UF
↓
município
↓
zona
↓
seção
↓
BU
```

A chave preferencial é:

```
eleição
turno
UF
município
zona
seção
cargo
```

Identifique:

- seção duplicada;
- seção ausente;
- seção presente e depois ausente;
- seção com valores diferentes;
- mesma seção com dois conteúdos;
- mesma seção com hash diferente;
- substituição de BU.

---

# 11. BOLETINS DE URNA

Quando os BUs estiverem disponíveis:

1. preserve o arquivo original;
2. calcule SHA-256;
3. valide formato;
4. valide assinatura digital se houver documentação/chaves necessárias;
5. não diga que uma assinatura é válida se você não executou verificação criptográfica real;
6. extraia votos por seção;
7. compare com a totalização publicada.

Para cada seção gere:

`output/bu_reconciliation.csv`

com:

- UF;
- município;
- zona;
- seção;
- hash BU;
- votos BU;
- votos totalização;
- diferença;
- status.

Status:

- MATCH;
- MISMATCH;
- MISSING_BU;
- MISSING_TOTALIZATION;
- DUPLICATE_SECTION;
- CHANGED_HASH;
- UNVERIFIED_SIGNATURE.

---

# 12. RASTREABILIDADE

Para cada total agregado tente responder:

> Consigo explicar exatamente de quais registros inferiores esse número veio?

Exemplo:

```
BR Flávio = 48.704.246
```

Tente decompor até:

```
Σ votos Flávio por UF
Σ votos por município
Σ votos por seção
```

Se em algum nível não for possível reconstruir:

marque:

`TRACEABILITY_BREAK`

Informe:

- nível;
- intervalo de tempo;
- valor faltante;
- arquivos necessários;
- impacto.

---

# 13. PONTO CRÍTICO JÁ CONHECIDO PARA TESTE

Investigue de forma especial o intervalo:

```
04/10/2026 19:14:08 BRT
até
04/10/2026 20:04:39 BRT
```

Antes:

- 323.539 seções
- 64,805% das seções
- Flávio: 37.566.895
- Lula: 32.007.853

Depois:

- 424.153 seções
- 84,958%
- Flávio: 48.704.246
- Lula: 43.705.754

Diferença publicada de uma só vez:

- +100.614 seções
- +24.728.306 votos válidos
- Flávio: +11.137.351
- Lula: +11.697.901

Esses números são um ponto de partida da base histórica e DEVEM ser reconferidos.

Perguntas:

1. Os 24.728.306 votos são exatamente reconstruíveis pelas UFs?
2. Quais UFs produziram esse lote?
3. A soma dos arquivos estaduais já estava à frente do BR?
4. Desde quando?
5. Houve arquivos estaduais gerados durante o congelamento nacional?
6. Houve período sem geração de nenhum arquivo?
7. O arquivo BR ficou congelado na origem ou apenas no CDN?
8. ETag mudou?
9. Last-Modified mudou?
10. O hash do arquivo nacional permaneceu igual?
11. A primeira versão posterior contém todo o delta esperado?
12. Existe algum voto absoluto que tenha diminuído?

---

# 14. VERSÕES MARCADAS COMO REGRESSIVAS

A base auxiliar possui indicadores como `marcada_regressiva`.

NÃO interprete essa flag como perda de votos.

Para cada ocorrência:

- encontre o registro bruto;
- descubra qual identificador regrediu;
- compare valores eleitorais;
- compare hash;
- compare timestamp;
- classifique a causa.

Produza:

`output/regressive_versions.csv`

---

# 15. ANÁLISE DE PERDA DE DADOS

Procure:

- sequência quebrada de IDs;
- arquivo esperado ausente;
- versão referenciada mas não preservada;
- HTTP 404/timeout;
- lacuna de snapshots;
- truncamento de JSON;
- JSON inválido;
- Content-Length incompatível;
- download parcial;
- arquivo zero bytes;
- duplicação;
- alteração posterior do mesmo recurso sem preservação da versão antiga.

Classifique:

- DATA_LOSS_CONFIRMED;
- SNAPSHOT_NOT_CAPTURED;
- SOURCE_NOT_PUBLISHED;
- NETWORK_FAILURE;
- PARSER_FAILURE;
- UNKNOWN.

---

# 16. TESTES ESTATÍSTICOS — USO LIMITADO

Estatística pode identificar um lote incomum, mas NÃO prova alteração.

Calcule por lote:

- votos novos;
- % de cada candidato no lote;
- tamanho médio de seção;
- distribuição por UF;
- z-score apenas como triagem;
- comparação com lotes geograficamente semelhantes.

Nunca use "probabilidade baixa" como prova de fraude.

Se um lote for estatisticamente extremo, investigue primeiro sua composição geográfica.

---

# 17. CLASSIFICAÇÃO DE SEVERIDADE

Use:

## CRÍTICO
- voto absoluto diminui sem explicação documental;
- soma de componentes não fecha;
- BU diverge da totalização;
- seção tem dois conteúdos incompatíveis e ambos aparecem como válidos;
- integridade criptográfica falha.

## ALTO
- seções diminuem;
- votos válidos diminuem;
- mudança eleitoral sem mudança de seção;
- regressão de versão com impacto nos totais.

## MÉDIO
- gap longo;
- cache defasado;
- divergência temporária nacional × UF.

## BAIXO
- serialização;
- ordem de chaves;
- timestamp;
- atraso pequeno sem impacto.

---

# 18. RELATÓRIO FINAL

Crie:

`REPORT.md`

Estrutura:

## 1. Resumo executivo

Somente fatos comprovados.

## 2. Fontes e cadeia de custódia

## 3. Linha do tempo

## 4. Gaps

## 5. Hashes

## 6. Regressões

## 7. Reconciliação BR × UF

## 8. Reconciliação UF × município × seção

## 9. BUs

## 10. Cache/CDN

## 11. Falhas confirmadas

## 12. Anomalias sem explicação

## 13. Hipóteses descartadas

## 14. Limitações

## 15. Conclusão

A conclusão deve usar uma destas categorias para cada ponto:

- confirmado;
- consistente com os dados;
- inconsistente;
- inconclusivo;
- não testável.

---

# 19. ARQUIVOS DE SAÍDA

Obrigatórios:

```
output/
├── REPORT.md
├── anomalies.csv
├── timeline_versions.csv
├── timeline_minute.csv
├── gaps.csv
├── hash_manifest.csv
├── chain_of_custody.jsonl
├── json_field_diffs.jsonl
├── reconciliation_br_uf.csv
├── reconciliation_sections.csv
├── bu_reconciliation.csv
└── regressive_versions.csv
```

---

# 20. REGRA MAIS IMPORTANTE

Eu não quero uma narrativa.

Eu quero uma **auditoria reproduzível**.

Para cada alegação, mostre:

- arquivo;
- URL;
- timestamp;
- hash;
- versão anterior;
- versão posterior;
- campo;
- valor anterior;
- valor posterior;
- código que reproduz;
- evidência.

Se não conseguir provar uma hipótese, escreva explicitamente:

> "Não há evidência suficiente nos artefatos analisados para afirmar isso."

Se encontrar uma falha real, escreva:

> "Falha reproduzida", seguida do procedimento exato para reprodução.

Comece clonando os repositórios necessários, preserve as fontes brutas, gere o manifesto SHA-256 e só depois faça qualquer análise.
