# IMPL — Prática de 3 níveis no futurecoder (as-built)

> **Documento "as-built".** Descreve o que foi **implementado e verificado**, complementando o design
> em [`SDD-pratica-3-niveis-futurecoder.md`](./SDD-pratica-3-niveis-futurecoder.md).
>
> - **Data:** 2026-06-25/26
> - **Status:** IMPLEMENTADO e verificado (build + unittest + Playwright)
> - **Branch:** `feat/plataforma-refactor`
> - **Regra:** editar SÓ em `datacamp/futurecoder-patches/` → `build_ptbr.sh` → servir `server.py`.

---

## 1. O que foi entregue

Painel **"🏋️ Pratique"** dentro de cada capítulo do curso (`/course/`), com exercícios em **3 níveis**
(formato inspirado no "30 Days of Python"), em PT-BR e alinhados a QA. O aluno escreve o código; a
plataforma roda no Pyodide e dá **dicas em escada** (nunca a solução). Mais: sistema de **gamificação**
(XP, 17 conquistas com raridade, streak diário) e **Modo Foco**.

- **47 exercícios** em 12 capítulos (`exercises_br.json`): **40 `write_code`** + **7 `write_test`**.
- Gerados por workflow multi-agente (gerar→verificar com Python real) e validados localmente
  (40/40 soluções passam; 7/7 mutantes 100% matáveis).

---

## 2. Arquitetura (arquivos)

### Frontend (`datacamp/futurecoder-patches/frontend/src/`)
| Arquivo | Papel |
|---------|-------|
| `exercises_br.json` | Banco de exercícios, keyed pelo **título do capítulo** (igual `media_br.json`). Schema em §3. **Sem `solution`** (removida do bundle). |
| `components/PracticePanel.jsx` | UI do painel: lista os níveis, editor (`textarea`, Tab indenta), "▶ Rodar"/"■ Parar", dicas em escada, feedback ✅/❌, XP, streak. Persiste em `localStorage` + servidor. |
| `components/PyodideRunner.js` | Monta a harness Python (base64), roda via `runRawPython`, parseia. **Loop-guard via AST** (§4). |
| `Worker.js` *(patch)* | Adiciona `runRaw(code)` — roda Python cru no MESMO Pyodide; trata KeyboardInterrupt. |
| `TaskClient.js` *(patch)* | `runRawPython(code)` + `interruptRaw()`. |
| `book/serverSync.js` *(patch)* | `savePracticeProgress(id, xp, mode)`. |
| `App.js` *(patch)* | Monta `<PracticePanel/>`; **XP + 17 badges** (raridade/progresso); chip de **streak 🔥**; botão **Foco**. |
| `css/dark.scss` *(patch)* | Estilos do painel, badges por raridade (brilho), streak, Modo Foco. |

### Backend (`datacamp/server.py`)
- `GET/POST /api/practice-progress` + tabela SQLite `practice_progress` (espelho do progresso).
- `record_attempt` agora em `try/finally` (não vaza conexão se o `agy` falhar).
- Testes: `tests/test_server.py` (10/10 verdes, 3 novos de practice-progress).

---

## 3. Schema de `exercises_br.json`

Keyed por título do capítulo → `{title, exercises[]}`. Cada exercício:

```
id, level (1|2|3), mode ("write_code"|"write_test"),
title, concept, prompt, starter, hints[] (escada, nunca a solução), xp
write_code:  tests[] = [{call, expect}]          (a solução fica no sidecar, fora do bundle)
write_test:  reference_impl, mutants[], min_tests
```

Solução de referência dos `write_code`: `datacamp/docs/exercises_solutions.json` (verificação, **não**
vai pro bundle).

---

## 4. Runner (Pyodide) — pontos importantes

- **Reuso do Pyodide** do futurecoder via `Worker.runRaw` (sem 2ª instância; mesma origem → seguro com
  o COOP/COEP que o `server.py` manda em `/course/*`).
- **`write_code`:** roda a função do aluno e compara cada `{call, expect}`.
- **`write_test` (mutation testing):** roda os testes do aluno na **referência** (devem passar) e em cada
  **mutante** (cada um deve falhar = "morto"). Aceita `assert` solto **e** `def test_`. Conta testes via
  **AST** (`ast.Assert` + `def test_`) — ignora comentário/string.
- **Loop infinito:** o código do aluno é **transformado via AST**, injetando um contador-guarda no início
  de cada `while`/`for`; após ~3M iterações levanta `RuntimeError`. É **in-process** porque, neste setup,
  nem `sys.settrace` nem o `interrupt` do pyodide-worker-runner funcionam (o canal de interrupt usa
  service worker, que foi desregistrado). Backup: botão "■ Parar" + timeout de 8s.
- **Anti-vazamento:** o payload (testes/mutantes) é decodificado em escopo local e `del`-etado dos globals.

---

## 5. Gamificação

- **XP/Nível:** páginas concluídas (×20) + XP de prática. Pill na navbar com barra de nível.
- **17 conquistas** (`BADGES` em `App.js`) com **raridade** (comum/raro/épico/lendário, cada uma com cor
  e brilho) e **barra de progresso** nas travadas. Categorias: páginas, capítulos, prática, XP, nível, streak.
- **Streak diário 🔥** (`localStorage futurecoder_streak_v1`): dias seguidos praticando; chip na navbar +
  badges de 3/7/30 dias; atualizado a cada exercício concluído.
- **Assets:** emoji + CSS (offline; o COEP de `/course/*` bloqueia imagens de CDN).

---

## 6. Modo Foco

Botão "Foco" na navbar: liga a classe `body.focus-mode` (esconde IDE/distrações, centraliza a aula) +
fullscreen best-effort. **Esc sai.** A classe e o estado são setados juntos (sem dessincronizar);
limpa ao desmontar.

---

## 7. Como rodar e verificar

```bash
python3 datacamp/server.py            # http://localhost:8000/course/
python3 -m unittest discover -s datacamp/tests   # 10/10
bash datacamp/build_ptbr.sh           # rebuild após editar os patches
```

**IMPORTANTE (cache):** depois de `build_ptbr.sh`, o browser pode servir o **bundle velho**. Teste em
**janela anônima**, com **Cmd+Shift+R**, ou abrindo `…/course/?cb=1`. Sintoma clássico de cache velho:
"minha mudança não apareceu / parece bugada".

---

## 8. Verificação registrada (2026-06-25/26)

- Build OK; **10/10 unittest** verdes.
- Playwright (bundle fresco): Modo Foco liga/desliga + Esc; `write_code` roda e passa (XP reativo, card
  ✓); **loop infinito para em ~0.9s** com mensagem; streak "🔥 1"; "Conquistas 2/17" com raridade.
- Conteúdo: 40/40 `write_code` com solução válida; 7/7 `write_test` com mutantes 100% matáveis.

---

## 9. Dívidas / próximos passos

- `Worker.js`/`TaskClient.js` são cópias completas nos patches → podem divergir se o futurecoder atualizar.
- `interrupt`/`input()` do Pyodide dependem do service worker (desligado) — não use; o loop-guard cobre o caso crítico.
- Expandir conteúdo (mais exercícios por capítulo) via `agy` 0-quota, mantendo o schema.
- QA humano da prosa PT-BR dos enunciados (foram gerados por agente).
