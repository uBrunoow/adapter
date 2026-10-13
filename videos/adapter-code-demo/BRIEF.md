---
workflow: faceless-explainer
flow: automation
storyboard: no
message: "O código real do Adapter rodando: OFX, Excel e CSV viram o mesmo Transaction; formato novo = adaptador novo."
destination: embed
aspect: 1920x1080
language: pt-BR
audience: "Turma de Engenharia de Software (ADS) — conhece programação, está aprendendo padrões de projeto"
length: 60s
narration: none
captions: none
angle: how-to
---

## Intent

Vídeo de demonstração do código do padrão Adapter, embutido no slide "Veja o código rodando"
de uma apresentação de 10 minutos sobre padrões de projeto. Segue o roteiro do slide:
1) importar um arquivo OFX, 2) a mesma transação em Excel, 3) comparar as duas saídas
(mesmo objeto Transaction), 4) adicionar um formato novo (CSV) sem mexer no serviço.

## Customizations

- SEM narração e SEM legendas (pedido do usuário: "nao precisa de legenda nem narração"). A turma ouve os apresentadores ao vivo.
- Formato: editor estilo VS Code em tema claro + terminal, mostrando o código REAL do projeto ../../codigo e a saída real de `npm run` (capturada em capture/run/).
- Identidade visual do próprio deck (não um preset): fundo claro #fbfbf9, texto #17181b,
  laranja #ff6a13 / #c2410c, Inter Tight + JetBrains Mono, painéis de código claros #f3f2ee
  com sintaxe (.k #c2410c, .t #2556c9, .s #157a3c, .n #9a5b00), pinos de encaixe por formato
  (● OFX, ▲ Excel, ⬢ PDF, ✚ CSV, ■ Transaction).

## Notes

- Requisito da professora: fundo claro com letras escuras; código legível (cuidado com cores).
- O código mostrado deve ser o mesmo do deck (TypeScript): TransactionFileAdapter.parse(content),
  OfxAdapter, ExcelAdapter, TransactionImportService.import(content, adapter), mapa adapters.
- Saída final copiada para ../../demo-adapter.mp4 (ao lado do index.html do deck).
