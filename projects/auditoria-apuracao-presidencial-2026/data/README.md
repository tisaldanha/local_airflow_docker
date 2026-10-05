# Dados

Não versionar artefatos brutos coletados sem revisar tamanho, licença e sensibilidade.

Estrutura sugerida:

```
data/
├── raw/          # bytes exatamente recebidos
├── metadata/     # headers/timestamps
└── derived/      # transformações reproduzíveis
```

A fonte histórica inicial é `ArvorCo/PNAD`, mas qualquer conclusão deve ser reconferida contra fontes oficiais do TSE quando disponíveis.
