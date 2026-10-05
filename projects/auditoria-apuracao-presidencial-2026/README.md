# Auditoria técnica da divulgação presidencial — Eleições 2026

Projeto de auditoria **reprodutível e neutra** para investigar integridade, rastreabilidade e consistência temporal dos arquivos públicos de divulgação do resultado presidencial de 2026.

## Objetivo

Verificar tecnicamente, com evidências reproduzíveis:

- lacunas entre versões publicadas;
- perda de rastreabilidade;
- regressões de contadores;
- alteração de votos absolutos entre versões;
- divergências entre agregados nacional/UF/município/seção;
- mudanças de arquivo sem mudança lógica e mudanças lógicas sem mudança esperada de versão;
- comportamento de cache/CDN, ETag, Last-Modified e timestamps;
- hash byte a byte e hash canônico de JSON;
- cadeia de custódia das evidências coletadas;
- compatibilidade entre Boletins de Urna publicados e totalização, quando os arquivos necessários estiverem disponíveis.

O projeto **não parte da hipótese de fraude**. Uma pausa, salto percentual ou grande lote não prova manipulação. Toda conclusão deve distinguir fato observado, hipótese técnica, limitação de dados e causa confirmada.

## Fontes principais

- TSE — Informações técnicas sobre a divulgação de resultados 2026  
  https://www.tse.jus.br/eleicoes/informacoes-tecnicas-sobre-a-divulgacao-de-resultados
- TSE — Divulgação de resultados  
  https://www.tse.jus.br/eleicoes/historia/processo-eleitoral-brasileiro/divulgacao-de-resultados
- TSE — Apuração x totalização  
  https://www.tse.jus.br/comunicacao/noticias/2026/Outubro/entenda-a-diferenca-entre-apuracao-e-totalizacao-de-votos
- TSE — Resolução 23.751/2026  
  https://www.tse.jus.br/legislacao/compilada/res/2026/resolucao-no-23-751-de-26-de-fevereiro-de-2026
- Base histórica usada para a linha do tempo:
  https://github.com/ArvorCo/PNAD/blob/main/analysis/apuracao_2026/dados/linha_do_tempo.json

## Estrutura

```
.
├── CLAUDE_PROMPT.md
├── README.md
├── requirements.txt
├── data/
│   └── README.md
├── docs/
│   └── METODOLOGIA.md
└── scripts/
    ├── audit_timeline.py
    ├── fetch_tse_snapshot.py
    └── hash_chain.py
```

## Execução rápida

```bash
python scripts/audit_timeline.py --input linha_do_tempo.json --out output
python scripts/hash_chain.py --input data/raw --out output/hash_manifest.csv
```

Para coletar arquivos oficiais, coloque URLs completas em `urls.txt`, uma por linha:

```bash
python scripts/fetch_tse_snapshot.py --urls urls.txt --out data/raw
```

## Regras de evidência

Classifique cada achado como:

1. **Fato confirmado** — reproduzido diretamente em artefato oficial ou em dois artefatos independentes.
2. **Inconsistência observada** — dado que viola uma invariável esperada e precisa de explicação.
3. **Hipótese técnica** — causa possível ainda sem prova.
4. **Comportamento esperado** — mudança explicada pela entrada de novas seções/lotes.
5. **Não demonstrável com os dados disponíveis**.

Nunca use queda percentual como sinônimo de perda de votos. O teste de retirada exige queda em **voto absoluto** ou evidência de substituição/reprocessamento de registros.
