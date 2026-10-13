---
format: 1920x1080
duration: 66s
message: "O código real do Adapter rodando: OFX, Excel e CSV viram o mesmo Transaction; formato novo = adaptador novo."
arc: how-to-process
audience: "Turma de Engenharia de Software (ADS)"
mode: autonomous
music: none
---

## Video direction

- **Formato:** um editor estilo VS Code em tema CLARO (a professora exige fundo claro) ocupando o quadro inteiro: barra de título, explorador de arquivos à esquerda, abas, editor com números de linha e painel de terminal que sobe por baixo. Todos os quadros usam a mesma moldura, então os cortes parecem uma única gravação de tela.
- **Conteúdo:** o código é lido dos arquivos reais em `../../codigo/src`, e o terminal mostra a saída real de `npm run` (`capture/run/*.txt`).
- **Sem narração, sem legendas, sem música.** O ritmo deixa tempo de leitura: os apresentadores explicam ao vivo.
- **Paleta:** editor #fbfbf9, barra lateral e abas #f1efeb, terminal #f3f2ee; sintaxe do deck (palavras-chave #c2410c, tipos #2556c9, strings #157a3c, números #9a5b00, comentários #8b8d92); laranja #ff6a13 só no destaque de linha e na aba ativa.
- **Movimento:** digitação em degraus (determinística), faixa de destaque varrendo a linha ativa, troca de abas por corte seco, terminal subindo com settle `power3`. Nada de bounce, breathing ou pan.

## Frame 1 — O contrato

- src: compositions/frames/01-contrato.html
- type: product_intro
- duration: 9s
- transition_in: cut
- status: animated
- scene: Abre transaction.ts (modelo) e depois transaction-file-adapter.ts (a interface Target); a linha de parse() é destacada.

## Frame 2 — Passo 1: OfxAdapter

- src: compositions/frames/02-ofx.html
- type: feature_showcase
- duration: 14s
- transition_in: cut
- status: animated
- scene: Abre adapters/ofx.adapter.ts; destaca o mapeamento campo a campo; o terminal sobe e roda `npm run importar data/extrato.ofx` com a saída real.

## Frame 3 — Passo 2: ExcelAdapter

- src: compositions/frames/03-excel.html
- type: feature_showcase
- duration: 12s
- transition_in: cut
- status: animated
- scene: Abre adapters/excel.adapter.ts; destaca as colunas da planilha; roda `npm run importar data/extrato.xlsx` com a mesma saída.

## Frame 4 — Passo 3: comparar

- src: compositions/frames/04-comparar.html
- type: social_proof
- duration: 10s
- transition_in: cut
- status: animated
- scene: Abre transaction-import-service.ts e destaca `adapter.parse(content)`; roda `npm run comparar` → "✓ mesmo objeto Transaction".

## Frame 5 — Passo 4: formato novo (CSV)

- src: compositions/frames/05-csv.html
- type: feature_showcase
- duration: 21s
- transition_in: cut
- status: animated
- scene: Roda `npm run importar data/extrato.csv` → "✗ Formato não suportado: .csv"; cria adapters/csv.adapter.ts (digitado); adiciona 2 linhas em adapter-resolver.ts; roda de novo → mesma saída. No explorador, csv.adapter.ts aparece como U, adapter-resolver.ts como M, e o serviço segue sem marca.
