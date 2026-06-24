# Progresso — futurecoder PT-BR (tema escuro + tradução + UX)

Plano: `docs/superpowers/plans/2026-06-24-futurecoder-dark-ptbr.md`

- [x] Task 1 — Marcador + baseline (baseline = `futurecoder-ptbr.png`, estado claro)
- [x] Task 2 — Tema escuro (`dark.scss`) ✅ verificado em `dark-1.png` (escuro, sem bug)
- [x] Task 3 — UI intuitiva: navbar escura, botões violeta, shell alinhado, Avançar/Retornar navegáveis, ☰ → quick menu do conteúdo, TOC profissional ✅ (verify-main/menu/toc.png)
- [x] Task 4 — merge_overrides.py + extract_missing.py (pipeline de overrides) ✅
- [x] Task 5 — Extraídos 79 rótulos de UI em inglês ✅
- [x] Task 6 — Gemini (bridge deliberation, 0-quota) traduziu os 79 rótulos → terms_br.json, mesclado, verificado (Sumário, Requisitos, etc.) ✅ verify-pt.png
- [~] Task 7 — Capítulo Dicionários (c12) ainda em inglês; resto do conteúdo já PT. Pendente: tradução-alvo SÓ do c12 (cuidado p/ não reescrever PT existente).
- [ ] Task 8 — Verificação final

## Correção importante (durável)
O futurecoder de precache deixou um **service worker cravado em localhost:8001** servindo build antigo (mascarava TODAS as mudanças). Solução: servir em **localhost:8002** (origem limpa, build novo sem precache não registra SW). `serve_futurecoder.py` agora usa :8002 + serve um SW stub auto-desregistrante.

> CHECKPOINT: ao fim de cada Task, marcar `[x]` e tirar screenshot.
