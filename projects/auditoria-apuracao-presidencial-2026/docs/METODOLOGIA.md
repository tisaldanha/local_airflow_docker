# Metodologia de auditoria

## Separação de camadas

A análise deve tratar separadamente:

1. **urna/BU** — origem do resultado de uma seção;
2. **transmissão** — envio do resultado;
3. **totalização** — soma/estado lógico do resultado;
4. **geração de arquivo** — criação do JSON de divulgação;
5. **CDN/cache** — distribuição;
6. **coletor** — ferramenta que consulta e preserva;
7. **parser/análise** — transformação feita localmente.

Um gap observado na camada 6 não demonstra gap na camada 3.

## Hashes

Sempre preservar dois hashes:

- SHA-256 bruto dos bytes;
- SHA-256 canônico do JSON.

O hash bruto detecta qualquer mudança de byte. O canônico separa mudanças lógicas de mudanças de serialização.

## Temporalidade

Manter simultaneamente:

- horário declarado pelo artefato;
- horário HTTP;
- horário da captura;
- timezone original;
- UTC normalizado.

Nunca ordenar versões apenas pelo horário de captura se houver um identificador oficial de geração.

## Reconciliação

A soma de níveis inferiores deve ser comparada somente com snapshots temporalmente compatíveis. Para comparações aproximadas, registrar a idade máxima de cada componente.

## Evidência negativa

Ausência de evidência não é evidência de ausência. Quando um arquivo não foi preservado, classificar como lacuna de observabilidade, não como prova de que não existiu.

## Conclusão

O projeto busca identificar defeitos técnicos e inconsistências. Não deve converter anomalias em acusações sem prova documental ou reproduzível.
